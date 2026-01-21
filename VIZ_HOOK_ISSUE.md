# Zero-Copy Viz Hook: Windows Implementation Report

## Overview
We are attempting to implement a "Zero-Copy" screen capture mechanism for Neural-Chromium by hooking directly into the Viz compositor's `SoftwareOutputDevice`. This allows capturing frames from the shared memory buffer before they are presented to the OS, avoiding slow `BitBlt` or `PrintWindow` calls.

**Status:** Implementation complete, but Benchmark reports **0 FPS** on Windows 11.
**Hypothesis:** The hooked `SoftwareOutputDevice` class is either not being instantiated, or the rendering path is bypassing the hook (e.g., using GPU Rasterization despite `--disable-gpu`).

## Implementation Details

### 1. NeuralCortexWriter
We implemented `NeuralCortexWriter` to manage a shared memory segment:
- **Map Name:** `Local\NeuralChromium_VisualCortex_V3`
- **Size:** 16MB (4K ready)
- **Security:** NULL DACL for cross-process access (Browser/GPU <-> Agent).
- **Header:** `VisualCortexHeader` with timestamp, dimensions, and atomic `frame_index`.

### 2. SoftwareOutputDevice Hooks
We identified that Windows uses specialized subclasses of `SoftwareOutputDevice`. We have added `NeuralCortexWriter::Write(pixmap)` hooks to:

1.  **`SoftwareOutputDevice::EndPaint`** (Base class - Bypassed on Windows)
2.  **`SoftwareOutputDeviceWinDirect::EndPaintDelegated`** (Direct HWND drawing)
3.  **`SoftwareOutputDeviceWinProxy::EndPaintDelegated`** (Proxy/Layered Window drawing)
4.  **`SoftwareOutputDeviceWinSwapChain::EndPaintDelegated`** (DirectComposition / SwapChain path)

### 3. Build Configuration
- Added `components/viz/service/display/neural_cortex_writer.h` and `.cc` to `components/viz/service/BUILD.gn`.
- Launch Flags: `--disable-gpu --enable-logging --v=1`

## The Problem (0 FPS)
Despite these hooks, the Python agent reports 0 frames received.
- **Python Side:** "Visual Cortex Connected (Host Mode)". This confirms the shared memory *can* be created by Python, but C++ is not writing to it.
- **C++ Side:** `chrome_debug.log` shows **NO** signs of `[VisualCortex]` logs.
    - We added `LOG(ERROR)` to `NeuralCortexWriter::Init()` and `Write()`.
    - None of these logs appear.
    - This strongly implies that **NONE** of the hooked classes (`SoftwareOutputDeviceWin*`) are being instantiated.

### Diagnosis
If `SoftwareOutputDeviceWin*` are not being created, Chrome must be using:
1.  **SkiaOutputDevice (GPU Path):** Even with `--disable-gpu`, Chrome might be using a Software GL implementation (SwiftShader) which sits below Viz but *above* the output device in a different way, or uses `SkiaOutputDeviceDComp`.
2.  **OutputSurfaceProviderImpl Logic:** The logic in `OutputSurfaceProviderImpl::CreateSoftwareOutputDeviceForPlatform` might be failing or taking a different branch (e.g., `headless`).

## Files Modified
The following files contain the implementation and need to be preserved:

- `src/components/viz/service/display/neural_cortex_writer.h` (New)
- `src/components/viz/service/display/neural_cortex_writer.cc` (New)
- `src/components/viz/service/display/software_output_device.h`
- `src/components/viz/service/display/software_output_device.cc`
- `src/components/viz/service/display_embedder/software_output_device_win.cc`
- `src/components/viz/service/display_embedder/software_output_device_win_swapchain.cc`
- `src/components/viz/service/BUILD.gn`
- `src/content/browser/speech/network_speech_recognition_engine_impl.cc` (Audio Hook - Working)
