# ADR 0004: NixOS Declarative Foundation and Atomic Generations

## Status
Accepted

## Context
Operating systems can suffer from state drift, dependency conflicts, broken updates, and irrecoverable system states. PROJECT AURA requires deterministic, reproducible installations with instant rollback capability.

## Decision
1. Use **NixOS** and **Nix Flakes** as the declarative Linux foundation.
2. Package AURA components (`aurad`, `jarvisd`, `aura-shell`, `aura-cli`) as first-class Nix packages.
3. System updates generate a new immutable system generation.
4. If an update introduces an issue, `systemd-boot` allows instant reboot into any previous known-good generation.

## Consequences
- Guaranteed reproducibility across developer machines, CI, and production installations.
- Robust recovery without requiring full OS reinstallation.
