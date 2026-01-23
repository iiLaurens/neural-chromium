# Neural Runtime Architecture

## 1. Executive Summary
The Neural Runtime replaces the traditional "Browser Automation" model with a "Jacked-In" architecture.
- **Old Model**: Agent talks to Browser via WebSockets (CDP) over a network. High latency (>50ms).
- **New Model**: Agent (Glazyr) and Browser (Neural Chromium) share GPU memory (DXGI Shared Handles). Low latency (<16ms).

## 2. Monorepo Structure
We strictly use a Monorepo strategy to ensure binary compatibility between the C++ Producer and Python/Rust Consumer.

**Root**: `c:/operation-greenfield/neural-chromium`
- `src/glazyr`: The Agent Runtime Host.
- `src/components/viz`: The Rendering Engine modifications.

## 3. Data Flow
### 3.1 Zero-Copy Vision (The Optic Nerve)
1.  **Producer (Chromium)**:
    - Renders frame in `SwapChainPresenter` (D3D11).
    - Allocates backbuffer with `D3D11_RESOURCE_MISC_SHARED_NTHANDLE | D3D11_RESOURCE_MISC_SHARED_KEYEDMUTEX`.
    - Exports `HANDLE` via `IDXGIResource1::CreateSharedHandle`.
    - Sends `HANDLE` (uint64) to Glazyr via Named Pipe `\\.\pipe\NeuralChromiumSharedHandle`.
2.  **Consumer (Glazyr)**:
    - Receives `HANDLE`.
    - Imports to CUDA via `cudaImportExternalMemory`.
    - Maps direct to Tensor. No CPU copy.

### 3.2 Synchronization (Keyed Mutex)
To prevent tearing, we use `IDXGIKeyedMutex`:
- **Key 0**: Producer (Chrome) owns the texture.
- **Key 1**: Consumer (Glazyr) owns the texture.

Sequence:
- Chrome: `AcquireSync(0)` -> Draw -> `ReleaseSync(1)`
- Glazyr: `AcquireSync(1)` -> Inference -> `ReleaseSync(0)`

### 3.3 Direct Input Injection
- Glazyr writes input events to a generic Shared Memory Ring Buffer.
- Chrome's `GlazyrInputPoller` thread reads events and dispatches directly to `RenderWidgetHost`, bypassing Windows Message Pump.
