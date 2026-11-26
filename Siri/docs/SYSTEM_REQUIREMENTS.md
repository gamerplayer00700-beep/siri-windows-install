# Siri system requirements

**Current release target:** Windows x86-64 closed beta.

## Required

- 64-bit Windows 10 or Windows 11.
- A working microphone available to Windows desktop applications.
- About 1.8 GB for the installed application (speech model and a small built-in AI model with vision included); keep at least 4 GB free for installation, staging, logs, and updates.
- A standard non-administrator user account is sufficient; Siri installs per-user under `%LOCALAPPDATA%\Programs`.
- A physical keyboard/mouse remains necessary for recovery and confirmation.

The default Fast Local speech option runs on the CPU and does not require an NVIDIA GPU. Exact minimum CPU and RAM
claims are intentionally not published until the clean-machine beta matrix is complete; 8 GB RAM is the current
practical recommendation, not a verified minimum.

## Optional

- Nothing extra for AI features: a small local model and its runtime ship with the app and run on the CPU or a
  supported GPU. Settings > AI model can download larger models; they also run on this PC. The installed beta uses
  its bundled model runtime and does not send AI requests to a cloud service.
- An NVIDIA GPU and the separately installed speech add-on when using the optional Enhanced Local recognition mode.
- Internet access for browser actions and optional model downloads.
- No service key is needed. The retired online speech setting falls back to local speech recognition.

## Not currently supported

- macOS, Linux, Windows on ARM, Windows Server, managed MSI deployment, and multi-user/RDS sessions.
- Accessibility-grade full mouse grids or complete Windows Voice Access replacement.
- Languages other than English as a marketed end-to-end experience.
