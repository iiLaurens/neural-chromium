@echo off
echo Starting Neural Chromium...
set CHROME_LOG_FILE=C:\tmp\neural_chrome_profile\chrome_debug.log
"out\AgentDebug\chrome.exe" --enable-logging --v=1 --no-sandbox --user-data-dir=C:\tmp\neural_chrome_profile --remote-debugging-port=9222 http://google.com
echo Chrome Launched. Logs FORCED to %CHROME_LOG_FILE%
