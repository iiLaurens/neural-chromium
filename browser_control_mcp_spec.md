# [DEPRECATED] Browser Control MCP Spec

> [!WARNING]
> This specification is **DEPRECATED**.
> The Neural Chromium architecture has shifted to a **Monorepo** and **Zero-Copy Shared Memory** model.
>
> Please refer to: `c:/operation-greenfield/neural-chromium/docs/NEURAL_RUNTIME_ARCHITECTURE.md`

## Key Changes
- **Transport**: WebSockets (CDP) -> **Shared Memory (DXGI Handles)**.
- **Control**: JSON-RPC -> **Direct Input Injection**.
- **Repo**: Multi-repo -> **Monorepo** (`src/glazyr` inside `neural-chromium`).

The MCP server concept is replaced by a direct `glazyr_runtime.py` host process.
