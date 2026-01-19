# Project Neural-Chromium: Challenges & Status Report (Day 2)

## 🚨 Critical Snags Encountered

### 1. The Build System "Antibody" Response
**Issue**: Attempting to inject the Visual Cortex (`AgentSharedMemory` class) into the `components/viz` subsystem triggered persistent build failures (`manifest error`, `ninja: cannot make progress`).
**Diagnosis**:
*   Chromium's build system (`gn` + `ninja`) is extremely sensitive to modification of core `BUILD.gn` files.
*   Adding `agent_shared_memory.cc` to `components/viz/service/BUILD.gn` caused a graph consistency error, likely due to circular dependencies or missing header checks (`gn check`).
*   The error logs were often truncated or obscured by PowerShell pipe handling (`python tools/monitor_build.py` vs direct execution).

**Resolution (Temporary)**: 
*   **Revert**: We backed out the changes to `BUILD.gn` and `display.cc` to restore a clean, buildable state. 
*   **Impact**: The "Eyes" (Visual Cortex) are currently disabled. The "Ears" (Audio Hook) remain fully functional as they live in `content/browser` which was stable.

### 2. The Windows File Lock "Deadlock"
**Issue**: Rapid iteration is hindered by Windows holding file locks on `chrome.exe` and `content.dll` even after the window is closed (zombie processes).
**Impact**: `lld-link: error: permission denied`.
**Workaround**: Manual `taskkill /F /IM chrome.exe` is required before every link step. Automated scripts need to include this frame-killing logic.

---

## ✅ Successes (The "Working Body")

### 1. The Auditory Cortex (Native-to-Agent Bridge)
We successfully bypassed the high-level Web Speech API and tapped directly into the browser's audio bloodstream.
*   **Hook Point**: `NetworkSpeechRecognitionEngineImpl::TransmitAudioUpstream`.
*   **Method**: Intercepting raw Int16 PCM audio buffers before they are sent to Google's speech servers.
*   **Transport**: Base64 encoded chunks written to `chrome_debug.log` (The "Nerve Fiber").
*   **Receiver**: `nexus_agent.py` tails the log, extracts chunks, decodes them, and processes them.
*   **Result**: Zero-latency access to microphone data for any AI model (Gemini, OpenAI) without permission prompts or web page JavaScript.

### 2. Multi-Modal Agent Host (`nexus_agent.py`)
The Python host is now a robust "Brain" capable of:
*   **Sensory Input**: Receiving Audio streams (working) and Vision streams (ready for connection).
*   **Cognition**: Routing inputs to Gemini 1.5 Pro or OpenAI.
*   **Voice Activity Detection**: Tuned "Hyper-Sensitive" VAD (0.2s trigger) for snappy interactions.

---

## 🔮 Research Wishlist & Next Steps

To move from "Hearing Browser" to "Seeing Agent", we need to solve the following:

### 1. Visual Cortex Architecture (Refined)
*   **Isolate the Graft**: Instead of modifying `components/viz/service/BUILD.gn` (Kernel Space), create a standalone component `components/agent_interface` with its own `BUILD.gn`. 
*   **Dep-Injection**: Link `viz` against `agent_interface` rather than embedding source files directly. This reduces `gn` friction.

### 2. Input Synthesis (The Hands)
*   **Research Item**: Determine if we should use:
    *   **OS Level**: `ctypes` / `SendInput` (Global, easier, but "blind" to DOM).
    *   **Browser Level**: `InputInjector` (Chrome Internal, "correct" but requires complex C++ wiring).
*   **Recommendation**: Start with OS Level for Phase 3 to get quick wins, then graduate to Internal.

### 3. Agent UI overlay
*   **Goal**: The user needs feedback ("Listening", "Processing"). 
*   **Tech**: Implement a "Heads Up Display" using a dedicated, transparent overlay window (Electron or native DirectX overlay) rather than modifying Chrome's UI directly (which is notoriously hard).
