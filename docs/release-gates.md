# PROJECT AURA Release Gates & Performance Budgets

To ensure high reliability, predictable resource consumption, and rock-solid stability, every release of PROJECT AURA must pass the following release gates.

## 1. Measurable Performance Budgets

| Metric | Target Budget | Hard Failure Threshold |
| :--- | :--- | :--- |
| **Cold Boot (UEFI to Shell)** | < 6.0s on NVMe | > 10.0s |
| **Idle RAM (OS + Shell + jarvisd)** | < 450 MB | > 750 MB |
| **Idle CPU (All background daemons)**| < 0.5% average | > 1.5% |
| **Command Palette Latency** | < 15ms | > 50ms |
| **Deterministic IPC Round-Trip** | < 2ms | > 10ms |
| **Local SLM First-Token Latency** | < 400ms (on GPU/NPU) | > 1500ms |
| **Disk I/O During Idle** | 0 B/s steady-state | > 100 KB/s |

## 2. Mandatory Release Gates

### Gate 1: Bootable Foundation & Generation Rollback
- [x] NixOS configuration produces bootable ISO and QEMU image.
- [x] Wayland session initializes directly without relying on heavy desktop environments.
- [x] Upgrades are atomic and can be rolled back via `systemd-boot` generations.

### Gate 2: Security & Capability Isolation
- [x] Zero ambient root access for `jarvisd`.
- [x] 100% of tool invocations pass through `aura-policy`.
- [x] Red-team prompt injection suite passes with 0 unauthorized privilege escalations.
- [x] Structured audit logs generated in `/var/log/aura/ai/`.

### Gate 3: Windows & Gaming Compatibility
- [x] Empirical compatibility database tracking tested titles and apps.
- [x] Wine/Proton prefix isolation per application.
- [x] Gamescope and GameMode integration functional.
- [x] KVM/virtio fallback available for non-Wine compatible software.

### Gate 4: Developer Platform & Toolchain
- [x] Automatic project detection (`Rust`, `Node`, `Python`, `Go`).
- [x] `aura dev doctor` diagnostics and isolated service management.
- [x] TypeScript and Rust SDK API stability verification.
