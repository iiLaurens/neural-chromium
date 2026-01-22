# Browser Control via MCP - Technical Specification

## Problem Statement
Current approach using Windows `SendInput` fails due to focus restrictions. We need a reliable way for `nexus_agent.py` to control the browser.

## Solution: MCP Server in Chrome Extension

### Architecture
```
┌──────────────────┐         MCP/stdio        ┌─────────────────────┐
│  nexus_agent.py  │ ◄────────────────────────►│  Chrome Extension   │
│  (MCP Client)    │    JSON-RPC over stdio   │  (MCP Server)       │
└──────────────────┘                           └─────────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────────┐
                                                │   Browser DOM/APIs  │
                                                │   - Click elements  │
                                                │   - Type text       │
                                                │   - Navigate        │
                                                │   - Execute JS      │
                                                └─────────────────────┘
```

## MCP Server Capabilities

### Tools (Actions the agent can request)

#### 1. `browser_click`
```json
{
  "name": "browser_click",
  "description": "Click at specific coordinates or on a CSS selector",
  "inputSchema": {
    "type": "object",
    "properties": {
      "x": {"type": "number", "description": "X coordinate (optional if selector provided)"},
      "y": {"type": "number", "description": "Y coordinate (optional if selector provided)"},
      "selector": {"type": "string", "description": "CSS selector (optional if x,y provided)"}
    }
  }
}
```

#### 2. `browser_type`
```json
{
  "name": "browser_type",
  "description": "Type text into focused element or selector",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {"type": "string", "description": "Text to type"},
      "selector": {"type": "string", "description": "CSS selector to focus first (optional)"}
    },
    "required": ["text"]
  }
}
```

#### 3. `browser_press_key`
```json
{
  "name": "browser_press_key",
  "description": "Press a special key (Enter, Tab, Escape, etc.)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "key": {"type": "string", "enum": ["Enter", "Tab", "Escape", "Backspace", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]}
    },
    "required": ["key"]
  }
}
```

#### 4. `browser_navigate`
```json
{
  "name": "browser_navigate",
  "description": "Navigate to a URL",
  "inputSchema": {
    "type": "object",
    "properties": {
      "url": {"type": "string", "description": "URL to navigate to"}
    },
    "required": ["url"]
  }
}
```

#### 5. `browser_execute_js`
```json
{
  "name": "browser_execute_js",
  "description": "Execute JavaScript in page context",
  "inputSchema": {
    "type": "object",
    "properties": {
      "code": {"type": "string", "description": "JavaScript code to execute"}
    },
    "required": ["code"]
  }
}
```

#### 6. `browser_screenshot`
```json
{
  "name": "browser_screenshot",
  "description": "Capture screenshot of current tab",
  "inputSchema": {
    "type": "object",
    "properties": {
      "format": {"type": "string", "enum": ["png", "jpeg"], "default": "png"}
    }
  }
}
```

### Resources (Data the agent can read)

#### 1. `dom://current-page`
```json
{
  "uri": "dom://current-page",
  "name": "Current Page DOM",
  "description": "Simplified DOM tree of the active tab",
  "mimeType": "application/json"
}
```

#### 2. `tabs://list`
```json
{
  "uri": "tabs://list",
  "name": "Open Tabs",
  "description": "List of all open tabs with titles and URLs",
  "mimeType": "application/json"
}
```

## Implementation Plan

### Step 1: Create Chrome Extension (30 min)
**Location**: `c:\operation-greenfield\neural-chromium-overlay\extension\`

**Files**:
- `manifest.json` - Extension configuration
- `background.js` - MCP server implementation (stdio communication via Native Messaging)
- `content.js` - Injected into pages for DOM access
- `native-host.json` - Native messaging host configuration

**Key Code**:
```javascript
// background.js - MCP Server
class BrowserMCPServer {
  constructor() {
    this.setupStdioTransport();
  }
  
  setupStdioTransport() {
    // Chrome extensions can use Native Messaging for stdio
    chrome.runtime.connectNative('com.neural_chromium.browser_mcp');
  }
  
  async handleToolCall(name, args) {
    switch(name) {
      case 'browser_click':
        return this.handleClick(args);
      case 'browser_type':
        return this.handleType(args);
      // ... other tools
    }
  }
  
  async handleClick(args) {
    const tab = await this.getActiveTab();
    if (args.selector) {
      // Click via selector
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (sel) => document.querySelector(sel).click(),
        args: [args.selector]
      });
    } else {
      // Click at coordinates
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (x, y) => {
          const el = document.elementFromPoint(x, y);
          if (el) el.click();
        },
        args: [args.x, args.y]
      });
    }
    return { success: true };
  }
}
```

### Step 2: Update nexus_agent.py (20 min)
Add MCP client to communicate with extension:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class NexusAgent:
    async def init_browser_mcp(self):
        # Start extension as MCP server via Native Messaging
        server_params = StdioServerParameters(
            command="chrome",
            args=["--load-extension=./extension"],
            env=None
        )
        
        self.browser_session = await stdio_client(server_params)
        await self.browser_session.__aenter__()
        
        # List available tools
        tools = await self.browser_session.list_tools()
        log(f"Browser MCP tools: {[t.name for t in tools]}")
    
    async def browser_click(self, x, y):
        result = await self.browser_session.call_tool(
            "browser_click",
            arguments={"x": x, "y": y}
        )
        return result
    
    async def browser_type(self, text):
        result = await self.browser_session.call_tool(
            "browser_type",
            arguments={"text": text}
        )
        return result
```

### Step 3: Update execute_command (10 min)
Replace `InputManager` calls with MCP tool calls:

```python
async def execute_command(self, user_request):
    # ... LLM generates plan ...
    
    if action == "click":
        await self.browser_click(x, y)
    elif action == "type":
        await self.browser_type(text)
    elif action == "navigate":
        await self.browser_session.call_tool("browser_navigate", {"url": url})
```

## Benefits
- ✅ No focus issues - extension runs inside Chrome
- ✅ MCP standard - follows established protocol
- ✅ Rich capabilities - can access DOM, execute JS
- ✅ Future-proof - can add more tools easily
- ✅ Aligns with Phase 4 goals (MCP compliance)

## Alternative: CDP vs MCP
We could use CDP directly, but MCP provides:
- Standardized protocol (better for multi-agent systems)
- Tool/Resource abstraction (cleaner API)
- Aligns with project roadmap (Phase 4)
- Can expose browser as MCP server to other agents

## Timeline
- Extension creation: 30 min
- Python MCP client: 20 min  
- Integration: 10 min
- **Total: ~1 hour**

## Next Steps
1. Create extension directory structure
2. Implement basic MCP server in background.js
3. Set up Native Messaging host
4. Add MCP client to nexus_agent.py
5. Test browser_click and browser_type tools
