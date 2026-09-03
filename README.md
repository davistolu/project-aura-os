# PROJECT AURA

**A lightweight Linux-based personal computing platform with an OS-native AI runtime (JARVIS), custom Wayland shell, Windows compatibility, and declarative NixOS foundation.**

---

## Architecture Blueprint

```
+-------------------------------------------------------------------------+
|                  AURA Shell (GPU-Accelerated Wayland UI)                |
|       [Command Palette (Ctrl+Space)]  [HUD]  [Workspace Switcher]       |
+-------------------------------------------------------------------------+
                                    |
            +-----------------------+-----------------------+
            | (Deterministic IPC)                           | (Intent stream)
            v                                               v
+-----------------------+               +---------------------------------+
|      AURA System      |               |             JARVIS              |
|  (aurad: D-Bus / IPC) |               |      (jarvisd: Agent Runtime)   |
|   - Hardware APIs     |               |   - Model Router (Local/Cloud)  |
|   - Workspaces / Apps |               |   - Multi-Tier Memory Engine    |
|   - Power & Thermal   |               |   - Bounded Agent Planning Loop |
+-----------------------+               |   - Capability Tool Registry    |
            ^                           +---------------------------------+
            |                                           |
            |                                           v
            |                         +-----------------------------------+
            +-------------------------|  AURA Policy & Capability Engine  |
                                      |   - Capability Authorization      |
                                      |   - Secret Broker (Zero-Leakage)  |
                                      |   - Structured Tamper-Audit Log   |
                                      +-----------------------------------+
                                                        |
+-------------------------------------------------------+-----------------+
|                               System Foundation                         |
|  - NixOS Declarative State & Atomic Rollback Generations                |
|  - Upstream Linux Kernel (DRM/KMS, Mesa, PipeWire, Vulkan, libinput)   |
|  - Windows Compatibility (Wine-GE / Proton / Gamescope / KVM Fallback) |
|  - Developer Layer (Nix Shells, Rootless Podman, OCI Containers)       |
+-------------------------------------------------------------------------+
```

---

## Key Repository Components

- **`crates/`**:
  - [`aura-core`](crates/aura-core): Shared IPC protocols, capability tokens, and error definitions.
  - [`aura-policy`](crates/aura-policy): Capability authorization engine, permission gates, and secret broker.
  - [`aura-system`](crates/aura-system): Hardware monitoring and workspace profiles.
  - [`jarvis-providers`](crates/jarvis-providers): Local and cloud model adapters (Ollama, llama.cpp, Anthropic, OpenAI, Google).
  - [`jarvis-runtime`](crates/jarvis-runtime): JARVIS daemon (`jarvisd`), multi-tier memory, model router, and tool registry.
  - [`aura-compat`](crates/aura-compat): Empirical Windows/Proton/KVM runtime manager.
  - [`aura-dev`](crates/aura-dev): Per-project environment detector and Nix orchestrator.
  - [`aura-shell`](crates/aura-shell): Command palette parser, HUD state, and window manager integration.
  - [`aura-cli`](crates/aura-cli): Unified `aura` CLI utility.
  - [`aura-sdk`](crates/aura-sdk): Rust platform SDK.
- **`sdk/typescript/`**: First-class TypeScript SDK and application manifest validator.
- **`nix/`**: Flake, NixOS configuration profiles, systemd service units, and bootable ISO generator.
- **`docs/`**: Master architecture, security threat model, release gates, and Architecture Decision Records (ADR-0001 to ADR-0005).
- **`tests/`**: Automated verification test suite and adversarial red-team harness.

---

## Verification & Release Gate Tests

Run the complete test suite:
```bash
python tests/run_all_tests.py
```
