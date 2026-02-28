@echo off
title Sypher STT
cd /d "%~dp0"

:: Find Python: py launcher > user-installed Python 3.13/3.12/3.11 > PATH python
set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py -3"
if not defined PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PYTHON set "PYTHON=python"

%PYTHON% -m sypher_stt
pause
