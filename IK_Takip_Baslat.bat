@echo off
setlocal

set "LOCAL_PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
set "CODEX_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if exist "%LOCAL_PY%" (
  "%LOCAL_PY%" "%~dp0ik_takip.py"
  exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  python "%~dp0ik_takip.py"
  exit /b %ERRORLEVEL%
)

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py "%~dp0ik_takip.py"
  exit /b %ERRORLEVEL%
)

if exist "%CODEX_PY%" (
  "%CODEX_PY%" "%~dp0ik_takip.py"
  exit /b %ERRORLEVEL%
)

echo Python bulunamadi. Lutfen Python 3 kurun: https://www.python.org/downloads/
pause
