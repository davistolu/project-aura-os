# ADR 0001: Local IPC Architecture Strategy

## Status
Accepted

## Context
PROJECT AURA requires fast, secure, and lightweight inter-process communication between the AURA desktop shell, system daemon (`aurad`), AI runtime (`jarvisd`), and platform applications. Unnecessary HTTP overhead or heavy serialization must be avoided.

## Decision
1. **System Services**: Use **D-Bus** on Linux for standard system integration (systemd, NetworkManager, PipeWire, UPower).
2. **High-Performance Internal IPC**: Use **Unix Domain Sockets** with binary/JSON framing for high-throughput, low-latency streaming between `aura-shell` and `jarvisd`.
3. **Cross-Platform Host Support**: On Windows/WSL2 host mode, fallback to named pipes / local sockets with token authentication.

## Consequences
- Ultra-low latency (<2ms) for command palette queries.
- Zero network stack overhead or external attack surface.
- Strict file descriptor permission controls on the socket endpoints.
