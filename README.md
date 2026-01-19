# Neural-Chromium

**Neural-Chromium** is an experimental build of the Chromium browser designed for high-fidelity AI agent integration. It exposes a low-latency perception and action interface ("System Interface") directly from the browser process, enabling next-generation research into synthetic user interaction models.

## Mission
To bridge the gap between AI agents and web interfaces by removing the overhead of accessibility layers and screen scraping, providing agents with:
*   **Direct Perception**: Zero-copy access to the rendering pipeline.
*   **High-Fidelity Action**: Millisecond-level input injection.
*   **Deep State Awareness**: Direct access to the DOM and internal browser states.

## Architecture
*   **Embedded Agent Process**: A dedicated process lifecycle coupled with the browser execution environment.
*   **Zero-Copy Vision**: Direct shared memory access to the composition surface (Viz) for sub-16ms inference latency.
*   **High-Precision Input**: Coordinate transformation pipeline for mapping agent actions to internal browser events.

## Repository Structure
This project utilizes a **Source Overlay** pattern to maintain a lightweight footprint while modifying the massive Chromium codebase.
*   `src/`: Contains the specific modified files that overlay the official Chromium source.
*   `docs/`: Project documentation, including `challenges_report.md` (Build Analysis) and `development_log.md` (Tasks).
*   `scripts/`: Utilities for applying changes to and capturing snapshots from a full Chromium build.

## 🧠 Current Status: The "Hearing" Browser (Day 2)

### ✅ Auditory Cortex (Online)
*   **Feature**: Native Audio Bridge (`content.dll` -> `nexus_agent.py`).
*   **Capabilities**: Real-time microphone capture, "Hyper-Sensitive" Voice Activity Detection (0.2s), Gemini 1.5 Pro transcription.
*   **Verification**: "Matrix Rain" in terminal validates packet flow.

### ⚠️ Visual Cortex (Paused)
*   **Feature**: "Computer Use" / Zero-Latency Video Stream.
*   **Status**: Blocked by Build System "Antibody" response (`manifest error` in `gn gen`).
*   **Plan**: Requires architectural refactor (Day 3).

## Getting Started

### Prerequisites
*   Windows 10/11 (64-bit)
*   **Critical:** The source code path must **NOT** contain spaces (e.g., use `C:\neural-chromium`, NOT `C:\My Projects\neural-chromium`). Chromium build tools (gn, ninja) will fail if there are spaces in the path.
*   Visual Studio 2022 (with Desktop development with C++, MFC/ATL support)
*   [depot_tools](https://commondatastorage.googleapis.com/chrome-infra-docs/flat/depot_tools/docs/html/depot_tools_tutorial.html) installed and in your PATH.

### 1. Fetch Chromium Source
Create a working directory (e.g., `c:\Operation Greenfield\neural-chromium`) and fetch the code. **Note:** This will download >50GB of data.

```powershell
mkdir c:\Operation Greenfield\neural-chromium
cd c:\Operation Greenfield\neural-chromium
fetch chromium
cd src
git checkout main
gclient sync
```

### 2. Apply the Overlay
Apply the Neural-Chromium modifications to your vanilla source tree.

```powershell
# From this repository's root
powershell -ExecutionPolicy Bypass -File scripts\apply_snapshot.ps1
```
*Note: You may need to adjust paths in `scripts\apply_snapshot.ps1` if your directory structure differs.*

### 3. Build
Generate build files and compile.

```powershell
cd c:\Operation Greenfield\neural-chromium\src
gn gen out\AgentDebug
autoninja -C out\AgentDebug chrome
```

## Contributing
We welcome contributions! Because we don't host the full Chromium source, the workflow is slightly different:

1.  **Modify**: Make your changes in your full Chromium `src` directory.
2.  **Track**: If you modified a new file, add its path to `$TrackedFiles` in `scripts/save_snapshot.ps1`.
3.  **Snapshot**: Run the snapshot script to copy your changes back to this overlay repository.
    ```powershell
    powershell -ExecutionPolicy Bypass -File scripts\save_snapshot.ps1
    ```
4.  **Commit**: Commit the updated files in this repository and open a Pull Request.

## Discussion & Roadmap
We are currently focusing on:
*   [ ] Reducing IPC latency for the Agent Interface.
*   [ ] Exposing the localized accessibility tree to the Agent Process.
*   [ ] Headless operation with full GPU support.

Join the discussion in the [Issues](https://github.com/mcpmessenger/neural-chromium/issues) tab!

## Disclaimer
This project is for educational and research purposes only, focusing on the intersection of browser engines and autonomous agents. It is not affiliated with Google or the Chromium project.
