// Neural-Chromium Content Script
// Injected into every page for enhanced control

console.log('[Neural-Chromium] Content script loaded on:', window.location.href);

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('[Content] Received message:', message);

    // Handle any page-specific logic here
    // Most actions are handled via chrome.scripting.executeScript in background.js

    sendResponse({ received: true });
    return true; // Keep channel open for async response
});

// Helper: Highlight element (for debugging)
function highlightElement(element) {
    if (!element) return;
    const original = element.style.outline;
    element.style.outline = '3px solid #00ff00';
    setTimeout(() => {
        element.style.outline = original;
    }, 1000);
}

// Expose helper to window for debugging
window.neuralChromium = {
    highlightElement,
    version: '1.0.0'
};
