# PROJECT AURA — Command Line & Verbs Reference

A comprehensive reference for all Command Palette verbs, syntax, quick hotkeys, and behavioral options in **PROJECT AURA**.

---

## Command Reference Index

| Command | Category | Short Alias | Purpose |
| :--- | :--- | :--- | :--- |
| [`/help`](#help) | Manual | `?`, `h`, `manual` | Displays the global command palette and shortcut cheatsheet. |
| [`/ws`](#ws) | Workspaces | `1`, `2`, `3`, `4`, `5` | Switches the active Wayland workspace profile. |
| [`/settings`](#settings) | System | `c`, `cfg`, `config` | Opens the Unified System Control Center. |
| [`/wifi`](#wifi) | Hardware | `w`, `wifi` | Real Wi-Fi network scanner, connection, and interface control. |
| [`/bt`](#bt) | Hardware | `b`, `bt`, `bluetooth` | Real Bluetooth device manager and battery telemetry. |
| [`/power`](#power) | Hardware | `f8`, `f9`, `f10`, `perf` | Switches real Windows/Linux power schemes (`powercfg`). |
| [`/res`](#res) | Hardware | `r`, `res`, `ram` | Configures RAM resource limits, CPU affinity, and ZRAM. |
| [`/net`](#net) | Network | `n`, `net`, `ping` | Runs live ICMP latency ping tests and switches DNS resolvers. |
| [`/sys`](#sys) | System | `s`, `sys`, `status` | Real hardware telemetry snapshot and Process Monitor (`/ps`). |
| [`/vol`](#vol) | Audio | `vol <n>` | Sets system master audio volume (0–100%). |
| [`/run`](#run) | Apps | `run <app>` | Launches Windows games and applications via Proton / Wine. |
| [`/find`](#find) | Files | `f`, `find <query>` | Deep file search across Documents, Downloads, and Workspace. |
| [`/read`](#read) | Files | `read <file>` | Reads and previews text, markdown, or source code files. |
| [`/sec`](#sec) | Security | `sec`, `caps`, `audit` | Inspects Capability Matrix and structured AI audit trail. |
| [`/mic`](#mic) | Voice | `v`, `voice`, `listen` | Manually triggers the microphone for a 5-second voice command. |
| [`/mute`](#mute) | Privacy | `m`, `mute` | Toggles microphone hardware/software privacy mute. |

---

## Detailed Command Specifications

### `/help`
- **Aliases**: `?`, `h`, `manual`, `palette`
- **Description**: Renders the complete categorized command manual, 1-key hotkey cheat sheet, and DAVIS voice query syntax.
- **Example**:
  ```bash
  AURA » /help
  AURA » ?
  ```

---

### `/ws`
- **Syntax**: `/ws <id|name>`
- **Aliases**: `1`, `2`, `3`, `4`, `5`, `alt+1`..`alt+5`
- **Arguments**:
  - `1` or `general`: Everyday multitasking profile.
  - `2` or `dev`: Development Studio workspace.
  - `3` or `gaming`: Gamescope 144Hz Proton profile.
  - `4` or `creative`: PipeWire audio/video studio.
  - `5` or `ai`: Local SLM and AI agent workflows.
- **Example**:
  ```bash
  AURA » /ws 3
  AURA » 2
  ```

---

### `/settings`
- **Aliases**: `c`, `cfg`, `config`
- **Description**: Displays the unified system control center showing live status of Wi-Fi, Bluetooth, Power plan, RAM allocations, DNS, and Volume.
- **Example**:
  ```bash
  AURA » /settings
  AURA » c
  ```

---

### `/wifi`
- **Syntax**: `/wifi [scan | connect <ssid> | disconnect | on | off | status]`
- **Aliases**: `w`, `wifi`
- **Subcommands**:
  - `scan` (Default): Runs real `netsh wlan` scan and displays nearby SSIDs, signal strength bars, and security protocols.
  - `connect <ssid>`: Connects to a saved or broadcasted network profile.
  - `disconnect`: Disconnects from current Wi-Fi network.
  - `on` / `off`: Toggles interface state.
- **Example**:
  ```bash
  AURA » /wifi scan
  AURA » w
  AURA » /wifi connect Office-5G
  ```

---

### `/bt`
- **Syntax**: `/bt [scan | connect <device> | disconnect [device] | on | off]`
- **Aliases**: `b`, `bt`, `bluetooth`
- **Description**: Queries real Bluetooth peripherals (headphones, gamepads, keyboards) via Windows PnP and displays connection and battery levels.
- **Example**:
  ```bash
  AURA » /bt scan
  AURA » b
  AURA » /bt connect Sony WH-1000XM5
  ```

---

### `/power`
- **Syntax**: `/power [perf | balanced | saver | boost]`
- **Aliases**: `f8` (Saver), `f9` (Balanced), `f10` (Performance), `perf`, `saver`, `balanced`
- **Description**: Switches the real Windows operating power scheme via `powercfg /setactive`.
- **Example**:
  ```bash
  AURA » /power perf
  AURA » f10
  ```

---

### `/res`
- **Syntax**: `/res [status | set-ram <target> <mb> | set-cores <os_cores> <work_cores> | set-zram <gb>]`
- **Aliases**: `r`, `res`, `ram`, `resources`
- **Subcommands**:
  - `status` (Default): Renders RAM allocation matrix, CPU core affinity map, and ZRAM size.
  - `set-ram <ai|game|os> <mb>`: Allocates memory quotas.
  - `set-cores <os> <work>`: Configures CPU core affinity pinning.
  - `set-zram <gb>`: Configures ZRAM compressed memory swap.
- **Example**:
  ```bash
  AURA » /res
  AURA » /res set-ram ai 8192
  AURA » /res set-cores 0-3 4-15
  ```

---

### `/net`
- **Syntax**: `/net [ping [host] | dns <provider> | status]`
- **Aliases**: `n`, `net`, `ping`
- **Subcommands**:
  - `ping [host]`: Sends live ICMP ping packet (Default: `1.1.1.1`) and reports latency in milliseconds.
  - `dns <cloudflare|google|quad9|custom>`: Changes DNS server configuration.
  - `status`: Displays current IP address, Gateway, Subnet Mask, and Firewall zone.
- **Example**:
  ```bash
  AURA » /net ping
  AURA » n
  AURA » /net dns cloudflare
  ```

---

### `/sys`
- **Syntax**: `/sys [status | ps]`
- **Aliases**: `s`, `sys`, `status` (for `/sys status`); `p`, `ps`, `top` (for `/sys ps`)
- **Subcommands**:
  - `status`: Displays physical RAM, CPU cores, active power plan, and real local IP.
  - `ps`: Interactive Process Monitor showing active processes, PID, memory, and security sandbox.
- **Example**:
  ```bash
  AURA » /sys status
  AURA » s
  AURA » /sys ps
  AURA » p
  ```

---

### `/vol`
- **Syntax**: `/vol <level (0-100)>`
- **Description**: Sets the master audio output volume percentage.
- **Example**:
  ```bash
  AURA » /vol 80
  AURA » /vol 0
  ```

---

### `/find` & `/read`
- **Syntax**:
  - `/find <query>`: Searches documents and downloads for matching filenames.
  - `/read <filename>`: Opens a formatted text/code preview of the document.
- **Aliases**: `f` (for `/find`)
- **Example**:
  ```bash
  AURA » /find report.pdf
  AURA » /read notes.txt
  ```

---

### `/sec`
- **Syntax**: `/sec [caps | audit]`
- **Aliases**: `caps`, `security` (for `/sec caps`); `audit`, `/audit` (for `/sec audit`)
- **Description**:
  - `caps`: Displays the zero-trust capability permission matrix.
  - `audit`: Displays the tamper-evident structured AI audit decision log.
- **Example**:
  ```bash
  AURA » /sec caps
  AURA » /sec audit
  ```
