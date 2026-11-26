"""
Siri Model Proxy — adds extra models to the notch / island Settings panel
==========================================================================
Sits between the Siri client (notch / island HUD) and the real Siri engine,
transparently proxying every request.  The only thing it changes is the
``/v1/models/recommend`` response: three additional downloadable models —
Qwen3.5 4B, Qwen3 8B, and Gemma4 E4B — are injected into the ``models``
list that the Settings > AI model page renders.

It also handles ``/v1/models/download`` and ``/v1/models/select`` for the
three extra models, using the same NTFS-hardlink-into-slot mechanism as
``siri_model_manager_gui.py``.

Usage
-----
    python siri_model_proxy.py          # auto-detects real engine port
    python siri_model_proxy.py 7860     # explicit real-engine port

The proxy picks a free port, writes it to ``engine.port`` so the notch
client reconnects to the proxy on next refresh, and forwards everything
else unchanged.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.request import Request, urlopen

# ── Paths ────────────────────────────────────────────────────────────────
LOCAL = Path(os.environ.get("LOCALAPPDATA", "")) / "Siri"
MODELS_DIR = LOCAL / "models"
ENGINE_PORT_FILE = LOCAL / "engine.port"
SLOT_FILE = "Qwen3.5-2B-Q4_K_M.gguf"

HF_URL = "https://huggingface.co/{repo}/resolve/{revision}/{file}"

# ── Extra model catalog (the three models to inject) ─────────────────────
EXTRA_MODELS = [
    {
        "id": "qwen3.5-4b",
        "label": "Medium",
        "model": "Qwen3.5 4B",
        "file": "Qwen3.5-4B-Q4_K_M.gguf",
        "extra_files": [],
        "repo": "Boollm/Qwen3.5-4B-GGUF",
        "revision": "main",
        "bytes": 2_783_446_752,
        "sha256": "fd68ce71f4225ebd0f33c5ddddb9dc612349e20189c213c24363ec787fd2a398",
        "params_b": 4.0,
        "speed": "fast",
        "notes": "Top pick for speed — fits in 6 GB VRAM, great balance of size and smarts.",
        "verified": False,
        "may_run_slowly": False,
        "size_name": "Medium",
    },
    {
        "id": "qwen3-8b",
        "label": "Large",
        "model": "Qwen3 8B",
        "file": "Qwen3-8B-Q4_K_M.gguf",
        "extra_files": [],
        "repo": "Qwen/Qwen3-8B-GGUF",
        "revision": "main",
        "bytes": 5_027_783_488,
        "sha256": "d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785",
        "params_b": 8.0,
        "speed": "medium",
        "notes": "Top pick for smarts — deep reasoning, uses GPU + RAM.",
        "verified": False,
        "may_run_slowly": True,
        "size_name": "Large",
    },
    {
        "id": "gemma4-e4b",
        "label": "Medium",
        "model": "Gemma4 E4B",
        "file": "gemma-4-E4B-it-Q4_K_M.gguf",
        "extra_files": [],
        "repo": "Xylolabs/gemma-4-E4B-it-GGUF",
        "revision": "main",
        "bytes": 4_977_119_680,
        "sha256": "d7f1cd193872939e7e6c546d3fab8b60fa44b5618163b4901ebfafcc4356dcd5",
        "params_b": 4.0,
        "speed": "medium",
        "notes": "Google Gemma 4 — balanced speed and quality, uses GPU + RAM.",
        "verified": False,
        "may_run_slowly": True,
        "size_name": "Medium",
    },
]

EXTRA_IDS = {m["id"] for m in EXTRA_MODELS}

# ── Active downloads (model_id -> {thread, cancel, progress}) ───────────
_downloads: dict[str, dict] = {}
_downloads_lock = threading.Lock()


# ── Helpers ──────────────────────────────────────────────────────────────
def human_size(b: int) -> str:
    if b >= 1_000_000_000:
        return f"{b / (1024 ** 3):.1f} GB"
    return f"{b / (1024 ** 2):.0f} MB"


def model_store_path(entry: dict) -> Path:
    return MODELS_DIR / entry["file"]


def is_installed(entry: dict) -> bool:
    p = model_store_path(entry)
    return p.exists() and p.stat().st_size > 1_000_000


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().lower()


def link_or_copy(src: Path, dst: Path):
    if dst.exists():
        try:
            dst.unlink()
        except PermissionError:
            _release_llama()
            dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def _release_llama():
    import subprocess
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "llama-server.exe"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=0x08000000, timeout=5,
        )
        time.sleep(0.4)
    except Exception:
        pass


def _enrich_extra(entry: dict) -> dict:
    """Build a row dict matching what /v1/models/recommend returns."""
    installed = is_installed(entry)
    return {
        "id": entry["id"],
        "label": entry["label"],
        "model": entry["model"],
        "bytes": entry["bytes"],
        "params_b": entry["params_b"],
        "notes": entry["notes"],
        "fit": "gpu+ram",
        "verified": entry.get("verified", False),
        "tokens_per_s": 0,
        "reply_seconds": 2.0 if entry["params_b"] >= 8 else 1.2,
        "speed": entry["speed"],
        "installed": installed,
        "may_run_slowly": entry.get("may_run_slowly", False),
        "download_bytes": entry["bytes"],
        "size_name": entry.get("size_name", ""),
    }


# ── Download worker ──────────────────────────────────────────────────────
def _download_worker(entry: dict):
    model_id = entry["id"]
    dest = model_store_path(entry)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = Path(str(dest) + ".part")

    with _downloads_lock:
        info = _downloads.get(model_id)
        if not info:
            return
        cancel = info["cancel"]

    try:
        existing = part.stat().st_size if part.exists() else 0
        if existing > entry["bytes"]:
            part.unlink()
            existing = 0

        url = HF_URL.format(
            repo=entry["repo"],
            revision=entry["revision"],
            file=entry["file"],
        )
        headers = {"User-Agent": "SiriModelProxy/1.0"}
        if existing > 0:
            headers["Range"] = f"bytes={existing}-"

        req = Request(url, headers=headers)
        with urlopen(req, timeout=60) as resp:
            status = getattr(resp, "status", 200)
            if status == 200 and existing > 0:
                existing = 0
            total = entry["bytes"]
            downloaded = existing
            mode = "ab" if existing > 0 and status == 206 else "wb"

            with open(part, mode) as f:
                while True:
                    if cancel.is_set():
                        with _downloads_lock:
                            _downloads.pop(model_id, None)
                        return
                    chunk = resp.read(512 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    pct = min(99, int(downloaded * 100 / total)) if total else 0
                    with _downloads_lock:
                        if model_id in _downloads:
                            _downloads[model_id]["bytes"] = downloaded
                            _downloads[model_id]["total"] = total

        # Verify
        with _downloads_lock:
            if model_id in _downloads:
                _downloads[model_id]["state"] = "verifying"

        digest = sha256_file(part)
        if digest != entry["sha256"].lower():
            part.unlink(missing_ok=True)
            with _downloads_lock:
                if model_id in _downloads:
                    _downloads[model_id]["state"] = "failed"
                    _downloads[model_id]["error"] = "Checksum mismatch"
            return

        if dest.exists():
            dest.unlink()
        part.replace(dest)

        with _downloads_lock:
            if model_id in _downloads:
                _downloads[model_id]["state"] = "done"

    except Exception as exc:
        with _downloads_lock:
            if model_id in _downloads:
                _downloads[model_id]["state"] = "failed"
                _downloads[model_id]["error"] = str(exc)


# ── The Proxy Handler ────────────────────────────────────────────────────
class ProxyHandler(BaseHTTPRequestHandler):
    real_port: int = 7860

    def log_message(self, fmt, *args):
        pass  # silence request logs

    # ---------- Routing ----------
    def do_GET(self):
        if self.path == "/v1/models/recommend":
            self._handle_recommend()
        elif self.path == "/v1/models/downloads":
            self._handle_downloads_get()
        else:
            self._proxy("GET")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""

        if self.path == "/v1/models/download":
            self._handle_download(body)
        elif self.path == "/v1/models/select":
            self._handle_select(body)
        else:
            self._proxy("POST", body)

    # ---------- /v1/models/recommend — inject extra models ----------------
    def _handle_recommend(self):
        upstream = self._fetch_upstream("GET", self.path)
        if upstream is None:
            self._json({"error": "engine unreachable"}, 502)
            return

        try:
            data = json.loads(upstream)
        except Exception:
            self._raw(upstream)
            return

        # Inject extra models into the "models" list
        models = data.get("models", [])
        existing_ids = {m["id"] for m in models if isinstance(m, dict)}

        for extra in EXTRA_MODELS:
            if extra["id"] not in existing_ids:
                models.append(_enrich_extra(extra))

        data["models"] = models

        # The original 9B entry is only a disabled placeholder.  Once the
        # three usable choices are present it makes the original fixed-size
        # card compress all rows, so keep the five working choices readable.
        data["coming_soon"] = []

        # Also update downloads status for extra models
        downloads = data.get("downloads", {})
        with _downloads_lock:
            for mid, info in _downloads.items():
                if mid in EXTRA_IDS:
                    downloads[mid] = {
                        "state": info.get("state", "downloading"),
                        "bytes": info.get("bytes", 0),
                        "total": info.get("total", 0),
                    }
        data["downloads"] = downloads

        self._json(data)

    # ---------- /v1/models/download — handle extra models -----------------
    def _handle_download(self, body: bytes):
        try:
            req = json.loads(body)
        except Exception:
            self._json({"error": "bad json"}, 400)
            return

        model_id = req.get("id", "")
        entry = next((m for m in EXTRA_MODELS if m["id"] == model_id), None)

        if entry is None:
            # Not an extra model → forward to real engine
            self._proxy("POST", body)
            return

        if is_installed(entry):
            self._json({"ok": True, "already_installed": True})
            return

        with _downloads_lock:
            if model_id in _downloads and _downloads[model_id].get("state") == "downloading":
                self._json({"ok": True, "already_downloading": True})
                return

            cancel = threading.Event()
            _downloads[model_id] = {
                "cancel": cancel,
                "state": "downloading",
                "bytes": 0,
                "total": entry["bytes"],
            }

        t = threading.Thread(target=_download_worker, args=(entry,), daemon=True)
        t.start()
        self._json({"ok": True})

    # ---------- /v1/models/downloads — merge extra download state ----------
    def _handle_downloads_get(self):
        upstream = self._fetch_upstream("GET", self.path)
        try:
            data = json.loads(upstream) if upstream else {}
        except Exception:
            data = {}

        with _downloads_lock:
            for mid, info in _downloads.items():
                if mid in EXTRA_IDS:
                    data[mid] = {
                        "state": info.get("state", "downloading"),
                        "bytes": info.get("bytes", 0),
                        "total": info.get("total", 0),
                        "done": info.get("state") == "done",
                        "failed": info.get("state") == "failed",
                        "error": info.get("error", ""),
                    }

        self._json(data)

    # ---------- /v1/models/select — handle extra models -------------------
    def _handle_select(self, body: bytes):
        try:
            req = json.loads(body)
        except Exception:
            self._json({"error": "bad json"}, 400)
            return

        model_id = req.get("id", "")
        entry = next((m for m in EXTRA_MODELS if m["id"] == model_id), None)

        if entry is None:
            # Not an extra model → forward to real engine
            self._proxy("POST", body)
            return

        if not is_installed(entry):
            self._json({"error": "model not downloaded yet"}, 400)
            return

        # Map model into Siri's GGUF slot via NTFS hardlink
        _release_llama()
        src = model_store_path(entry)
        slot_path = MODELS_DIR / SLOT_FILE
        link_or_copy(src, slot_path)

        # Update selected.json
        selected_json = MODELS_DIR / "selected.json"
        selected_json.write_text(json.dumps({"id": "qwen3.5-2b"}), encoding="utf-8")

        # Tell the real engine to load the slot
        try:
            self._fetch_upstream(
                "POST", "/v1/models/select",
                json.dumps({"id": "qwen3.5-2b"}).encode()
            )
        except Exception:
            pass

        self._json({"ok": True, "model": entry["model"]})

    # ---------- Raw proxy ------------------------------------------------
    def _proxy(self, method: str, body: bytes = b""):
        upstream = self._fetch_upstream(method, self.path, body)
        if upstream is None:
            self._json({"error": "engine unreachable"}, 502)
        else:
            self._raw(upstream)

    def _fetch_upstream(self, method: str, path: str, body: bytes = b"") -> bytes | None:
        url = f"http://127.0.0.1:{self.real_port}{path}"
        try:
            req = Request(url, data=body if body else None, method=method)
            req.add_header("Content-Type", "application/json")
            with urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception:
            return None

    # ---------- Response helpers -----------------------------------------
    def _json(self, obj, code=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _raw(self, data: bytes, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)


# ── Main ─────────────────────────────────────────────────────────────────
def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    # The original Siri engine keeps its normal port.  The matching original
    # UI copy reads SIRI_P0RT and talks to this fixed proxy port instead.
    # Keeping the two ports separate avoids a startup race and does not alter
    # any original UI code or visuals.
    real_port = int(os.environ.get("SIRI_MODEL_ENGINE_PORT", "7860"))
    proxy_port = int(os.environ.get("SIRI_MODEL_PROXY_PORT", "7862"))
    if len(sys.argv) > 1:
        real_port = int(sys.argv[1])
    if len(sys.argv) > 2:
        proxy_port = int(sys.argv[2])

    ProxyHandler.real_port = real_port
    server = HTTPServer(("127.0.0.1", proxy_port), ProxyHandler)

    print(f"Siri Model Proxy running on 127.0.0.1:{proxy_port}")
    print(f"  -> forwarding to real engine on 127.0.0.1:{real_port}")
    print("  -> 3 extra models injected: Qwen3.5 4B, Qwen3 8B, Gemma4 E4B")
    print("  -> open Settings > AI model in the notch to see them")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProxy stopped.")


if __name__ == "__main__":
    main()
