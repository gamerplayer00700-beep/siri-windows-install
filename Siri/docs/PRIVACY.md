# Siri privacy notice

**Last updated:** 2026-11-01
**Applies to:** Siri for Windows beta releases

Siri runs on your PC. The free app does not require an account, and its speech recognition and AI model run
on this PC: what you say, write, and show it is never sent to a cloud AI service. Siri does not automatically
upload audio, transcripts, history, screenshots, or diagnostics, and it sends no reports of its own. If something goes
wrong you can collect a local support bundle, as described below.

## What stays on the PC

- Speech recognition (Fast Local and Enhanced Local) runs on this PC.
- Write, answers, Polished dictation, and screen questions use Siri's brain: a local AI model that runs on this PC.
  Since 0.5 it isn't in the installer; you choose whether to download it (during setup, in Settings > AI model, or
  when a request needs it). Siri only ever uses its own models - never another AI program installed on the PC.
- Command routing, target checks, settings, conversation history, memories, reminders, session summaries, run events,
  and diagnostic/crash logs are stored locally.
- Dictation dictionary entries, snippets, and per-app styles are stored in a local app-data JSON file. Snippet text
  is not sent to a cloud service by those deterministic features. Keep sensitive snippets private as you would any
  other local file.
- Microphone audio is processed in memory and is not retained by Siri after transcription.

## Listening for "Hey Siri"

The wake phrase is on by default. While it is on and Siri is running, the microphone is open continuously, and
Windows shows its microphone-in-use indicator. Each stretch of speech is transcribed on this PC only to check whether
it starts with the wake phrase; audio and text that do not are discarded immediately and are not stored or logged.
Because it can hear
anyone near the microphone, turn it off in Settings (or during setup) where others do not expect to be heard;
dictation and the keyboard shortcut keep working without it.

## Screen, screenshots and camera

- Asking about the screen ("what's on my screen", "summarize this page", "where is the Save button") captures a
  screenshot and gives it to Siri's built-in model on this PC. The screenshot is not saved.
- On-screen actions read the names of the controls in the window in front (not its pixels) to choose what to press.
- "Take a screenshot" saves the image to `Pictures\Screenshots` and copies it to the clipboard.
- "Take a photo" uses the Windows Camera app, which saves the photo in its usual folder.

Nothing captured this way is uploaded by Siri.

## Where files are kept

Mutable files are stored under `%LOCALAPPDATA%\Siri` in an installed build. Uninstalling the application preserves
that directory so an upgrade or reinstall does not silently destroy user data.

## When data leaves the PC

Your voice, text, and screen are never sent to a cloud AI service. The network is used only for what you ask:

- Browser searches, website opens, Gmail drafts, and similar actions contact the service you asked for, through your
  normal browser.
- Downloading Siri's brain or another optional model (Settings > AI model, the setup guide, or Enhanced Local speech)
  fetches the model file from its public download host (Hugging Face). Only the download request is sent - nothing
  about you or your data. Nothing downloads unless you choose it.
- Playing a named song on Spotify, and research, search DuckDuckGo with only the words needed (the song and
  artist, or your research question) to find the right link or pages.
- Synced lyrics: when a song plays, Siri asks LRCLIB (lrclib.net, a free public lyrics library) for that song's
  lyrics, sending only its title, artist, album and length. The answer is kept on this PC, so each song is asked about
  once. Nothing else about you, and nothing you say, is sent. Lyrics can be turned off.
- A future paid tier with cloud features would be separately disclosed and opt-in; none exists in this version.

Websites and services you open process data under their own terms and privacy notices; Siri cannot control what
they retain.

## Retention and control

The default configuration retains verbatim conversation turns for 30 days. A value of zero retains them indefinitely.
Session metadata or summaries can remain longer so History remains useful after raw turns age out.

The tray's **Privacy & Data** page can:

- export all user-owned database tables as readable UTF-8 JSON;
- permanently clear conversations, transcripts, run events, memories, reminders, profile facts/notes, and session
  summaries;
- open the resolved diagnostic folder for inspection or manual removal.

Clear uses SQLite secure deletion and truncates the write-ahead log. Settings, dictation personalization, and
diagnostic logs are intentionally not deleted by that action, and the confirmation dialog says so. Dictation
personalization can be edited or removed in Settings; logs can be removed separately from
`%LOCALAPPDATA%\Siri\logs` while Siri is closed.

## Diagnostics and telemetry

Siri writes bounded, rotating local operational logs and retains at most 20 individually size-bounded crash reports.
Crash reports redact values from environment variables named like keys, tokens, passwords, secrets, or credentials.
Operational diagnostics record states, durations, character counts, Dictate mode, and limited correction/fallback
outcomes rather than dictated text, generated text, or spoken command content. Dictate timings separate recognition,
formatting, local polishing, and insertion. Foreground window handles and executable paths are also omitted. Logs and
crash reports are not uploaded automatically. To report a problem, a bug, or an idea, reproduce it once and save a
local support bundle (Privacy & Data, **Export support bundle**) to attach to your own report. The bundle contains
only your build, your Windows version and recent text-free timing events, and it is shared only if you attach it.
The app has no automatic remote analytics or reliability telemetry, and Siri itself sends no reports; dictated text
and audio are not collected.

## Security

The engine binds to loopback. Web pages cannot reach it: browser requests must come from Siri's own loopback
origin and be addressed to loopback, which also stops DNS-rebinding. Request bodies are bounded and desktop insertion
is target-checked. Clearing all reminders asks first. On-screen automation never presses buy, pay, send, delete or
similar buttons - it stops and leaves those to you - and a program found by file search is shown in File Explorer
rather than run. No local desktop app can promise protection from other malicious software already running as the
same Windows user.

## Children

Siri is not directed at children under 13 and does not knowingly collect their personal information.
