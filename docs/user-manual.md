# PROJECT AURA — Complete Operating System User Manual

Welcome to **PROJECT AURA**, a modern personal computing platform designed for speed, deep hardware control, empirical Windows app compatibility, and an OS-native conversational intelligence engine: **DAVIS**.

---

## 1. Getting Started & Launching AURA

AURA provides a unified entrypoint for both interactive desktop usage and hands-free voice operations:

```bash
# Launch Project Aura OS Shell & DAVIS Voice Runtime
python aura.py
```

Upon launch, AURA displays the **Live Desktop HUD Bar** and opens the **Global Command Prompt**:

```
+---------------------------------------------------------------------------------------------------+
| AURA OS 1.0  [Development]  Wayland 1.23 | CPU: 3.8%  RAM: 4,120 MB (25.1%) / 16.0 GB | 🎙️ MIC: ACTIVE |
+---------------------------------------------------------------------------------------------------+
AURA » 
```

---

## 2. Desktop HUD Bar & Workspace Profiles

The top HUD bar provides real-time system metrics:
- **Active Workspace Pill**: Shows the active Wayland workspace.
- **Hardware Gauges**: Live CPU load, real physical RAM used/total, and GPU driver state.
- **Microphone Status**: Indicates whether DAVIS is actively listening for its wake-word (*"Davis"*).
- **System Clock**: Real-time 12-hour local clock.

### Workspace Modes
Switch workspaces instantly using number keys or `/ws <id>`:

| Key | Workspace Profile | Focus & Optimizations |
| :--- | :--- | :--- |
| **`1`** | **General** | Everyday multitasking, lightweight web browsing, and office work. |
| **`2`** | **Development** | Tiled editor, shell terminals, container runtimes, and compiler toolchains. |
| **`3`** | **Gaming** | Gamescope compositor, Proton Direct rendering, DXVK, and 144Hz GameMode priority. |
| **`4`** | **Creative** | PipeWire low-latency audio/video production suite. |
| **`5`** | **AI Workflows** | Local SLM inference, autonomous agents, and dataset tooling. |

---

## 3. DAVIS Voice Assistant & Intelligence Runtime

**DAVIS** is an OS-native AI runtime integrated directly into the system shell.

### How to Interact
1. **Say the Wake-Word**: Say **"Davis"** or **"Hey Davis"** into your microphone.
2. **Instant Acknowledgement**: Davis responds immediately (*"Yeah?"*, *"What can I do for you?"*, *"Yes? I'm listening."*).
3. **Speak Your Command**: Speak your request clearly (4-second high-accuracy Google Web Speech window).
4. **Hands-Free Response**: Davis synthesizes responses with high-fidelity human neural voice (`en-US-ChristopherNeural` / SAPI fallback) and immediately returns to standby.

### Integrated Capabilities
- **Live Weather**: *"What is the weather in Tokyo?"* (Real-time temperature, wind, humidity via Open-Meteo).
- **Forex & Currency**: *"Convert 100 USD to EUR"* (Live exchange rates via open.er-api.com).
- **Math & Science**: *"What is 45 * 12 + 180?"* or *"What is the square root of 144?"*.
- **Web Knowledge**: *"Who is Alan Turing?"* or *"Tell me about quantum computing"* (Wikipedia & DuckDuckGo).
- **Song Discovery**: *"Who sings Bohemian Rhapsody?"* (iTunes Search API).
- **Local File Search**: *"Find document report.pdf"* or *"Read file notes.txt"*.
- **Persistent Memory**: Davis remembers your name, conversation history, and preferences across sessions in `~/.aura_memory.json` (*"My name is Alex"*, *"What did we talk about?"*).

---

## 4. Real PC Hardware Configuration & Control Center

Project Aura interfaces with **100% real PC hardware, network adapters, and Windows subsystem services** (Zero dummy data).

### Control Center Hub (`/settings`, `c`)
Type `/settings` or press `c` to open the full visual control card:
- **Wi-Fi Manager (`/wifi`, `w`)**: Scans real broadcasted wireless networks (`netsh wlan`), displays signal strength bars `[████]`, channel bands, and encryption protocols. Connect or disconnect with one command.
- **Bluetooth Hub (`/bt`, `b`)**: Monitors real paired peripherals (headphones 🎧, gamepads 🎮, keyboards ⌨️, phones 📱) and battery percentages.
- **Power Management (`/power`, `f8`-`f10`)**: Directly switches active Windows power schemes using `powercfg` (`Performance`, `Balanced`, `Power Saver`, `Gaming Boost`).
- **RAM & CPU Allocator (`/res`, `r`)**: Configures memory limits for DAVIS AI (e.g. 4–8 GB), Gaming sandboxes (e.g. 16 GB), CPU core affinity pinning, and ZRAM compressed swap.
- **Network & DNS (`/net`, `n`)**: Measures live ICMP round-trip latency (`ping 1.1.1.1`), inspects real IP and Gateway, and switches DNS resolvers (Cloudflare `1.1.1.1`, Google `8.8.8.8`, Quad9 `9.9.9.9`).
- **Audio Volume (`/vol`)**: Adjusts master system volume (0–100%) and mute state.

---

## 5. Instant 1-Key Shortcut Cheatsheet

Type any of the following keys directly into the `AURA » ` prompt:

| Key | Instant Action | Target Command |
| :--- | :--- | :--- |
| **`1`** .. **`5`** | Switch to Workspace 1–5 | `/ws 1` .. `/ws 5` |
| **`w`** | Scan & Display Real Wi-Fi Networks | `/wifi scan` |
| **`b`** | Inspect Bluetooth Peripherals & Battery | `/bt scan` |
| **`c`** / **`cfg`** | Open Unified Settings Control Center | `/settings` |
| **`r`** / **`res`** | Open RAM & CPU Quota Allocator | `/res` |
| **`n`** / **`net`** | Run Real ICMP Ping & DNS Diagnostics | `/net ping` |
| **`p`** / **`ps`** | Open Process Monitor & Resource Ledger | `/sys ps` |
| **`s`** / **`sys`** | Open Real Hardware Telemetry Snapshot | `/sys status` |
| **`f8`** | Switch Power Scheme to **Battery Saver** | `/power saver` |
| **`f9`** | Switch Power Scheme to **Balanced** | `/power balanced` |
| **`f10`** | Switch Power Scheme to **Performance** | `/power perf` |
| **`m`** | Toggle Microphone Privacy Mute | `/mute` |
| **`?`** / **`h`** | Open Global Help Manual & Command Directory | `/help` |

---

## 6. Windows Application & Gaming Compatibility

Project Aura provides automated compatibility layers for running Windows executables:
- **Proton Direct Runner**:
  ```
  AURA » /run cyberpunk.exe
  # Or: /run game.exe
  ```
  Launches with DXVK (Direct3D 9/10/11 &rarr; Vulkan), VKD3D-Proton (Direct3D 12 &rarr; Vulkan), and Gamescope compositor (1440p @ 144Hz).
- **Wine Prefix Isolation**:
  ```
  AURA » /run notepad.exe
  ```
  Executes within an isolated prefix at `/var/lib/aura/wine_prefixes/<app>`.

---

## 7. Security, Privacy & Zero-Trust Audit Ledger

AURA implements strict capability tokens and cryptographic logging:
- **Capability Tokens**: Every hardware, file, or network action requires authorization (`system.hardware.read`, `audio.capture`, `filesystem.read`, `network.status.read`).
- **Structured Audit Ledger (`/sec audit`)**: Every granted or denied action is recorded to an append-only cryptographic JSON log.
- **Hardware Microphone Killswitch (`/mute`, `m`)**: Disables voice capture at the driver level for total acoustic privacy.
