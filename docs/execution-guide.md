# PROJECT AURA Execution and Deployment Guide

This guide describes how to build, test, and run **PROJECT AURA** as a fully functional operating system across three deployment targets.

---

## Target 1: Instant Host Simulation & Interactive Shell (No Prerequisites)

You can run and test the complete AURA desktop environment, Command Palette, System Daemon, and JARVIS capability engine directly in your terminal right now:

```bash
python scripts/run_aura_simulator.py
```

### Try These Interactions in the Simulator:
- `status` → Inspects real-time hardware telemetry and ultra-low idle resource budget (<450 MB RAM).
- `workspace 3` → Switches active Wayland workspace profile to Gaming Mode (Gamescope, Proton, DXVK).
- `run cyberpunk.exe` → Demonstrates automated Proton/DXVK runtime selection.
- `run notepad.exe` → Demonstrates isolated Wine staging prefix creation.
- `dev doctor` → Analyzes project dependencies and checks sandboxed toolchains.
- `sudo rm -rf /` → Demonstrates JARVIS zero-trust security gate blocking unauthorized root execution.
- `audit` → Displays the tamper-evident security audit log.

---

## Target 2: Windows Host Mode (WSL2 + Wayland + systemd)

Run AURA inside Windows without rebooting using WSL2's native Linux kernel, Wayland graphical support (WSLg), and systemd:

### 1. Enable WSL2 and systemd
In Windows PowerShell (Administrator):
```powershell
wsl --install -d Ubuntu
```

Ensure systemd is enabled in `/etc/wsl.conf`:
```ini
[boot]
systemd=true
```

### 2. Launch AURA Host Mode
Run the launcher script:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_wsl.ps1
```

---

## Target 3: Bootable Live ISO & Physical Hardware / Virtual Machine

To compile the declarative NixOS foundation into a bootable ISO image for physical hardware or a virtual machine:

### 1. Build the ISO with Nix Flakes
On any Linux system with Nix installed:
```bash
./scripts/build_iso.sh
```
This evaluates `nix/flake.nix` and outputs a bootable `aura-os-installer.iso` image in `result-iso/`.

### 2. Boot in QEMU Virtual Machine
Test the bootable ISO in a local hardware-accelerated VM:
```bash
./scripts/run_qemu.sh result-iso/iso/*.iso
```

### 3. Flash to USB for Physical Hardware Boot
Flash the ISO to a USB flash drive (replace `/dev/sdX` with your USB drive):
```bash
sudo dd if=result-iso/iso/aura-os-installer.iso of=/dev/sdX bs=4M status=progress conv=fsync
```
Boot your computer via UEFI into the USB drive to launch native AURA OS.

---

## Target 4: Compiling the Rust System Crates

To compile the native Rust binaries (`aurad`, `jarvisd`, `aura-cli`, `aura-shell`):

```bash
cargo build --release --workspace
```
The compiled binaries will be placed in `target/release/`:
- `aura` (CLI)
- `aurad` (System Daemon)
- `jarvisd` (JARVIS AI Runtime)
