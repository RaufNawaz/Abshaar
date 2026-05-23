@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0cxh-run.ps1" %*
exit /b %ERRORLEVEL%
