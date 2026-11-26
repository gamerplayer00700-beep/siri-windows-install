@echo off
setlocal
set "SIRI_PORT=7860"
set "SIRI_P0RT=7862"
set "SIRI_MODEL_ENGINE_PORT=7860"
set "SIRI_MODEL_PROXY_PORT=7862"

start "Siri model service" /D "%~dp0" "%~dp0model-proxy-runtime\pythonw.exe" -B "%~dp0siri_model_proxy.py"
start "Siri" /D "%~dp0" "%~dp0Siri.exe"
