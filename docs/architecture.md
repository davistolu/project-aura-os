# PROJECT AURA Master Architecture Specification

## 1. Executive Summary & Product Vision
PROJECT AURA is a Linux-native personal computing platform designed from first principles with an integrated AI runtime (**JARVIS**), a custom Wayland desktop shell, native Windows application compatibility through curated Wine/Proton/KVM profiles, and a declarative, reproducible operating system foundation based on NixOS.

Unlike conventional Linux distributions with post-hoc AI extensions or chatbot apps, AURA treats the AI runtime as an operating system service subject to deterministic security policies, strict capability gating, and full auditability.

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

## 2. Core Subsystems

### 2.1 AURA OS (Linux Foundation)
- **Base OS**: Minimal NixOS profile configured declaratively via Nix flakes.
- **Init & Service Manager**: `systemd` managing hardened service units with `ProtectSystem=strict`, `NoNewPrivileges=true`, and private temporary directories.
- **Audio & Media**: PipeWire with WirePlumber session management.
- **Display Server**: Wayland compositor with direct DRM/KMS buffer allocation and Vulkan hardware acceleration.

### 2.2 AURA Shell
- **Interaction Paradigm**: Global command palette accessed via `Ctrl+Space`.
- **Fast Deterministic Path**: Commands matching known system verbs (`open`, `kill`, `switch-workspace`, `doctor`, `compat`) execute instantly through zero-latency IPC without invoking LLM inference.
- **AI-Assisted Path**: Ambiguous natural language prompts route to `jarvisd` for intent classification, tool orchestration, and capability-bounded execution.

### 2.3 JARVIS AI Runtime (`jarvisd`)
- **Local-First Model Router**: Prioritizes local SLM inference (Ollama / llama.cpp) for offline operations and private telemetry; routes complex reasoning to configured cloud endpoints (Anthropic, OpenAI, Google) when user policy permits.
- **Multi-Tier Memory Architecture**:
  - *Working Memory*: Scratchpad for active execution context, cleared upon task completion.
  - *Session Memory*: Ephemeral multi-turn interaction logs.
  - *Project Memory*: Contextual build instructions, project manifests, and directory layouts.
  - *User Preferences & Personas*: Explicitly inspectable, editable, and resettable key-value stores.
- **Agent Loop**: Bounded `Observe -> Plan -> Authorize -> Execute -> Verify -> Report` cycle with bounded retries and cancellation tokens.

### 2.4 Security & Capability Architecture
- The AI model is strictly **unprivileged**. It possesses zero ambient permissions and cannot invoke `sudo` or execute raw shell strings by default.
- Every system interaction requires a capability token (e.g., `filesystem.read`, `process.kill`, `workspace.switch`).
- Actions are classified into permission tiers:
  - `OBSERVE`: Read-only system state inspection.
  - `SUGGEST`: Recommendation requiring user confirmation.
  - `EXECUTE_SAFE`: Automated execution of reversible or low-risk actions.
  - `EXECUTE_PRIVILEGED`: Approval-gated actions requiring explicit user authorization.
  - `AUTONOMOUS`: Configured background operations bounded by rate and scope.
- **Secret Broker**: API keys, SSH credentials, and passwords are never injected into LLM prompt contexts. The agent interacts with handles/tokens that the broker resolves internally.

### 2.5 Windows Compatibility & Gaming Stack
- **Application Engine**: Automated prefix creation and DLL override management for Windows executables (`.exe`, `.msi`).
- **Gaming Subsystem**: Integrated Proton, DXVK, VKD3D, Gamescope resolution scaling, and GameMode scheduler prioritization.
- **Virtualization Fallback**: Seamless QEMU/KVM virtual machine orchestration with virtio-fs shared folders and clipboard synchronization for workloads incompatible with Wine.

### 2.6 Developer Experience (`aura-dev`)
- Automatic project type detection (`Rust`, `Node.js`, `Python`, `Go`, `PHP`, `C/C++`).
- Declarative per-project environments with isolated dependencies (`aura dev shell`, `aura dev doctor`, `aura dev services`).
- Structured diagnostic integration enabling JARVIS to parse compiler errors, test failures, and service health checks directly.
