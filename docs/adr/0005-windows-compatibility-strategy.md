# ADR 0005: Empirical Windows Compatibility and Gaming Strategy

## Status
Accepted

## Context
A personal operating system must provide a seamless bridge to Windows applications and games without false promises of 100% Wine compatibility.

## Decision
1. Implement a tiered compatibility architecture:
   - **Tier 1: Native Wine/Proton Runtime**: For high-performance gaming and desktop applications using DXVK, VKD3D-Proton, and Gamescope with isolated prefixes.
   - **Tier 2: Managed Compatibility Database**: Local and community-verified configuration profiles for popular Windows software.
   - **Tier 3: KVM / QEMU Virtual Machine Fallback**: Seamless virtualized environment with virtio-fs shared storage, clipboard, and audio pass-through for software requiring anti-cheat or proprietary Windows kernel drivers.
2. Provide transparent runtime selection via `aura compat run <file.exe>` with empirical recommendations.

## Consequences
- Transparent user expectations based on empirical test results.
- Zero host system pollution via isolated prefix and VM boundaries.
