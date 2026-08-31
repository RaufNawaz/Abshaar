@echo off
REM Double-clickable launcher: bypasses the PowerShell execution policy for
REM this one script, which locked-down lab machines usually need.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_ALL.ps1" %*
pause
