# Neural-Chromium Browser Control Extension

## Installation

1. **Copy the icon**:
   - Copy the generated icon to `icons/icon16.png`, `icons/icon48.png`, and `icons/icon128.png`
   - Or use any placeholder PNG files for now

2. **Load the extension**:
   - Open Chrome
   - Go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select this `extension/` folder

3. **Get the Extension ID**:
   - After loading, you'll see an ID like: `abcdefghijklmnopqrstuvwxyz123456`
   - Copy this ID

4. **Configure Native Messaging**:
   - See `../extension_spec.md` for Native Messaging setup
   - You'll need to create the native host configuration

## Testing

Once installed, the extension will:
- Show in the extensions toolbar
- Attempt to connect to the Python native host
- Log connection status in the extension's service worker console

To view logs:
- Go to `chrome://extensions/`
- Click "service worker" under the extension
- Check console for connection messages

## Features

- **Click**: Click at specific coordinates
- **Type**: Type text into focused or first available input
- **Press Key**: Press special keys (Enter, Tab, etc.)
- **Navigate**: Navigate to URLs
- **Execute JS**: Run arbitrary JavaScript
- **Get DOM**: Get simplified DOM structure

## Status

✅ Extension files created
⏳ Native Messaging setup pending
⏳ Python integration pending
