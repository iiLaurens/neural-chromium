# Neural-Chromium Task List

- [x] **Phase 1: Foundation & Documentation**
    - [x] Create `PRD.md` with defined goals (Agentic Use, Voice, Interchangeable AI, MCP/A2A/UCP). <!-- id: 0 -->
    - [x] Audit existing codebase for "Ghost" features (what is planned vs implemented). <!-- id: 1 -->
    - [/] Verify `config.json` usage and API key integration points. <!-- id: 2 -->

- [x] **Phase 2: The Auditory Cortex (Native Hook + Cloud Protocol)**
    - [x] **CONSULTANT STUDY**: Comparative analysis of Whisper vs Gemini vs Native Chrome Speech. <!-- id: 3 -->
    - [x] Wire up `nexus_agent.py` to receive Native Audio Chunks. <!-- id: 4 -->
    - [x] Implement Gemini 1.5 Audio Transcription (File-based fallback). <!-- id: 5 -->
    - [ ] Explore Realtime (Streaming) API integration for lower latency. <!-- id: 6 -->

- [/] **Phase 2.5: The Visual Cortex (C++ Shared Memory)**
    - [x] Create `components/agent_interface` scaffolding. <!-- id: 14 -->
    - [x] Implement `AgentSharedMemory` class (Named Shared Memory). <!-- id: 15 -->
    - [ ] Hook `Display::DrawAndSwap` in `display.cc` (PAUSED: Build System Corruption). <!-- id: 16 -->
    - [x] Verify Shared Memory data in `nexus_agent.py` (Implemented Python Host + Null DACL). <!-- id: 17 -->

- [/] **Phase 3: The Connected Brain (Agent Core)**
    - [x] Implement/Refactor Agent Client to support OpenAI, Gemini, and Anthropic. <!-- id: 6 -->
    - [x] reading `config.json` for API keys dynamically. <!-- id: 7 -->
    - [x] Create abstraction layer for "Model Provider". <!-- id: 8 -->
    - [x] Implement `generate_vision` in `GeminiProvider` (Multimodal). <!-- id: 18 -->
    - [x] Convert Shared Memory (RGBA) to Image Format (PIL). <!-- id: 19 -->
    - [x] Implement "Describe Screen" command. <!-- id: 20 -->

- [ ] **Phase 4: Standards Compliance (MCP & Protocols)**
    - [ ] Implement MCP Server interface for the Browser (Exposing DOM/Tabs as Resources). <!-- id: 9 -->
    - [ ] Verify A2A (Agent-to-Agent) readiness. <!-- id: 10 -->
    - [ ] UCP Compliance Verification. <!-- id: 11 -->

- [ ] **Phase 5: Agentic Action (The Hands)**
    - [ ] Calibrate Input Synthesizer (Mouse/Keyboard). <!-- id: 12 -->
    - [ ] Test End-to-End "Show and Tell" loop. <!-- id: 13 -->
