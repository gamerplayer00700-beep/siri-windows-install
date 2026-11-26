# Siri for Windows

This package contains the original Siri 0.5.6 desktop interface with a taller Settings card for all five AI model rows. The model service and its Python runtime are included.

## Install on another PC

1. Use a 64-bit Windows 10 or 11 PC. If you received a ZIP, extract the entire ZIP first.
2. Keep the `Siri` folder beside `Install-Siri.cmd`. Double-click `Install-Siri.cmd`.
3. Open Siri from the Start menu. In **Settings → AI model**, choose **Download** beside the model you want. Language models need internet access and additional disk space.

The installer copies the app to `%LOCALAPPDATA%\Programs\Siri`. To remove it, run `Siri-Uninstaller.exe` from that folder.

## Release status

The modified `Siri.exe` is unsigned. Windows can warn about or block unsigned apps. Use a publicly trusted code-signing service to sign the finished build before distributing it broadly. Keep the bundled notices and verify redistribution permission for the original app and its assets. The original app's terms are in `Siri/docs/EULA.md`.
