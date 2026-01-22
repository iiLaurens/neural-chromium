# Chrome DevTools Protocol (CDP) Implementation Plan

## Overview
Replace Windows SendInput with Chrome DevTools Protocol for reliable browser control.

## Why CDP?
- **No focus issues** - Commands sent directly to Chrome via WebSocket
- **Professional grade** - Used by Puppeteer, Playwright, Selenium 4+
- **Rich API** - Click, type, navigate, execute JavaScript, capture screenshots
- **Already available** - Chrome has CDP built-in, just need to enable it

## Implementation Steps

### Phase 1: Enable CDP in Chrome
Modify `START_NEURAL_CHROME.bat` to launch Chrome with `--remote-debugging-port=9222`

### Phase 2: Add CDP Client to Python
Install library and create `CDPController` class with methods:
- `click(x, y)` - Using `Input.dispatchMouseEvent`
- `type_text(text)` - Using `Input.insertText`
- `press_key(key)` - Using `Input.dispatchKeyEvent`
- `navigate(url)` - Using `Page.navigate`

### Phase 3: Replace InputManager
Update `execute_command` to use `CDPController` instead of `InputManager`

## Timeline
Total: ~30 minutes to get basic CDP working
