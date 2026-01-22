@echo off
REM Native Messaging Host Launcher for Neural-Chromium
REM This script is called by Chrome to start the Python native host

REM Create log directory if it doesn't exist
if not exist "C:\tmp" mkdir "C:\tmp"

REM Log to a file for debugging (Unique file to avoid locking)
set LOGFILE=C:\tmp\native_host_%RANDOM%.log
echo [%date% %time%] Native host starting >> %LOGFILE%

REM Run the Python native host with full path
"C:\Users\senti\AppData\Local\Python\pythoncore-3.14-64\python.exe" "C:\operation-greenfield\neural-chromium-overlay\src\native_host.py" 2>> %LOGFILE%
