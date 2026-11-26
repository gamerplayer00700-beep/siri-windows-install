@echo off
setlocal
set "SIRI_INSTALL_DIR=%LOCALAPPDATA%\Programs\Siri"
if /i "%~1"=="--test-install" (
  if "%~2"=="" exit /b 2
  set "SIRI_INSTALL_DIR=%~2"
)

if not exist "%~dp0Siri\Siri.exe" (
  echo The Siri app folder is missing. Extract the entire package and try again.
  if /i not "%~1"=="--test-install" pause
  exit /b 1
)

echo.
echo Siri installer
echo.
if exist "%SIRI_INSTALL_DIR%\Siri.exe" (
  echo An existing Siri installation was found:
  echo %SIRI_INSTALL_DIR%
  echo Close Siri from its system tray menu before continuing.
  choice /M "Replace the app files and keep your local Siri data"
  if errorlevel 2 exit /b 1
)

robocopy "%~dp0Siri" "%SIRI_INSTALL_DIR%" /E /COPY:DAT /R:2 /W:1 /NFL /NDL /NJH /NJS
if errorlevel 8 (
  echo.
  echo Installation failed. Check that the folder is writable and try again.
  pause
  exit /b 1
)

if /i "%~1"=="--test-install" exit /b 0

powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; $d=$env:SIRI_INSTALL_DIR; $w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Programs')) 'Siri.lnk')); $s.TargetPath=Join-Path $d 'Start-Siri.cmd'; $s.WorkingDirectory=$d; $s.IconLocation=(Join-Path $d 'Siri.exe')+',0'; $s.Save()"
if errorlevel 1 echo Use Start-Siri.cmd in the installed Siri folder to launch the app.

echo.
echo Installed. Starting Siri...
start "Siri" /D "%SIRI_INSTALL_DIR%" "%SIRI_INSTALL_DIR%\Start-Siri.cmd"
endlocal
