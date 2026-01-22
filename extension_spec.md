# Neural-Chromium Browser Control Extension - Technical Specification

## Overview
A Chrome extension that provides reliable browser control for the Nexus Agent via Native Messaging. This replaces the CDP approach with a more robust solution that has full DOM access.

## Architecture

```
┌─────────────────┐    Native Messaging     ┌──────────────────────┐
│  nexus_agent.py │ ◄──────────────────────►│  Extension           │
│  (Python)       │    stdin/stdout JSON    │  (background.js)     │
└─────────────────┘                         └──────────────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────────────┐
                                            │  Content Scripts     │
                                            │  (Injected into      │
                                            │   each page)         │
                                            └──────────────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────────────┐
                                            │  Page DOM            │
                                            │  - Click elements    │
                                            │  - Type text         │
                                            │  - Execute JS        │
                                            └──────────────────────┘
```

## Extension Structure

```
neural-chromium-overlay/extension/
├── manifest.json           # Extension configuration
├── background.js           # Service worker (handles Native Messaging)
├── content.js              # Content script (injected into pages)
├── native-host.json        # Native Messaging host config
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## File Specifications

### 1. manifest.json
```json
{
  "manifest_version": 3,
  "name": "Neural-Chromium Browser Control",
  "version": "1.0.0",
  "description": "Enables AI agent control of the browser",
  
  "permissions": [
    "activeTab",
    "scripting",
    "tabs",
    "nativeMessaging"
  ],
  
  "host_permissions": [
    "<all_urls>"
  ],
  
  "background": {
    "service_worker": "background.js"
  },
  
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"],
      "run_at": "document_idle",
      "all_frames": true
    }
  ],
  
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

### 2. background.js (Service Worker)
```javascript
// Neural-Chromium Browser Control Extension
// Background Service Worker - Handles Native Messaging

const NATIVE_HOST = 'com.neural_chromium.browser_control';
let nativePort = null;

// Connect to Python agent via Native Messaging
function connectNative() {
  try {
    nativePort = chrome.runtime.connectNative(NATIVE_HOST);
    
    nativePort.onMessage.addListener((message) => {
      console.log('[Extension] Received from Python:', message);
      handleCommand(message);
    });
    
    nativePort.onDisconnect.addListener(() => {
      console.log('[Extension] Native host disconnected');
      nativePort = null;
      // Retry connection after 2 seconds
      setTimeout(connectNative, 2000);
    });
    
    console.log('[Extension] Connected to native host');
  } catch (error) {
    console.error('[Extension] Failed to connect to native host:', error);
  }
}

// Handle commands from Python agent
async function handleCommand(message) {
  const { id, action, params } = message;
  let result = { id, success: false };
  
  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    switch (action) {
      case 'click':
        result = await executeClick(tab.id, params);
        break;
        
      case 'type':
        result = await executeType(tab.id, params);
        break;
        
      case 'press_key':
        result = await executePressKey(tab.id, params);
        break;
        
      case 'navigate':
        result = await executeNavigate(tab.id, params);
        break;
        
      case 'execute_js':
        result = await executeJS(tab.id, params);
        break;
        
      case 'get_dom':
        result = await getDOM(tab.id);
        break;
        
      default:
        result.error = `Unknown action: ${action}`;
    }
    
    result.id = id;
    result.success = !result.error;
    
  } catch (error) {
    result.error = error.message;
  }
  
  // Send result back to Python
  if (nativePort) {
    nativePort.postMessage(result);
  }
}

// Execute click at coordinates
async function executeClick(tabId, params) {
  const { x, y } = params;
  
  const result = await chrome.scripting.executeScript({
    target: { tabId },
    func: (x, y) => {
      const element = document.elementFromPoint(x, y);
      if (element) {
        element.click();
        return { success: true, element: element.tagName };
      }
      return { success: false, error: 'No element at coordinates' };
    },
    args: [x, y]
  });
  
  return result[0].result;
}

// Execute typing
async function executeType(tabId, params) {
  const { text } = params;
  
  const result = await chrome.scripting.executeScript({
    target: { tabId },
    func: (text) => {
      let el = document.activeElement;
      
      // If nothing focused, find first input
      if (!el || (el.tagName !== 'INPUT' && el.tagName !== 'TEXTAREA' && !el.isContentEditable)) {
        el = document.querySelector('input[type="text"], input[type="search"], textarea, [contenteditable="true"]');
        if (el) el.focus();
      }
      
      if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA')) {
        el.value = text;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        return { success: true, element: el.tagName };
      } else if (el && el.isContentEditable) {
        el.textContent = text;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        return { success: true, element: 'contenteditable' };
      }
      
      return { success: false, error: 'No input element found' };
    },
    args: [text]
  });
  
  return result[0].result;
}

// Execute key press
async function executePressKey(tabId, params) {
  const { key } = params;
  
  const result = await chrome.scripting.executeScript({
    target: { tabId },
    func: (key) => {
      const el = document.activeElement || document.body;
      
      const keydownEvent = new KeyboardEvent('keydown', { key, bubbles: true });
      const keyupEvent = new KeyboardEvent('keyup', { key, bubbles: true });
      
      el.dispatchEvent(keydownEvent);
      el.dispatchEvent(keyupEvent);
      
      return { success: true };
    },
    args: [key]
  });
  
  return result[0].result;
}

// Navigate to URL
async function executeNavigate(tabId, params) {
  const { url } = params;
  await chrome.tabs.update(tabId, { url });
  return { success: true };
}

// Execute arbitrary JavaScript
async function executeJS(tabId, params) {
  const { code } = params;
  
  const result = await chrome.scripting.executeScript({
    target: { tabId },
    func: new Function(code)
  });
  
  return { success: true, result: result[0].result };
}

// Get simplified DOM
async function getDOM(tabId) {
  const result = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      // Return simplified DOM structure
      return {
        title: document.title,
        url: window.location.href,
        inputs: Array.from(document.querySelectorAll('input, textarea')).map(el => ({
          type: el.type || 'textarea',
          placeholder: el.placeholder,
          value: el.value
        }))
      };
    }
  });
  
  return result[0].result;
}

// Initialize on extension load
chrome.runtime.onInstalled.addListener(() => {
  console.log('[Extension] Neural-Chromium Browser Control installed');
  connectNative();
});

// Connect on startup
connectNative();
```

### 3. content.js (Content Script)
```javascript
// Neural-Chromium Content Script
// Injected into every page for enhanced control

console.log('[Neural-Chromium] Content script loaded');

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[Content] Received message:', message);
  
  // Handle any page-specific logic here
  // Most actions are handled via chrome.scripting.executeScript
  
  sendResponse({ received: true });
});

// Helper: Highlight element (for debugging)
function highlightElement(element) {
  const original = element.style.outline;
  element.style.outline = '3px solid red';
  setTimeout(() => {
    element.style.outline = original;
  }, 1000);
}
```

### 4. native-host.json (Native Messaging Configuration)
```json
{
  "name": "com.neural_chromium.browser_control",
  "description": "Neural-Chromium Browser Control Native Host",
  "path": "C:\\operation-greenfield\\neural-chromium-overlay\\src\\native_host.bat",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://EXTENSION_ID_WILL_BE_GENERATED/"
  ]
}
```

### 5. native_host.bat (Native Messaging Launcher)
```batch
@echo off
REM Native Messaging Host Launcher
REM This script is called by Chrome to start the Python native host

python "C:\operation-greenfield\neural-chromium-overlay\src\native_host.py"
```

### 6. native_host.py (Python Native Messaging Host)
```python
#!/usr/bin/env python3
"""
Native Messaging Host for Neural-Chromium Extension
Handles communication between Chrome extension and nexus_agent.py
"""

import sys
import json
import struct
import threading
import queue

# Message queue for bidirectional communication
outgoing_queue = queue.Queue()
incoming_queue = queue.Queue()

def read_message():
    """Read a message from Chrome extension (stdin)"""
    # Read message length (4 bytes)
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return None
    
    message_length = struct.unpack('=I', raw_length)[0]
    
    # Read message
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message)

def send_message(message):
    """Send a message to Chrome extension (stdout)"""
    encoded_message = json.dumps(message).encode('utf-8')
    encoded_length = struct.pack('=I', len(encoded_message))
    
    sys.stdout.buffer.write(encoded_length)
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()

def message_reader():
    """Thread to read messages from extension"""
    while True:
        try:
            message = read_message()
            if message is None:
                break
            incoming_queue.put(message)
        except Exception as e:
            sys.stderr.write(f"Read error: {e}\n")
            break

def message_writer():
    """Thread to write messages to extension"""
    while True:
        try:
            message = outgoing_queue.get()
            if message is None:
                break
            send_message(message)
        except Exception as e:
            sys.stderr.write(f"Write error: {e}\n")
            break

# Start reader/writer threads
reader_thread = threading.Thread(target=message_reader, daemon=True)
writer_thread = threading.Thread(target=message_writer, daemon=True)

reader_thread.start()
writer_thread.start()

# Main loop - integrate with nexus_agent.py
# This will be imported by nexus_agent.py
def send_command(action, params):
    """Send a command to the extension"""
    message = {
        'id': id(params),  # Unique ID for tracking
        'action': action,
        'params': params
    }
    outgoing_queue.put(message)
    
    # Wait for response
    response = incoming_queue.get(timeout=5)
    return response

if __name__ == '__main__':
    # Keep alive
    reader_thread.join()
```

## Integration with nexus_agent.py

Add `ExtensionController` class:

```python
class ExtensionController:
    """Controls browser via Chrome Extension + Native Messaging"""
    def __init__(self):
        self.connected = False
        # Import native_host module
        try:
            import native_host
            self.native_host = native_host
            self.connected = True
        except ImportError:
            pass
    
    def click(self, x, y):
        if not self.connected:
            return False
        response = self.native_host.send_command('click', {'x': x, 'y': y})
        return response.get('success', False)
    
    def type_text(self, text):
        if not self.connected:
            return False
        response = self.native_host.send_command('type', {'text': text})
        return response.get('success', False)
    
    def press_key(self, key):
        if not self.connected:
            return False
        response = self.native_host.send_command('press_key', {'key': key})
        return response.get('success', False)
    
    def navigate(self, url):
        if not self.connected:
            return False
        response = self.native_host.send_command('navigate', {'url': url})
        return response.get('success', False)
```

## Installation Steps

1. **Build Extension**:
   - Create `extension/` directory
   - Add all files (manifest.json, background.js, content.js)
   - Generate icons (can use placeholder PNGs)

2. **Install Extension**:
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select `extension/` folder
   - Copy the generated Extension ID

3. **Register Native Host**:
   - Update `native-host.json` with Extension ID
   - Copy to: `C:\Users\<USER>\AppData\Local\Google\Chrome\User Data\NativeMessagingHosts\com.neural_chromium.browser_control\native-host.json`

4. **Test**:
   - Restart Chrome
   - Extension should auto-connect to Python agent
   - Test with `debug type hello world`

## Benefits Over CDP

1. ✅ **Full DOM Access** - No Shadow DOM limitations
2. ✅ **Native Chrome APIs** - More reliable than JavaScript injection
3. ✅ **Persistent Connection** - Extension stays loaded
4. ✅ **Better Error Handling** - Proper success/failure responses
5. ✅ **Future-Proof** - Can add more features easily

## Timeline

- **Extension Files**: 20 minutes
- **Native Messaging Setup**: 15 minutes
- **Python Integration**: 15 minutes
- **Testing**: 10 minutes
- **Total**: ~1 hour

## Next Steps

1. Create extension files
2. Generate placeholder icons
3. Implement native_host.py
4. Update nexus_agent.py to use ExtensionController
5. Test end-to-end
