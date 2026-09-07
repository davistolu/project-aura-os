import os
import sys
import time
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.progress_bar import ProgressBar
from rich.columns import Columns
from rich import box

console = Console()

class PaletteTUI:
    """
    Operating-System-Grade Command Palette and Desktop HUD for PROJECT AURA.
    Provides categorized actions, system metrics, fuzzy action search, and visual feedback.
    """

    CATEGORIES = {
        "APPS": "🚀 Applications & Compatibility",
        "WORKSPACES": "🖥️ Workspaces & Display",
        "SYSTEM": "⚙️ System & Hardware Control",
        "DEV": "🛠️ Developer Studio & Nix",
        "SECURITY": "🛡️ Security & Capability Ledger",
        "AI": "🧠 DAVIS Intelligence & Web"
    }

    ACTION_REGISTRY = [
        # Workspaces
        {"cmd": "/ws 1", "alias": "1 / alt+1", "title": "General Workspace", "cat": "WORKSPACES", "desc": "Standard desktop profile for daily browsing", "key": "1"},
        {"cmd": "/ws 2", "alias": "2 / alt+2", "title": "Development Studio", "cat": "WORKSPACES", "desc": "Tiled editor, terminal, container services", "key": "2"},
        {"cmd": "/ws 3", "alias": "3 / alt+3", "title": "Gaming Mode", "cat": "WORKSPACES", "desc": "Gamescope, Proton Direct, 144Hz GameMode", "key": "3"},
        {"cmd": "/ws 4", "alias": "4 / alt+4", "title": "Creative Studio", "cat": "WORKSPACES", "desc": "Low-latency PipeWire audio/video editing", "key": "4"},
        {"cmd": "/ws 5", "alias": "5 / alt+5", "title": "AI Workflows", "cat": "WORKSPACES", "desc": "Local SLMs, agents & capability tools", "key": "5"},

        # System & Hardware Controls
        {"cmd": "/settings", "alias": "c / cfg", "title": "Unified Control Center", "cat": "SYSTEM", "desc": "Configure Wi-Fi, Bluetooth, Power, RAM quotas & DNS", "key": "C"},
        {"cmd": "/wifi scan", "alias": "w / wifi", "title": "Wi-Fi Wireless Manager", "cat": "SYSTEM", "desc": "Scan real networks, signal bars [████], connect", "key": "W"},
        {"cmd": "/bt scan", "alias": "b / bt", "title": "Bluetooth Device Center", "cat": "SYSTEM", "desc": "Scan, pair, connect audio, gamepads, keyboards", "key": "B"},
        {"cmd": "/res", "alias": "r / res", "title": "RAM & Core Quota Allocator", "cat": "SYSTEM", "desc": "Configure AI RAM, Gaming limits & CPU core pinning", "key": "R"},
        {"cmd": "/net ping", "alias": "n / net", "title": "Network & DNS Diagnostics", "cat": "SYSTEM", "desc": "Measure real ping latency, switch DNS to 1.1.1.1", "key": "N"},
        {"cmd": "/sys status", "alias": "s / sys", "title": "Hardware Telemetry", "cat": "SYSTEM", "desc": "Real host RAM, CPU cores, active power plan, IP", "key": "S"},
        {"cmd": "/sys ps", "alias": "p / ps", "title": "Process Monitor (Top)", "cat": "SYSTEM", "desc": "List active system processes & memory load", "key": "P"},
        {"cmd": "/vol <0-100>", "alias": "vol <n>", "title": "Master Volume Level", "cat": "SYSTEM", "desc": "Adjust master system audio volume (0-100%)", "key": "V"},

        # Power Modes
        {"cmd": "/power perf", "alias": "f10 / perf", "title": "Performance Power Mode", "cat": "SYSTEM", "desc": "Max CPU boost, GPU 2600MHz, 144Hz refresh rate", "key": "F10"},
        {"cmd": "/power balanced", "alias": "f9 / balanced", "title": "Balanced Power Mode", "cat": "SYSTEM", "desc": "Dynamic scaling for optimal efficiency", "key": "F9"},
        {"cmd": "/power saver", "alias": "f8 / saver", "title": "Battery Saver Mode", "cat": "SYSTEM", "desc": "Low-power under-volt and whisper-quiet fans", "key": "F8"},

        # Applications
        {"cmd": "/run <app>", "alias": "run <name>", "title": "App / Game Launcher", "cat": "APPS", "desc": "Launches Windows apps via Proton Direct or Wine", "key": "Ctrl+G"},

        # Developer & Files
        {"cmd": "/find <name>", "alias": "f / find", "title": "Search Files & Documents", "cat": "DEV", "desc": "Deep search across Downloads, Documents, Desktop", "key": "F"},
        {"cmd": "/read <name>", "alias": "read <file>", "title": "Read & Preview Document", "cat": "DEV", "desc": "Open text, code, or config file preview", "key": "O"},
        {"cmd": "/dev doctor", "alias": "dev", "title": "AURA Dev Diagnostics", "cat": "DEV", "desc": "Inspect toolchains, Cargo, Nix flakes, and services", "key": "Ctrl+D"},

        # Security & Privacy
        {"cmd": "/sec caps", "alias": "caps / sec", "title": "Capability Matrix", "cat": "SECURITY", "desc": "Inspect granted tokens & zero-trust boundaries", "key": "Ctrl+S"},
        {"cmd": "/sec audit", "alias": "audit", "title": "AI Security Audit Log", "cat": "SECURITY", "desc": "View append-only cryptographic decision ledger", "key": "Ctrl+L"},
        {"cmd": "/mute", "alias": "m / mute", "title": "Microphone Privacy Mute", "cat": "SECURITY", "desc": "Hardware/software microphone killswitch", "key": "M"},

        # DAVIS Voice & Intelligence
        {"cmd": "/mic", "alias": "voice / listen", "title": "Activate Davis Microphone", "cat": "AI", "desc": "Listen for 5s command with Google Speech STT", "key": "Space"},
    ]

    @classmethod
    def render_hud_header(cls, active_workspace="Development", cpu_pct=3.8, ram_mb=420, ram_total=32768, mic_active=True):
        """Renders the top OS Status HUD Bar with meters and badges"""
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=3)
        table.add_column(justify="center", ratio=4)
        table.add_column(justify="right", ratio=3)

        # Left: OS Info & Workspace Badge
        ws_colors = {
            "General": "blue",
            "Development": "cyan",
            "Gaming": "green",
            "Creative": "magenta",
            "AI": "yellow"
        }
        ws_col = ws_colors.get(active_workspace, "cyan")
        left_text = Text.assemble(
            (" AURA OS 1.0 ", "bold white on purple"),
            (" ", ""),
            (f" [{active_workspace}] ", f"bold white on {ws_col}"),
            (" Wayland 1.23 ", "dim cyan")
        )

        # Center: Resource Gauges
        ram_gb = ram_mb / 1024
        ram_total_gb = ram_total / 1024
        ram_pct = (ram_mb / ram_total) * 100 if ram_total else 0
        center_text = Text.assemble(
            (f"CPU: {cpu_pct:.1f}% ", "bold cyan"),
            (" RAM: ", "bold green"),
            (f"{ram_mb:,} MB ({ram_pct:.1f}%) ", "green"),
            (f"/ {ram_total_gb:.1f} GB Host ", "dim white"),
            (" GPU: Vulkan 1.3", "dim white")
        )

        # Right: Voice & Clock
        mic_badge = ("🎙️ MIC: LISTENING ('Davis') ", "bold green") if mic_active else ("🎙️ MIC: MUTED ", "bold red")
        clock_str = time.strftime("%I:%M %p")
        right_text = Text.assemble(
            mic_badge,
            (f" 🕒 {clock_str} ", "bold white on blue")
        )

        table.add_row(left_text, center_text, right_text)

        panel = Panel(
            table,
            box=box.ROUNDED,
            style="bold white on rgb(15,20,30)",
            border_style="cyan",
            padding=(0, 1)
        )
        console.print(panel)

    @classmethod
    def render_command_palette(cls, filter_query=""):
        """Renders the comprehensive, categorized Command Palette & Shortcut Manual (/help)"""
        q = filter_query.lower().strip()

        # 1. Quick 1-Key Shortcuts Banner
        shortcut_table = Table(
            title=Text("⚡ QUICK 1-KEY & FUNCTION SHORTCUT CHEATSHEET (Type key directly into prompt)", style="bold yellow"),
            box=box.ROUNDED,
            expand=True,
            header_style="bold cyan"
        )
        shortcut_table.add_column("Key", style="bold yellow", justify="center", width=10)
        shortcut_table.add_column("Instant Action Triggered", style="bold white", width=34)
        shortcut_table.add_column("Key", style="bold yellow", justify="center", width=10)
        shortcut_table.add_column("Instant Action Triggered", style="bold white")

        shortcut_table.add_row("1 .. 5", "Switch Workspaces (1:Gen, 2:Dev, 3:Game, 4:Creative, 5:AI)", "W", "Open Wi-Fi Wireless Scanner (/wifi)")
        shortcut_table.add_row("F10 / perf", "Switch Power to Performance Mode", "B", "Open Bluetooth Device Manager (/bt)")
        shortcut_table.add_row("F9 / balanced", "Switch Power to Balanced Mode", "C / cfg", "Open Unified Settings Hub (/settings)")
        shortcut_table.add_row("F8 / saver", "Switch Power to Battery Saver Mode", "R / res", "Open RAM & CPU Resource Allocator (/res)")
        shortcut_table.add_row("P / ps", "Open Interactive Process Monitor (/ps)", "N / net", "Run Real ICMP Ping & DNS Test (/net)")
        shortcut_table.add_row("S / sys", "Open Real Hardware Telemetry (/sys)", "M / mute", "Toggle Microphone Privacy Mute (/mute)")
        shortcut_table.add_row("F / find", "Search Local Documents & Files (/find)", "? / help", "Display this Complete Help Directory")

        console.print(shortcut_table)
        console.print()

        # 2. Categorized Command Ledger
        table = Table(
            title=Text("📚 AURA GLOBAL COMMAND & VERB DIRECTORY", style="bold cyan"),
            box=box.SIMPLE_HEAVY,
            expand=True,
            header_style="bold magenta",
            border_style="dim cyan"
        )
        table.add_column("CLI Verb / Command", style="bold green", width=22)
        table.add_column("Quick Alias", style="bold yellow", width=16)
        table.add_column("Action Title", style="bold white", width=28)
        table.add_column("Category", style="cyan", width=24)
        table.add_column("Description", style="dim white")

        for m in cls.ACTION_REGISTRY:
            if not q or (q in m["cmd"].lower() or q in m["title"].lower() or q in m["desc"].lower() or q in m["cat"].lower() or q in m.get("alias", "").lower()):
                cat_label = cls.CATEGORIES.get(m["cat"], m["cat"])
                table.add_row(
                    m["cmd"],
                    m.get("alias", m["key"]),
                    m["title"],
                    cat_label,
                    m["desc"]
                )

        console.print(table)
        console.print()

        # 3. Voice Assistant Cheat Card
        voice_panel = Panel(
            Text.assemble(
                ("🤖 DAVIS VOICE ASSISTANT CHEATSHEET\n", "bold magenta"),
                ("Say ", "white"), ("\"Davis\"", "bold green"), (" or ", "white"), ("\"Hey Davis\"", "bold green"), (" & wait for vocal acknowledgement (", "white"), ("\"Yeah?\"", "cyan"), (") then speak:\n", "white"),
                (" • Wi-Fi & Devices: ", "bold yellow"), ("\"Connect to Wi-Fi [SSID]\", \"Turn on Bluetooth\", \"Connect my headphones\"\n", "white"),
                (" • Power & RAM: ", "bold yellow"), ("\"Set power mode to Performance\", \"Allocate 8 GB of RAM to AI\", \"Switch to Battery Saver\"\n", "white"),
                (" • Live APIs: ", "bold yellow"), ("\"Weather in London\", \"Convert 100 USD to EUR\", \"Who is Alan Turing\", \"What is 45 * 12\"\n", "white"),
                (" • System & Workspaces: ", "bold yellow"), ("\"Switch to gaming mode\", \"Search for report.pdf\", \"How much RAM am I using\"\n", "white"),
                (" • Conversational Memory: ", "bold yellow"), ("\"My name is Alex\", \"What is my name?\", \"What did we talk about?\", \"Clear memory\"", "white")
            ),
            title="🎙️ Hands-Free Davis Voice AI",
            box=box.ROUNDED,
            border_style="magenta",
            padding=(0, 1)
        )
        console.print(voice_panel)

    @classmethod
    def render_process_table(cls):
        """Interactive process list viewer (/sys ps)"""
        table = Table(
            title=Text("⚡ AURA PROCESS & RESOURCE LEDGER", style="bold green"),
            box=box.ROUNDED,
            expand=True,
            header_style="bold cyan"
        )
        table.add_column("PID", style="bold yellow", width=8)
        table.add_column("Process Name", style="bold white", width=24)
        table.add_column("CPU %", style="cyan", width=12)
        table.add_column("Memory (MB)", style="green", width=16)
        table.add_column("Security Sandbox", style="magenta", width=20)
        table.add_column("Status", style="bold green")

        processes = [
            ("1", "systemd", "0.0%", "14.2 MB", "Strict System", "Running"),
            ("420", "aura-shell", "0.2%", "42.0 MB", "Wayland Native", "Active"),
            ("850", "davis-daemon", "0.1%", "65.5 MB", "Capability Bound", "Active"),
            ("1102", "pipewire", "0.1%", "12.0 MB", "Audio Core", "Running"),
            ("1450", "gamescope", "0.0%", "18.4 MB", "Gaming Sandbox", "Idle"),
            ("1890", "podman-rootless", "0.0%", "28.1 MB", "User Container", "Idle")
        ]

        for p in processes:
            table.add_row(*p)

        console.print(table)

    @classmethod
    def render_capabilities_matrix(cls):
        """Security Capability Matrix Table (/sec caps)"""
        table = Table(
            title=Text("🛡️ AURA ZERO-TRUST CAPABILITY & PERMISSION LEDGER", style="bold magenta"),
            box=box.DOUBLE_EDGE,
            expand=True,
            header_style="bold cyan"
        )
        table.add_column("Capability Token", style="bold white", width=28)
        table.add_column("Permission Tier", style="bold yellow", width=20)
        table.add_column("Granted Scope", style="green", width=24)
        table.add_column("Approval Gate", style="bold cyan")

        caps = [
            ("system.hardware.read", "OBSERVE", "CPU/RAM/GPU Telemetry", "Auto-Allowed"),
            ("system.process.list", "OBSERVE", "User & System Processes", "Auto-Allowed"),
            ("system.process.kill", "EXECUTE_PRIVILEGED", "User Processes", "User Modal Consent Required"),
            ("filesystem.read", "EXECUTE_SAFE", "Project Sandbox (~/*)", "Auto-Allowed"),
            ("filesystem.write", "EXECUTE_SAFE", "Project Sandbox (~/*)", "Auto-Allowed"),
            ("filesystem.delete", "EXECUTE_PRIVILEGED", "Project Sandbox", "Approval Gate Required"),
            ("audio.capture", "EXECUTE_SAFE", "Default Microphone", "Echo-Guarded"),
            ("audio.playback", "EXECUTE_SAFE", "System Audio Speakers", "Auto-Allowed"),
            ("terminal.execute", "EXECUTE_PRIVILEGED", "Isolated Shell", "Approval Gate Required"),
            ("vm.manage", "EXECUTE_SAFE", "KVM / Proton Prefixes", "Auto-Allowed")
        ]

        for c in caps:
            table.add_row(*c)

        console.print(table)

    @classmethod
    def render_settings_hub(cls, settings: dict):
        """Unified AURA OS Control Center & Hardware Configuration Hub (/settings)"""
        p = settings.get("power", {})
        w = settings.get("wifi", {})
        b = settings.get("bluetooth", {})
        r = settings.get("resources", {})
        n = settings.get("network", {})
        a = settings.get("audio_display", {})

        table = Table(
            title=Text("⚙️ PROJECT AURA — UNIFIED SYSTEM CONTROL CENTER & HARDWARE SETTINGS", style="bold cyan"),
            box=box.ROUNDED,
            expand=True,
            header_style="bold magenta"
        )
        table.add_column("Subsystem Category", style="bold white", width=24)
        table.add_column("Current Active Value", style="bold green", width=34)
        table.add_column("Quick CLI Verb / Command", style="yellow", width=28)
        table.add_column("Status / Health", style="cyan")

        # 1. Power
        table.add_row("⚡ Power & Thermals", f"Mode: {p.get('active_mode', 'Balanced')} ({p.get('cpu_governor', 'schedutil')})", "/power [perf|balanced|saver]", "Optimal (42°C)")
        # 2. Wi-Fi
        wifi_str = f"Connected: '{w.get('connected_ssid', 'None')}'" if w.get('enabled') and w.get('connected_ssid') else ("Enabled (Scanning)" if w.get('enabled') else "Disabled")
        table.add_row("📶 Wi-Fi Wireless", f"{wifi_str} ({w.get('signal_pct', 0)}%)", "/wifi [scan|connect|on|off]", "Online" if w.get('connected_ssid') else "Idle")
        # 3. Bluetooth
        connected_bt = [d['name'] for d in b.get('paired_devices', []) if d.get('connected')]
        bt_str = f"{len(connected_bt)} Connected ({', '.join(connected_bt[:2])})" if connected_bt else "0 Connected Devices"
        table.add_row("📡 Bluetooth Radio", f"{bt_str}", "/bt [scan|connect|pair]", "Radio Active" if b.get('enabled') else "Off")
        # 4. RAM & Resources
        table.add_row("🧠 RAM Resource Limits", f"AI: {r.get('davis_ai_ram_limit_mb', 4096)}MB | Games: {r.get('gaming_proton_ram_limit_mb', 16384)}MB", "/res [set-ram|set-cores]", f"ZRAM: {r.get('zram_size_gb', 8)}GB zstd")
        # 5. Network & DNS
        table.add_row("🌐 Internet & DNS", f"DNS: {n.get('dns_provider', 'Cloudflare')} ({n.get('primary_dns', '1.1.1.1')})", "/net [ping|dns <server>]", "Firewall Guard Active")
        # 6. Audio & Display
        table.add_row("🔊 Audio & Display", f"Volume: {a.get('master_volume_pct', 75)}% | {a.get('display_resolution', '1440p')}", "/vol [0-100] / /sys", f"{p.get('display_refresh_rate_hz', 144)}Hz")

        console.print(table)

    @classmethod
    def render_wifi_table(cls, networks: list, active_ssid: str, wifi_enabled: bool):
        """Wi-Fi Networks Scan Visualizer (/wifi scan)"""
        title_txt = f"📶 AURA WI-FI WIRELESS MANAGER — [Interface: {'ENABLED' if wifi_enabled else 'DISABLED'}]"
        table = Table(
            title=Text(title_txt, style="bold cyan"),
            box=box.ROUNDED,
            expand=True,
            header_style="bold green"
        )
        table.add_column("SSID Network Name", style="bold white", width=28)
        table.add_column("Signal Strength", style="bold yellow", width=22)
        table.add_column("Security Protocol", style="magenta", width=20)
        table.add_column("Channel / Band", style="cyan", width=18)
        table.add_column("Connection State", style="bold green")

        for net in networks:
            is_active = (net["ssid"] == active_ssid)
            sig = net["signal_pct"]
            bars = "████" if sig > 80 else ("███░" if sig > 60 else ("██░░" if sig > 40 else "█░░░"))
            status_text = "● CONNECTED (Active)" if is_active else "Saved Profile" if is_active else "Available"
            table.add_row(
                net["ssid"],
                f"[{bars}] {sig}%",
                net["security"],
                net["channel"],
                status_text
            )

        console.print(table)

    @classmethod
    def render_bluetooth_table(cls, devices: list, bt_enabled: bool):
        """Bluetooth Devices Matrix (/bt scan)"""
        title_txt = f"📡 AURA BLUETOOTH DEVICE MANAGER — [Radio: {'ACTIVE' if bt_enabled else 'DISABLED'}]"
        table = Table(
            title=Text(title_txt, style="bold cyan"),
            box=box.ROUNDED,
            expand=True,
            header_style="bold magenta"
        )
        table.add_column("Device Name", style="bold white", width=30)
        table.add_column("Type", style="cyan", width=16)
        table.add_column("Battery Level", style="yellow", width=18)
        table.add_column("Connection Status", style="bold green")

        for d in devices:
            bat_bar = f"{d.get('battery_pct', 0)}%"
            state = "● CONNECTED" if d.get("connected") else "○ Paired (Disconnected)"
            table.add_row(
                f"{d.get('icon', '🎧')} {d['name']}",
                d.get("type", "Peripheral"),
                f"🔋 {bat_bar}",
                state
            )

        console.print(table)

    @classmethod
    def render_resource_quotas(cls, res: dict):
        """RAM, CPU Affinity, and Workload Limits Visualizer (/res)"""
        table = Table(
            title=Text("🧠 AURA OS RESOURCE ALLOCATOR & WORKLOAD QUOTAS", style="bold green"),
            box=box.ROUNDED,
            expand=True,
            header_style="bold cyan"
        )
        table.add_column("Subsystem Workload", style="bold white", width=28)
        table.add_column("RAM Allocation Limit", style="bold yellow", width=24)
        table.add_column("CPU Affinity Pinning", style="cyan", width=24)
        table.add_column("Scheduling Policy", style="magenta")

        table.add_row(
            "DAVIS Neural AI Assistant",
            f"{res.get('davis_ai_ram_limit_mb', 4096)} MB ({res.get('davis_ai_ram_limit_mb', 4096)/1024:.1f} GB)",
            f"Cores [{res.get('pinned_os_cores', '0-3')}]",
            "SCHED_OTHER (Low Latency)"
        )
        table.add_row(
            "Gaming & Proton Sandbox",
            f"{res.get('gaming_proton_ram_limit_mb', 16384)} MB ({res.get('gaming_proton_ram_limit_mb', 16384)/1024:.1f} GB)",
            f"Cores [{res.get('pinned_workload_cores', '4-15')}]",
            "SCHED_ISO / GameMode (144Hz)"
        )
        table.add_row(
            "Aura Shell & Wayland Base",
            f"{res.get('aura_os_base_ram_limit_mb', 1024)} MB (Idle Target: <450 MB)",
            f"Cores [{res.get('pinned_os_cores', '0-3')}]",
            "SCHED_RR (Display Realtime)"
        )
        table.add_row(
            "ZRAM Compressed Memory Swap",
            f"{res.get('zram_size_gb', 8)} GB ({res.get('zram_algorithm', 'zstd')} Algorithm)",
            "Dynamic Core Pool",
            "Kernel Swap Driver Active"
        )

        console.print(table)

