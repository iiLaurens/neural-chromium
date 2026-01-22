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
            if (chrome.runtime.lastError) {
                console.error('[Extension] Disconnect error:', chrome.runtime.lastError.message);
            }
            nativePort = null;
            // Retry connection after 2 seconds
            setTimeout(connectNative, 2000);
        });

        console.log('[Extension] Connected to native host');
    } catch (error) {
        console.error('[Extension] Failed to connect to native host:', error);
        // Retry after 2 seconds
        setTimeout(connectNative, 2000);
    }
}

// Handle commands from Python agent
async function handleCommand(message) {
    const { id, action, params } = message;
    let result = { id, success: false };

    try {
        // Get active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab) {
            result.error = 'No active tab';
            sendResponse(result);
            return;
        }

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

            case 'ping':
                // Send pong to keep connection alive bi-directionally
                result = { pong: true };
                break;

            default:
                // Ignore 'connected' message or other status messages
                if (message.status === 'connected') {
                    return; // Don't send response
                }
                result.error = `Unknown action: ${action}`;
        }

        result.id = id;
        result.success = !result.error;

    } catch (error) {
        result.error = error.message;
    }

    sendResponse(result);
}

function sendResponse(result) {
    if (nativePort) {
        nativePort.postMessage(result);
    }
}

// Execute click at coordinates
async function executeClick(tabId, params) {
    const { x, y } = params;

    try {
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
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Execute typing
async function executeType(tabId, params) {
    const { text } = params;

    try {
        const result = await chrome.scripting.executeScript({
            target: { tabId },
            func: (text) => {
                let el = document.activeElement;

                // If nothing focused, find first visible input
                if (!el || (el.tagName !== 'INPUT' && el.tagName !== 'TEXTAREA' && !el.isContentEditable)) {
                    el = document.querySelector('input[type="text"]:not([style*="display: none"])') ||
                        document.querySelector('input[type="search"]') ||
                        document.querySelector('textarea') ||
                        document.querySelector('[contenteditable="true"]') ||
                        document.querySelector('input:not([type="hidden"])');

                    if (el) {
                        el.focus();
                        // Wait a bit for focus to take effect
                        setTimeout(() => { }, 50);
                    }
                }

                if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA')) {
                    el.value = text;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    return { success: true, element: el.tagName, value: el.value };
                } else if (el && el.isContentEditable) {
                    el.textContent = text;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    return { success: true, element: 'contenteditable' };
                }

                return { success: false, error: 'No input element found', activeElement: el ? el.tagName : 'none' };
            },
            args: [text]
        });

        return result[0].result;
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Execute key press
async function executePressKey(tabId, params) {
    const { key } = params;

    try {
        const result = await chrome.scripting.executeScript({
            target: { tabId },
            func: (key) => {
                const el = document.activeElement || document.body;

                const keydownEvent = new KeyboardEvent('keydown', { key, bubbles: true, cancelable: true });
                const keypressEvent = new KeyboardEvent('keypress', { key, bubbles: true, cancelable: true });
                const keyupEvent = new KeyboardEvent('keyup', { key, bubbles: true, cancelable: true });

                el.dispatchEvent(keydownEvent);
                el.dispatchEvent(keypressEvent);
                el.dispatchEvent(keyupEvent);

                return { success: true };
            },
            args: [key]
        });

        return result[0].result;
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Navigate to URL
async function executeNavigate(tabId, params) {
    const { url } = params;

    try {
        await chrome.tabs.update(tabId, { url });
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Execute arbitrary JavaScript
async function executeJS(tabId, params) {
    const { code } = params;

    try {
        const result = await chrome.scripting.executeScript({
            target: { tabId },
            func: new Function(code)
        });

        return { success: true, result: result[0].result };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Get simplified DOM
async function getDOM(tabId) {
    try {
        const result = await chrome.scripting.executeScript({
            target: { tabId },
            func: () => {
                return {
                    title: document.title,
                    url: window.location.href,
                    inputs: Array.from(document.querySelectorAll('input, textarea')).map(el => ({
                        type: el.type || 'textarea',
                        placeholder: el.placeholder,
                        value: el.value,
                        visible: el.offsetParent !== null
                    }))
                };
            }
        });

        return { success: true, dom: result[0].result };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Initialize on extension load
chrome.runtime.onInstalled.addListener(() => {
    console.log('[Extension] Neural-Chromium Browser Control installed');
    connectNative();
});

// Connect on startup
connectNative();
