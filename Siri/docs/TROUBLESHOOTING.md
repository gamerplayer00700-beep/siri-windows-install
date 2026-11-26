# Siri troubleshooting

Start with **tray icon → System Check**. It reports the default microphone, speech/TTS packages and models, optional
language-model service status, global hotkeys, and wake-phrase startup errors without recording audio.

## Siri is blocked by Windows and never starts

If double-clicking `Siri.exe` does nothing at all - no window, no tray icon, no
error - Windows is blocking it before it runs. That is Smart App Control, and it
is not a Siri fault.

Check it:

1. Open **Event Viewer -> Windows Logs -> Application and Services Logs -> Microsoft -> Windows -> CodeIntegrity -> Operational**.
2. Look for event **3033** or **3077** naming `Siri.exe`.

Smart App Control accepts the program when the signing certificate is in the
**Trusted Root Certification Authorities** store of the machine. Two things
make it refuse the program even then:

- **The certificate is also in "Trusted Publishers".** A certificate in that
  store is expected to chain to a real certificate authority, so a self-signed
  one fails the check and the app is refused with *"did not meet the
  Enterprise signing level requirements"*. Open **certmgr.msc** and check
  **Trusted Publishers**: the Siri certificate must not be there. This is the
  most common cause and it is easy to miss, because the certificate really is
  trusted in the Trusted Root store.
- **Windows cached its verdict for the exact bytes of the file.** A rebuilt or
  re-signed copy can be refused even though nothing else changed. `Start-Siri.cmd`
  gives every attempt its own copy of the program to work around that.

Also sign every `.exe` in the folder, including `runtime\llama\llama-server.exe`,
which ships unsigned - otherwise the UI starts and the local model then fails to
load.

For a build that is accepted on every PC with no certificate to import at all,
sign the package with a certificate from a real certificate authority (see
**INSTALL-ON-ANOTHER-PC.md**, route 3).


## Siri appears to do nothing

- Look for the three-button Command/Dictate/Write dock and the Siri tray icon.
- Launching Siri twice does not create two microphone clients; the second launch asks the existing instance to show.
- If no tray icon appears, inspect `%LOCALAPPDATA%\Siri\logs\client.log` and the `logs\crashes` directory.
- Do not start another engine manually on port 7860 while the packaged app is running.

## It listens but no text appears

- Confirm the intended text field had the caret before starting Dictate or Write.
- Siri fails closed if the captured window closes or cannot be restored; it will not paste into whichever app happens
  to be foreground.
- In Windows Settings, allow desktop applications to use the microphone and choose a working default input.
- Or choose a specific recording device under **Settings → Microphone**; all Siri capture modes use that selection
  after restart.
- Test Dictate in Notepad. If Notepad works but one app does not, record the app/version and whether it uses an embedded
  browser, elevated window, remote desktop, or secure/password field.

## Commands split at a pause or background speech triggers a turn

- Use a normal sentence and let the final 2.5-second endpoint complete.
- Stop the active session from the pill if a TV or another speaker is being heard.
- Wake sessions have absolute duration ceilings; ambient sound cannot keep them open indefinitely.
- Include the complete search object: “open YouTube and search for Care Bears,” not “search for…” followed much later
  by an unrelated phrase.

## Command or Dictate hotkeys do not work

- Open **Settings** and check the configured keys for conflicts with another app.
- The floating buttons remain available if global hotkey registration fails.
- Settings changes require restarting Siri.

## Write mode fails

- Write uses the AI model bundled with the installed beta. Open **Settings → AI model** to check its status. If a
  draft does not appear, make sure the target field is still open and focused, then try a shorter request. Target
  ownership changes intentionally stop output.

## Browser or Gmail page does not load correctly

- Browser navigation still depends on the browser, DNS, internet connection, login state, extensions, and the target
  website. Reloading can recover a service-worker or transient page failure.
- Siri drafts email but never sends it automatically.

## Safe diagnostic collection

- Reproduce once, then copy the relevant local log timestamps. Do not post the entire database or `.env`.
- Include the version and build identifier shown under **tray icon → About Siri**.
- API keys belong in the local configuration and should be removed from screenshots.
- Crash reports redact common secret environment values and are never uploaded automatically, but review any file
  before sharing it because exception text can contain application-specific context.
