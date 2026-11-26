# Supported feature matrix

> Historical snapshot for the 0.2.0 Windows beta. The current source catalog is
> [engine/nexusd/core/capability_registry.py](../engine/nexusd/core/capability_registry.py), which is the
> programmatic source for declared platform/action availability and the short in-app capability answer.
> Catalog evidence is currently offline-only; see [HANDOFF.md](HANDOFF.md) for live and installed checks.
> This table has not yet been reconciled against the 0.2.1 release or current source, so do not use it as
> current release copy or as proof of live behavior.

This matrix describes the 0.2.0 Windows beta honestly. “Offline covered” means deterministic tests pass without touching
the desktop. “Live validation required” means the implementation exists but the packaged build still needs repeated
user-observed passes before public release.

| Area | Current capability | Evidence/status |
|---|---|---|
| Command | Open/focus registered or installed apps, browser/site search, URLs, common keys, typing, volume, camera, reminders, system stats, deterministic compound chains | Offline covered; packaged live matrix required |
| Dictate | Exact, Clean, or Polished formatting; spoken domains; explicit bullets/numbering; automatic recipe, checklist, procedure, and notes structure in Polished; bounded spoken repairs ("make that", "scratch that", "no, I mean", punctuation-delimited "actually"); personal dictionary, exact/explicit snippets, deterministic per-app Casual/Formal/Code styles; inserts into a captured, verified Windows target; Notepad and Chromium focus restoration implemented | Offline and packaged self-test covered; personalization plus 10× live runs per supported app are still required |
| Write | Short drafts stream into the captured target and stop if ownership changes. With text selected, the spoken instruction ("make this shorter", "more formal") rewrites the selection in place. Exact word counts are not guaranteed by the small bundled model | Offline covered; uses the bundled local model; selection reading needs live checks per app |
| Built-in AI model | A small local model and its runtime ship with the app (GPU via Vulkan, CPU fallback). Settings > AI model detects the PC (GPU, VRAM, RAM), estimates speed per model and downloads bigger models (2B verified; 4B/9B/27B beta). The installed beta does not use a cloud AI service | Offline covered; first-run on clean PCs required |
| On-screen actions | "click sign in", "tick the in-stock filter", "choose express shipping", "fill in my name as Sam" in the window in front - including the user's own Chrome - via Windows UI Automation; never presses buy/pay/send/delete/place-order buttons | Benchmarked on local pages in real Chrome (2B 10/10 hard tasks); live sites required |
| Screen understanding | "what's on my screen", "what does this error say" answered by the built-in model's vision, offline | Offline covered; live screens required |
| Show me where to click | "where's the export button" rings the matching control in the window in front | Offline covered (private test window) |
| Teleprompter | "start teleprompter" turns the pill into a voice-paced reading strip for the copied script; tap to pause; hidden from screen capture | Offline covered; live microphone reading required |
| Tasks, notes, habits, focus | To-do list, quick notes and search, habit streaks, focus timer, timed reminders that pop up ("remind me at 6pm..."), daily briefing ("good morning") - shown as cards in the pill | Offline covered |
| Memory and routines | "remember that...", "what do you remember", "forget..."; routines ("create a routine called start my day: open Spotify and open Gmail") | Offline covered |
| Agent mode | "take care of this: ..." plans a few voice commands and runs them one by one, live on the pill, using only safe tools | Offline covered; 2B ran 3/3 sample goals exactly |
| MCP | `Siri.exe --mcp`: Claude Code / Codex / Claude Desktop can use your tasks, notes, reminders, habits, focus and show messages on the pill (see docs/MCP.md) | Offline covered; packaged stdio check required |
| Wake phrase | Opt-in local phrase detection with bounded session/follow-up windows | Offline covered; room-noise live matrix required |
| Speech recognition | Fast local recognition is the default. Enhanced local recognition is optional. Both run on this PC; the retired online setting falls back to fast local recognition | Packaged assets audited; clean-machine performance pending |
| Now playing | Shows what any player is playing (cover, title, artist, progress) in the notch, with previous / play-pause / next; a short peek when a new song starts; "what's playing?" by voice. Nothing leaves the PC | Offline covered; live checks with Spotify, a browser tab and Media Player required |
| Full-screen apps | The resting notch steps aside while a game, full-screen video or slideshow fills its display, and returns when it ends; anything the user starts still shows. Can be switched off | Offline covered; live checks with a game, a full-screen video, a maximised window and two displays required |
| Siri's look | Outfits (headphones, shades, glasses, bow), seasonal looks that can be switched off, heart eyes when thanked, and dancing to music | Offline covered; live visual pass required |
| Move and fade the pill | Drag the pill anywhere on a screen; it stays there (remembered per monitor, kept on screen, put back if a monitor goes away). Settings > General sets how opaque it is (30 to 100 percent, shown live) and moves it back to the top centre | Offline covered; live dragging on real monitors, mixed scaling and docking pending |
| Recorded voice | Short spoken lines in one recorded British voice: cues instead of chimes, times, dates, timers, greetings, a few set phrases, and a Sir or Ma'am choice. Nothing is generated and nothing leaves the PC; a reply without a recording stays on the pill | Offline covered; listening, loudness and wake-cue echo checks pending |
| Reporting a problem | Locally only: a support bundle (build, Windows version, text-free timings) can be saved from Privacy & Data to attach to your own report. There is no in-app reporting channel and the app sends no reports itself | Offline covered; the app stays silent on the network |
| History | Local conversations and session summaries with configured raw-turn retention | Implemented and offline covered |
| Privacy controls | JSON export; secure clear of history, memory, reminders, profiles, events, and sessions | Implemented and offline covered |
| Settings | Microphone, dictation style and local personalization, trigger/hotkeys, silence, wake phrase, idle dock, character/eye/notch colours, STT backend, history retention | Look and personalization apply on save; other settings require restart; packaged visual acceptance pending |
| System Check | Microphone, local speech and AI, hotkey, and wake diagnostics | Implemented; packaged visual pass required |
| Updates | No self-update and no "check for updates" action; a new build is installed by replacing the folder | Not applicable to this build |
| Installer | Per-user Windows NSIS installer with Start Menu and optional desktop shortcuts; shows the agreement before setup and offers to remove saved data when uninstalling | The latest candidate is unsigned; clean-user install and visible agreement-page checks remain pending |

## Explicit limitations

- In the installed beta, Polished dictation and Write use the bundled local AI model. They have a finite latency
  ceiling and safely fall back to the deterministic Clean result if the model is unavailable, times out, returns
  invalid output, expands unexpectedly, or drops a protected URL/email/path/code/number value. The current source
  lets Polished correct only a small number of close, one-word recognition slips; it cannot guarantee every word
  is right. Clean stays deterministic and does not infer misheard words. This correction change is source-only until
  a new installer is built and live-tested.
- Dictionary corrections, snippets, and per-app styles use no AI or cloud. Snippets expand only when their trigger is
  said alone or after “insert”/“type”; per-app styles are deterministic, not general rewriting.
- Spoken repairs affect only the current utterance and have deliberately narrow markers. Bare “actually” without
  punctuation is left as spoken to avoid deleting ordinary prose; learning from a user's later edits is not built.
- Command mode is a deterministic supported-action system, not arbitrary visual-agent control of every application.
- Siri does not yet provide meeting/media transcription, mobile clients, cross-device sync, team administration, or an
  account/billing service.
- Harmless supported actions run without confirmation. Destructive actions require confirmation.
- An unsigned internal installer is not a public release.
