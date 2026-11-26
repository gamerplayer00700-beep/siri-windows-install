# Third-party licences

Siri ships **free of charge and closed source**. That combination is more
constraining than open source, not less: every GPL component is excluded, and
every bundled model has to be redistributable by someone who is not publishing
their source.

This is the audit behind that. The package metadata inventory was first checked
in the installed release environment on 2026-09-21; `python-multipart 0.0.32`
was rechecked after its security upgrade on 2026-09-28. Bundled model terms are
based on their model cards and the copied Silero licence text. The release uses
the Windows-provided System.Speech API for optional spoken output; Siri does
not redistribute that API or any Windows voice assets. Each installed voice
remains subject to its supplier's terms.

## Clear to ship

| Component | Licence | How verified |
|---|---|---|
| PySide6 6.10.3 | LGPLv3 | Qt Company dual-licence; see conditions below |
| FastAPI, pydantic | MIT / Apache-2.0 | package metadata |
| python-multipart 0.0.32 | Apache-2.0 | package metadata |
| uvicorn, httpx, python-dotenv | BSD-3-Clause | package metadata |
| cryptography 50.0.1 | Apache-2.0 / BSD-3-Clause | package metadata; signed update verification |
| faster-whisper 1.2.1, CTranslate2 4.7.1 | MIT | package metadata |
| tokenizers 0.23.3 (Whisper's tokenizer) | Apache-2.0 | package metadata |
| Whisper weights (`Systran/faster-whisper-small`) | MIT | Hugging Face model card |
| onnx-asr | MIT | package metadata; deps are numpy + onnxruntime only |
| huggingface-hub 1.4.1, hf-xet 1.6.0 | Apache-2.0 | package metadata; resolves the bundled Parakeet snapshot locally |
| **Parakeet TDT 0.6B v3 weights** | **CC-BY-4.0** | Hugging Face model card — **needs an attribution notice**, see below |
| Silero VAD (`silero_vad.onnx`) | MIT | Upstream licence copied to `assets/licenses/SILERO-VAD-LICENSE.txt` |
| sounddevice, mss, pycaw, comtypes, keyboard | MIT | package metadata |
| winrt-runtime, winrt-Windows.Foundation, winrt-Windows.Foundation.Collections, winrt-Windows.Media.Control, winrt-Windows.Storage.Streams 3.2.1 (pywinrt) | MIT | package metadata; reads what is playing for the notch's music card, and sends play and pause to Spotify |
| numpy, psutil | BSD-3-Clause | package metadata |
| pillow | MIT-CMU | package metadata |
| Ollama, other Qwen weights | MIT / Apache-2.0 | optional, user-installed, not redistributed |
| llama.cpp `llama-server` + ggml (release b11402, Vulkan build) | MIT | Upstream licence copied to `assets/licenses/LLAMA-CPP-LICENSE.txt`; bundled in `runtime/llama` |
| LLVM OpenMP runtime (`libomp.dll`, shipped inside the llama.cpp release) | Apache-2.0 WITH LLVM-exception | `LICENSE-LLVM-OpenMP` shipped next to it in `runtime/llama` |
| **Qwen3.5-0.8B and 2B weights** (unsloth Q4_K_M GGUF, and the 0.8B's F16 vision projector, SHA-256 pinned) | Apache-2.0 | Qwen model card; licence copied to `assets/licenses/QWEN3.5-LICENSE.txt` and shipped; since 0.5 **not bundled**: downloaded by the user in the app into the data folder (`models/`) |
| LRCLIB lyrics (lrclib.net) | service; lyrics are user-contributed | not redistributed: fetched per song at the user's PC and kept locally; credited in About |
| Coucou (github.com/Louis-CFM/coucou), code only: the island's states and timers (`app/notch_fsm.py`), its geometry (`app/island_layout.py`) and the desktop mascot rules (`app/face_out.py`), ported to Python | MIT, Copyright (c) 2026 Louis Raillé | Credited in each file's header. Its name, character (Mochi), icon, sounds and media are all rights reserved and are **not** used: Siri's face and pill are Siri's own. MIT text in `assets/licenses/COUCOU-LICENSE.txt`; credited on the About screen |
| agent-desktop (github.com/vercel-labs/agent-desktop), design only: how the Mac screen agent reads and presses controls (`engine/nexusd/platform_adapters/mac_screen.py`). No code copied. | Apache-2.0 | `licenses/AGENT-DESKTOP-LICENSE.txt` |
| browser-use (github.com/browser-use/browser-use), code ideas only: the agent prompt's shape, the page-element format, the done self-check and the loop detector, rewritten small in `engine/nexusd/tools/web_agent.py`; no package dependency | MIT, Copyright (c) 2024 Gregor Zunic | Credited in the file and on the About screen. MIT text in `assets/licenses/BROWSER-USE-LICENSE.txt` |

### PySide6 conditions

LGPLv3 allows use in closed software provided the user can replace the Qt
libraries. The Nuitka **standalone** build leaves the Qt DLLs as loose files,
which satisfies this. Do not switch to a single-file layout without a fresh
LGPL compliance review. Ship the LGPLv3 text and a notice naming Qt.

## Excluded

### eSpeak/Kokoro neural TTS stack — removed from the release

The earlier neural TTS implementation used `kokoro-onnx`, which pulled in the
`espeakng-loader` native phonemizer. The eSpeak NG project is GPL-3.0-or-later
([upstream licence](https://github.com/espeak-ng/espeak-ng)); the closed-source
distribution implications were not cleared, and missing voice data also made
the packaged TTS endpoint fail. The release no longer depends on or bundles
Kokoro, eSpeak, phonemizer packages, or their model/data files. Release
preflight rejects those retired payloads. This removes that specific blocker;
it is not a substitute for the remaining component/model licence review.

### PyAV's FFmpeg — not in the Mac app (checked 2026-11-10)

The Mac app read Whisper's audio through PyAV 19.0.2 and shipped the FFmpeg
libraries from its macOS arm64 wheel. FFmpeg itself is built LGPL
(`library_meta` reports "LGPL version 3 or later" for all seven libraries, and
the configure line has no `--enable-gpl`), but the same wheel ships
**libx264 (GPL-2.0-or-later) and libx265 (GPL-2.0-or-later)**, and `libavcodec`
links both directly (`otool -L`). That is not LGPL-only, so it can't ship in
a closed-source app. The configure line, for the record, also enables
libvpx, libdav1d, libopus, libwebp, libSvtAv1, libvmaf and libmp3lame
(BSD or LGPL); x264 and x265 are the GPL ones.

Siri only hands Whisper its own PCM WAV recordings, so FFmpeg isn't needed:
`stt_faster_whisper._decode_wav_to_float32` reads PCM WAV with Python's
`wave` module and NumPy, and uses PyAV only for other formats where PyAV is
installed. `faster-whisper` imports `av` at the top of its audio module, so
on macOS and Linux `platform_adapters/compat.py` registers a placeholder `av`
when PyAV is missing. `scripts/build_mac.sh` leaves PyAV out
(`--nofollow-import-to=av`) and stops if any `libav*`, `libsw*` or `libx26*`
library is in the app. PyAV stays in `requirements-mac.txt` only because
faster-whisper requires it for installation; it is in the source checkout,
not the app.

Windows: not checked here. If the Windows release bundles faster-whisper with
PyAV, its wheel should be checked the same way (`av._core.library_meta` and
the DLLs beside `libavcodec`).

### PyQt6 — removed

GPLv3 or a paid Riverbank licence, no third option. Ported to PySide6 in
`99f754f`, and uninstalled rather than left beside it so nothing can quietly
fall back to it.

### openWakeWord's pre-trained models — must not be bundled

From openWakeWord's own README, in the installed package metadata:

> All of the included pre-trained models are licensed under the Creative
> Commons Attribution-NonCommercial-ShareAlike 4.0 International license due
> to the inclusion of datasets with unknown or restrictive licensing as part
> of the training data.

That covers `hey_jarvis_v0.1.onnx` and every other `.onnx`/`.tflb` in
`openwakeword/resources/models/`. NonCommercial is arguable for a free product
and ShareAlike is arguable for mere aggregation, but neither argument is worth
having, and CC themselves advise against using these licences for software.

Separately, **JARVIS is Marvel/Disney IP**, so the phrase is not shippable as a
product's wake word regardless of the model licence.

openWakeWord is no longer a runtime dependency. Siri uses its own minimal
Silero ONNX wrapper and ships only the separately MIT-licensed VAD model. The
release preflight still rejects these paths in case the dependency is ever
reintroduced accidentally:

```
openwakeword/resources/models/*.onnx
openwakeword/resources/models/*.tflb
```

with one exception: **`silero_vad.onnx` is MIT** and is needed for end-of-speech
detection, which is load-bearing. Keep that one file; drop the rest.

#### Unresolved: the feature-extraction backbone

`melspectrogram.onnx` and `embedding_model.onnx` are the frozen front end that
any custom-trained wake word would sit on top of. The README describes the
backbone as Google's TFHub `speech_embedding` module under Apache-2.0, manually
re-implemented - and the stated *reason* for the NC licence (restrictive
training data) does not apply to a model openWakeWord didn't train. But the
blanket sentence above literally covers them.

Until upstream clarifies, treat both as NC and do not ship them. This is why
the replacement wake word is being built on Whisper and Silero, which are both
MIT with no ambiguity at all.

### Parakeet's attribution

CC-BY-4.0 permits commercial and closed-source use, and requires credit. The
build must carry, in the notices shipped beside the executable and wherever
third-party components are listed:

> Speech recognition uses NVIDIA Parakeet TDT 0.6B v3, licensed under CC-BY-4.0.

This is the only obligation any shipped model places on us, and it is a line of
text.

### NVIDIA cuBLAS / cuDNN — no longer needed

Measured on this machine, Parakeet on the CPU transcribes a 2-second partial in
169ms, against 204ms for Whisper turbo on a 2080 Ti and 2885ms for Whisper on
the same CPU. Faster than the GPU path it replaces, seventeen times faster than
the CPU fallback, and identical on the keyword checks.

So the question below stops being one. With `SIRI_STT_BACKEND=parakeet` the
build needs no CUDA at all: no cublas, no cudnn, ~2.5GB off the installer, no
NVIDIA SDK agreement to read, and it runs on machines with no NVIDIA GPU in
them. The GPU, when there is one, is left entirely to the language model -
which means the VRAM contention that produced "CUDA failed with error out of
memory" on the first command.

The paragraph below is kept because faster_whisper is still a supported backend
for anyone who prefers it.

### NVIDIA cuBLAS / cuDNN — do not redistribute

These are under the NVIDIA Software Development Kit licence agreement, not an
OSS licence, and clause 2.5 restricts distributing the SDK in ways that make it
subject to open-source terms. Redistributing CUDA runtime libraries with an
application is common and probably permitted, but "probably" is not a basis for
shipping, and reading it properly is a lawyer's job rather than a build step.

There is an easy way not to need the answer: **ship CPU-only by default** and
make GPU acceleration an optional component that installs the NVIDIA wheels
from PyPI **on the user's machine**. The user then acquires them directly under
NVIDIA's terms and we redistribute nothing. This also keeps the default
download far smaller, which matters more for adoption than the speed does.

## Still to do

- Raise an issue upstream asking whether the openWakeWord backbone models are
  Apache-2.0 or CC BY-NC-SA. If Apache-2.0, a trained 1MB model becomes an
  option again and is cheaper at runtime than the Whisper approach.
- The release build ships this audited component inventory as
  `THIRD-PARTY-NOTICES.md`, alongside the complete GNU LGPLv3 and GPLv3 text
  required for the dynamically linked Qt for Python libraries. Preflight and
  the compiled executable self-test verify both license files against the
  official GNU text digests before an artifact is accepted.
