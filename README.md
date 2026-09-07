# PROJECT AURA

<div align="center">

**A Next-Generation Personal Computing Platform with OS-Native AI Runtime (DAVIS), Live Hardware Control Center, Empirical Windows Compatibility, and Declarative Foundation.**

[![CI/CD](https://github.com/davistolu/project-aura-os/actions/workflows/ci.yml/badge.svg)](https://github.com/davistolu/project-aura-os/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Linux / Windows Subsystem](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-green.svg)](https://github.com/davistolu/project-aura-os)
[![Voice AI: DAVIS](https://img.shields.io/badge/Voice%20AI-DAVIS%20Neural-purple.svg)](docs/voice-assistant-davis.md)

</div>

---

## ⚡ Quick Start

Launch the unified Project Aura OS Shell & DAVIS Voice Runtime:

```bash
# Clone the repository
git clone https://github.com/davistolu/project-aura-os.git
cd project-aura-os

# Launch Aura OS & DAVIS
python aura.py
```

- **Say *"Davis"*** &rarr; Davis responds *"Yeah?"* &rarr; speak any command (*"What is the weather in London?"*, *"Allocate 8 GB of RAM to AI"*, *"Set power mode to Performance"*).
- **Type anytime** directly into the `AURA » ` prompt (or use [1-Key Shortcuts](#-instant-1-key-shortcuts)).

---

## 🏗️ Architecture Overview

```
+---------------------------------------------------------------------------------------------------+
|                            AURA Shell (GPU-Accelerated Wayland UI / TUI HUD)                     |
|            [Live Status Bar]  [Command Palette / Help]  [Workspace Switcher (1-5)]                |
+---------------------------------------------------------------------------------------------------+
                                              |
                   +--------------------------+--------------------------+
                   | (Deterministic IPC)                                 | (Intent & Voice stream)
                   v                                                     v
+---------------------------------------+               +-------------------------------------------+
|          AURA System & Settings       |               |                   DAVIS                   |
|  - Real Wi-Fi Scanner (netsh wlan)    |               |         (OS-Native AI Runtime)            |
|  - Real Bluetooth Devices (PnP / WMI) |               |  - Wake-Word Engine ("Davis")             |
|  - Real Power Schemes (powercfg)      |               |  - Acoustic Echo Guard (VoiceIO Mutex)    |
|  - Real Memory (GlobalMemoryStatusEx) |               |  - Google Web Speech STT & Neural TTS     |
|  - Real Network & ICMP Ping (1.1.1.1) |               |  - Live APIs (Weather, Forex, Wikipedia)  |
|  - Workspace Profiles (General/Gaming)|               |  - Multi-Turn Memory (~/.aura_memory.json)|
+---------------------------------------+               +-------------------------------------------+
                   ^                                                     |
                   |                                                     v
                   |                                   +--------------------------------------------+
                   +-----------------------------------|      AURA Policy & Capability Ledger       |
                                                       |  - Zero-Trust Capability Tokens            |
                                                       |  - Append-Only AI Audit Log                |
                                                       |  - Hardware Microphone Killswitch (/mute)  |
                                                       +--------------------------------------------+
                                                                         |
+------------------------------------------------------------------------+--------------------------+
|                                           System Foundation                                       |
|  - Declarative NixOS Baseline & Atomic Generations (nix/flake.nix)                                 |
|  - Upstream Linux Kernel (DRM/KMS, Mesa 24.1, PipeWire Audio, Vulkan 1.3)                         |
|  - Windows Compatibility (Proton Direct, Wine Prefix Isolation, Gamescope 144Hz)                  |
|  - Developer Studio (Nix Shells, Rootless Containers, Dev Doctor)                                 |
+---------------------------------------------------------------------------------------------------+
```

---

## 🌟 Key Features

### 1. 🤖 DAVIS Hands-Free AI Assistant
- **Continuous Wake-Word Detection**: Listens in the background for *"Davis"* or *"Hey Davis"*.
- **Zero-Latency Pre-Warmed Voice**: Instant human-like verbal acknowledgements (*"Yeah?"*, *"What can I do for you?"*) via `~/.aura_voice_cache/`.
- **Acoustic Echo Guard**: Synchronous audio mutex prevents microphone feedback loops.
- **Live Connected APIs**: Weather (Open-Meteo), Forex (open.er-api.com), Math/Science solver, Wikipedia/DuckDuckGo web search, and iTunes song discovery.
- **Multi-Turn Persistent Memory**: Stores user identity and conversation turns across sessions in `~/.aura_memory.json`.

### 2. ⚙️ Real PC Hardware & Control Center (`/settings`)
*100% Real Live Hardware & Subsystems — Zero Dummy Data:*
- **📶 Wi-Fi Wireless Manager (`/wifi`, `w`)**: Scans real broadcasted wireless networks (`netsh wlan`), displays signal strength bars `[████]`, channel bands, and security protocols.
- **📡 Bluetooth Peripheral Hub (`/bt`, `b`)**: Monitors real paired peripherals (headphones 🎧, gamepads 🎮, keyboards ⌨️) and battery levels.
- **⚡ Power & Thermals (`/power`, `f8`-`f10`)**: Switches active Windows power schemes using `powercfg` (`Performance`, `Balanced`, `Power Saver`, `Gaming Boost`).
- **🧠 RAM & CPU Allocator (`/res`, `r`)**: Sets hard memory quotas for DAVIS AI, Gaming sandboxes, CPU core pinning, and ZRAM compressed swap.
- **🌐 Network & DNS (`/net`, `n`)**: Measures live ICMP round-trip latency (`ping 1.1.1.1`), discovers IP/Gateway, and switches DNS resolvers (Cloudflare `1.1.1.1`, Google `8.8.8.8`, Quad9 `9.9.9.9`).

### 3. 🖥️ Wayland Workspace Profiles
- **`1` (General)**: Multitasking, web browsing, and document editing.
- **`2` (Development)**: Tiled editor, terminals, and Nix development shells.
- **`3` (Gaming)**: Gamescope compositor, Proton Direct, and 144Hz GameMode priority.
- **`4` (Creative)**: PipeWire low-latency audio/video studio.
- **`5` (AI)**: Local SLMs, autonomous agents, and model runtime.

---

## ⌨️ Instant 1-Key Shortcuts

Type any key directly into the prompt without typing full verbs:

| Key | Instant Action | Target Verb |
| :--- | :--- | :--- |
| **`1`** .. **`5`** | Switch to Workspace 1–5 | `/ws 1` .. `/ws 5` |
| **`w`** | Open Real Wi-Fi Network Scanner | `/wifi scan` |
| **`b`** | Open Bluetooth Device Center & Battery Levels | `/bt scan` |
| **`c`** / **`cfg`** | Open Unified System Settings Hub | `/settings` |
| **`r`** / **`res`** | Open RAM & CPU Resource Allocator | `/res` |
| **`n`** / **`net`** | Run Live ICMP Ping & DNS Diagnostics | `/net ping` |
| **`p`** / **`ps`** | Open Process Monitor & Resource Ledger | `/sys ps` |
| **`s`** / **`sys`** | Open Hardware Telemetry Snapshot | `/sys status` |
| **`f8`** / **`saver`** | Switch Power Scheme to **Battery Saver** | `/power saver` |
| **`f9`** / **`balanced`** | Switch Power Scheme to **Balanced** | `/power balanced` |
| **`f10`** / **`perf`** | Switch Power Scheme to **Performance** | `/power perf` |
| **`m`** / **`mute`** | Toggle Microphone Privacy Mute | `/mute` |
| **`?`** / **`h`** | Display Complete Help Manual | `/help` |

---

## 📁 Repository Structure

```
.
├── aura.py                      # Unified AURA OS Entrypoint & Live HUD Bar
├── scripts/
│   ├── settings_manager.py      # Real Hardware, WLAN, Bluetooth, Powercfg & RAM Allocator
│   ├── palette_tui.py           # Rich TUI Desktop HUD, Settings Cards & Help Manual
│   ├── dialogue_engine.py       # DAVIS Natural Language, Live APIs & System Intent Router
│   ├── external_services.py     # Live Weather, Currency, Math, Wikipedia & Song APIs
│   ├── system_access.py         # Local File Search, Document Previews & Storage Inspector
│   ├── memory_store.py          # Multi-Turn Persistent Dialogue Memory
│   ├── neural_voice.py          # Edge-TTS Synthesizer, Pre-Cache & MCI Audio Player
│   └── speak.ps1 / record_mic.ps1 # Native Windows Audio Helpers
├── crates/                      # Core Rust Subsystems (Core, Policy, Shell, Compat, CLI)
├── sdk/                         # TypeScript Platform SDK
├── nix/                         # NixOS Declarative Flake, Base Config & ISO Builder
├── docs/                        # Complete Documentation Suite
│   ├── user-manual.md           # Master User Guide & Features Walkthrough
│   ├── cli-reference.md         # Full Command Line & Verbs Reference
│   ├── voice-assistant-davis.md # DAVIS AI Architecture & Audio Subsystem
│   ├── architecture.md          # Architectural Specifications
│   └── security-model.md        # Zero-Trust Capability & Threat Model
└── tests/                       # Automated Test Suite & Release Verification
```

---

## 🧪 Running Tests

Run the complete test suite:

```bash
python tests/run_all_tests.py
```

---

## 📖 Documentation Directory

- 📘 [**User Manual**](docs/user-manual.md): Comprehensive guide to all features, workspaces, and workflows.
- 📙 [**CLI & Verbs Reference**](docs/cli-reference.md): Detailed syntax and options for all command palette verbs.
- 🎙️ [**DAVIS Voice Assistant**](docs/voice-assistant-davis.md): Deep dive into speech recognition, neural audio synthesis, and memory.
- 📐 [**System Architecture**](docs/architecture.md): Operating system blueprint and subsystem boundaries.
- 🛡️ [**Security & Threat Model**](docs/security-model.md): Capability token permissions and append-only audit logging.

---

## 📄 License

Project Aura is open-source software licensed under the [MIT License](LICENSE).
