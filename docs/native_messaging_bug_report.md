# Bug Report: Chrome Native Messaging Instability

## Executive Summary
**Feature**: Robust Browser Control via Chrome Extension + Native Messaging.
**Current Status**: Unstable / Flaky.
**Symptoms**: `Extension connection failed` in Agent; "Native host has exited" in Chrome.
**Impact**: Agent cannot reliably control the browser on startup without manual intervention.

## System Architecture
1.  **Chrome Extension (Manifest V3)**:
    *   **Background Service Worker**: Handles non-persistent events.
    *   **Content Script**: Injected into pages for DOM manipulation.
    *   **Communication**: Uses `chrome.runtime.connectNative` to launch a local Python script (`native_host.py`).

2.  **Native Host (`native_host.py`)**:
    *   **Launched By**: Chrome (via `native_host.bat`).
    *   **Stdin/Stdout**: Used for IPC with Chrome (Length-prefixed JSON protocol).
    *   **Socket Server**: Listens on `127.0.0.1:9223` to accept commands from the external Python Agent.

3.  **Python Agent (`nexus_agent.py`)**:
    *   Connects to `127.0.0.1:9223` to send `click`/`type` commands.

## Root Cause Analysis

### 1. The Service Worker Lifecycle (The "Kill" Switch)
This is the primary suspect. In Manifest V3, background scripts are **Service Workers**, which are designed to be ephemeral.
*   **Behavior**: Chrome terminates the Service Worker after 30 seconds of "inactivity".
*   **Result**: When the SW dies, Chrome **kills the Native Messaging port**, which terminates the `native_host.py`.
*   **Our Fix Attempt**: Implemented a "Heartbeat" (Ping/Pong every 5s).
*   **Failure**: Even with heartbeats, Chrome can be aggressive. If the "keep-alive" logic isn't perfect (e.g., using `HighPriority` ports or specific APIs), it still dies.

### 2. The "Zombie" Host (Port Collision)
When Chrome kills the host, sometimes the `native_host.py` process doesn't die cleanly (or Windows keeps the socket `TIME_WAIT`).
*   **Scenario**:
    1.  Chrome kills Host Process A.
    2.  User runs Agent -> Chrome starts Host B.
    3.  Host B tries to bind port 9223.
    4.  **Error**: Port 9223 is still held by Host A (Zombie).
    5.  Host B crashes immediately ("Native host has exited").
    6.  Agent sees "Connection Refused".

### 3. The Startup Race Condition
*   **Scenario**:
    1.  User starts Agent.
    2.  Agent tries to connect to port 9223 immediately.
    3.  Chrome is still launching -> Extension loading -> Service Worker waking up -> Launching `native_host.bat` -> Python starting -> Binding Port.
    4.  **Result**: Agent fails to connect before the server is ready.
*   **Our Fix**: Added a 10s retry loop. This helps, but isn't a cure-all if the Host crashes (Problem #2).

## Proposed Solutions (For Research)

### Solution A: The "Manual Server" (WebSocket) - RECOMMENDED
Instead of letting Chrome launch the Python script:
1.  **Invert Control**: The User runs `native_server.py` manually (like the Agent). It stays running forever.
2.  **Chrome Connects**: The Extension uses `WebSocket` to connect *to* the Python server (e.g., `ws://localhost:9223`).
3.  **Benefit**:
    *   No Service Worker lifecycle killing the process.
    *   No Native Messaging protocol headaches (`stdin`/`stdout`).
    *   Logs go directly to the user's console, not hidden files.
    *   Persistent connection.

### Solution B: "Keep-Alive" Dedicated Tab
*   Open a dedicated "Dashboard" tab (e.g., `chrome-extension://.../dashboard.html`).
*   Tabs are persistent (unlike Service Workers).
*   Keep the Native Messaging connection open from that **Tab** instead of the Service Worker.
*   **Drawback**: Requires an open tab.

### Solution C: Robust Native Messaging (The "Gold Standard")
If we stick to Native Messaging, we need:
1.  **Reconnection Logic**: If the SW dies, the *Agent* needs to know and ask Chrome to wake up (impossible from outside).
2.  **Disconnect Handling**: The Extension must auto-reconnect immediately upon disconnection (we added this, but it spawns new processes, leading to zombies).

## Bounty Task
**Objective**: Implement **Solution A (WebSockets)**.
1.  Modify `native_host.py` to be a standalone WebSocket Server (using `websockets` lib or raw socket).
2.  Modify `background.js` to connect via `new WebSocket('ws://localhost:9223')`.
3.  Remove `native_host.bat` registration from Chrome (cleanup).
