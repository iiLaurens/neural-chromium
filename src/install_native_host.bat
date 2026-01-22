@echo off
REM Install Native Messaging Host for Neural-Chromium Extension
REM Run this script AFTER loading the extension and getting the Extension ID

echo ========================================
echo  Native Messaging Host Installer
echo ========================================
echo.

REM Check if Extension ID is provided
if "%1"=="" (
    echo ERROR: Extension ID not provided!
    echo.
    echo Usage: install_native_host.bat EXTENSION_ID
    echo.
    echo Steps:
    echo 1. Load the extension in Chrome (chrome://extensions/)
    echo 2. Copy the Extension ID (looks like: abcdefghijklmnopqrstuvwxyz123456)
    echo 3. Run: install_native_host.bat YOUR_EXTENSION_ID
    echo.
    pause
    exit /b 1
)

set EXTENSION_ID=%1
echo Extension ID: %EXTENSION_ID%
echo.

REM Create the manifest with the Extension ID
echo Creating native host manifest...
(
echo {
echo   "name": "com.neural_chromium.browser_control",
echo   "description": "Neural-Chromium Browser Control Native Host",
echo   "path": "C:\\operation-greenfield\\neural-chromium-overlay\\src\\native_host.bat",
echo   "type": "stdio",
echo   "allowed_origins": [
echo     "chrome-extension://%EXTENSION_ID%/"
echo   ]
echo }
) > "%TEMP%\com.neural_chromium.browser_control.json"

REM Create the registry entry directory
set REG_DIR=%LOCALAPPDATA%\Google\Chrome\NativeMessagingHosts\com.neural_chromium.browser_control
echo Creating registry directory: %REG_DIR%
if not exist "%REG_DIR%" mkdir "%REG_DIR%"

REM Copy the manifest
echo Copying manifest to: %REG_DIR%\com.neural_chromium.browser_control.json
copy "%TEMP%\com.neural_chromium.browser_control.json" "%REG_DIR%\com.neural_chromium.browser_control.json"

REM Add the registry key (Required for Windows)
echo Adding registry key...
reg add "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.neural_chromium.browser_control" /ve /t REG_SZ /d "%REG_DIR%\com.neural_chromium.browser_control.json" /f

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. REALLY Restart Chrome completely (Close all windows, check taskbar)
echo 2. Reload the extension (chrome://extensions/)
echo 3. Check the service worker console - should see "Connected to native host"
echo.
echo Troubleshooting:
echo - Check logs: C:\tmp\native_host.log
echo - Verify manifest: %REG_DIR%\com.neural_chromium.browser_control.json
echo - Verify registry: HKCU\Software\Google\Chrome\NativeMessagingHosts\com.neural_chromium.browser_control
echo.
pause
