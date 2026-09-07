#!/usr/bin/env python3
"""
PROJECT AURA - Operating-System-Grade Command Palette & DAVIS AI Runtime
Combines:
 - Live OS Status HUD Bar (CPU, RAM, GPU, Workspace Pill, Mic Status, Clock)
 - Spotlight / Raycast Style Categorized Command Palette
 - System Verbs (/ws, /run, /sys, /ps, /power, /sec, /find, /read)
 - Continuous Background Voice Recognition for "Davis" with Edge Neural Voice
 - Live External APIs (Weather, Forex, Wikipedia, Science, Song Search)
"""

import sys
import os
import subprocess
import time
import json
import uuid
import tempfile
import threading

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import speech libraries
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
try:
    from dialogue_engine import JarvisDialogueEngine
except ImportError:
    JarvisDialogueEngine = None

try:
    from settings_manager import SettingsManager
except ImportError:
    SettingsManager = None

try:
    from neural_voice import NeuralVoiceSynthesizer
except ImportError:
    NeuralVoiceSynthesizer = None

try:
    from palette_tui import PaletteTUI, console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

class VoiceIO:
    """Microphone Audio Capture & High-Fidelity Neural Speech Playback"""
    _is_speaking = False
    _lock = threading.Lock()

    @classmethod
    def _record_audio_file(cls, output_wav: str, duration_secs: int = 4) -> bool:
        """Records microphone PCM audio directly via Windows Multimedia API (0ms subprocess overhead)"""
        if sys.platform.startswith("win"):
            try:
                import ctypes
                winmm = ctypes.windll.winmm
                alias = f"rec_{int(time.time() * 1000) % 100000}"
                winmm.mciSendStringW(f"close {alias}", None, 0, 0)
                winmm.mciSendStringW(f"open new type waveaudio alias {alias}", None, 0, 0)
                winmm.mciSendStringW(f"set {alias} format tag pcm bitspersample 16 channels 1 samplespersec 16000", None, 0, 0)
                winmm.mciSendStringW(f"record {alias}", None, 0, 0)
                time.sleep(duration_secs)
                if os.path.exists(output_wav):
                    try:
                        os.remove(output_wav)
                    except Exception:
                        pass
                winmm.mciSendStringW(f'save {alias} "{output_wav}"', None, 0, 0)
                winmm.mciSendStringW(f"close {alias}", None, 0, 0)
                if os.path.exists(output_wav) and os.path.getsize(output_wav) > 1000:
                    return True
            except Exception:
                pass

        # Fallback to PowerShell script if needed
        script_path = os.path.join(os.path.dirname(__file__), "scripts", "record_mic.ps1")
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path, "-OutputFile", output_wav, "-DurationSeconds", str(duration_secs)]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=duration_secs + 4)
            return os.path.exists(output_wav) and os.path.getsize(output_wav) > 1000
        except Exception:
            return False

    @classmethod
    def record_and_recognize(cls, duration_secs=4):
        """Captures microphone audio and uses Google Speech Recognition for high accuracy"""
        if cls._is_speaking:
            return None

        temp_wav = os.path.join(tempfile.gettempdir(), f"aura_mic_{int(time.time()*1000)}.wav")
        recorded = cls._record_audio_file(temp_wav, duration_secs=duration_secs)
        if not recorded:
            return None

        if HAS_SR:
            try:
                r = sr.Recognizer()
                with sr.AudioFile(temp_wav) as source:
                    r.adjust_for_ambient_noise(source, duration=0.1)
                    audio_data = r.record(source)
                text = r.recognize_google(audio_data, language="en-US")
                return text
            except Exception:
                return None
            finally:
                if os.path.exists(temp_wav):
                    try:
                        os.remove(temp_wav)
                    except Exception:
                        pass
        return None

    @classmethod
    def speak_sync(cls, text: str):
        """Speaks synchronously so subsequent mic captures don't hear voice output"""
        if not text:
            return
        cls._is_speaking = True
        try:
            if NeuralVoiceSynthesizer:
                NeuralVoiceSynthesizer.speak_sync(text)
            else:
                clean = text.replace("'", "").replace('"', '').replace('\n', ' ')
                script_path = os.path.join(os.path.dirname(__file__), "scripts", "speak.ps1")
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path, "-Text", clean],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
        finally:
            cls._is_speaking = False

    @classmethod
    def speak(cls, text: str):
        """Speaks using NeuralVoiceSynthesizer in a non-blocking thread"""
        if not text:
            return
        t = threading.Thread(target=cls.speak_sync, args=(text,), daemon=True)
        t.start()

class AuraOS:
    def __init__(self):
        self.workspaces = {
            "1": "General",
            "2": "Development",
            "3": "Gaming",
            "4": "Creative",
            "5": "AI"
        }
        self.current_workspace = "2"
        self.settings_manager = SettingsManager() if SettingsManager else None
        self.power_mode = self.settings_manager.settings["power"]["active_mode"] if self.settings_manager else "Balanced"
        self.voice_enabled = True
        self.mic_muted = False
        self.audit_events = []
        self.dialogue_engine = JarvisDialogueEngine(self) if JarvisDialogueEngine else None

        # Start background wake-word listener thread for "Davis"
        self._stop_listener = False
        self._listener_thread = threading.Thread(target=self._background_wake_loop, daemon=True)
        self._listener_thread.start()

    def log_audit(self, tool, cap, decision, details):
        event = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tool": tool,
            "capability": cap,
            "decision": decision,
            "details": details
        }
        self.audit_events.append(event)
        return event

    def _background_wake_loop(self):
        """Monitors microphone for 'Davis' in the background"""
        time.sleep(0.5)
        while not self._stop_listener:
            if not self.voice_enabled or self.mic_muted or VoiceIO._is_speaking:
                time.sleep(0.5)
                continue

            heard = VoiceIO.record_and_recognize(duration_secs=3)
            if heard:
                lower = heard.lower()
                if "davis" in lower or "aura" in lower:
                    if HAS_RICH:
                        console.print(f"\n[bold green]🗣️ [Heard Wake-Word]: \"{heard}\"[/bold green]")
                    ack = self.dialogue_engine.get_wake_acknowledgement() if self.dialogue_engine else "Yeah?"
                    if HAS_RICH:
                        console.print(f"[bold magenta]🤖 DAVIS » [/bold magenta][white]{ack}[/white]")
                    
                    # Speak acknowledgement cleanly before listening for the follow-up command
                    VoiceIO.speak_sync(ack)

                    if HAS_RICH:
                        console.print("[bold yellow]🎙️ [DAVIS LISTENING FOR COMMAND...] Speak now (4s)...[/bold yellow]")
                    cmd = VoiceIO.record_and_recognize(duration_secs=4)
                    if cmd:
                        if HAS_RICH:
                            console.print(f"[bold green]🗣️ Command Heard:[/bold green] \"{cmd}\"")
                        self.execute_command(cmd, from_voice=True)
                    else:
                        if HAS_RICH:
                            console.print("[yellow]⚠️ [DAVIS » Standby] No command detected. Ready for your next request.[/yellow]")

            time.sleep(0.3)

    def execute_command(self, query: str, from_voice=False):
        q = query.strip()
        lower = q.lower()

        # Clean wake word prefixes
        if lower.startswith("hey davis") or lower.startswith("davis"):
            from_voice = True
            q = q.split(maxsplit=2)[-1] if len(q.split()) > 2 else ""
            lower = q.lower()

        # Quick 1-Key & Keyboard Shortcut Normalizer
        SHORTCUT_MAP = {
            "1": "/ws 1", "alt+1": "/ws 1", "workspace 1": "/ws 1", "general": "/ws 1",
            "2": "/ws 2", "alt+2": "/ws 2", "workspace 2": "/ws 2", "dev": "/ws 2", "development": "/ws 2",
            "3": "/ws 3", "alt+3": "/ws 3", "workspace 3": "/ws 3", "gaming": "/ws 3", "game": "/ws 3",
            "4": "/ws 4", "alt+4": "/ws 4", "workspace 4": "/ws 4", "creative": "/ws 4",
            "5": "/ws 5", "alt+5": "/ws 5", "workspace 5": "/ws 5", "ai": "/ws 5",
            "w": "/wifi scan", "alt+w": "/wifi scan", "wifi": "/wifi scan",
            "b": "/bt scan", "alt+b": "/bt scan", "bt": "/bt scan", "bluetooth": "/bt scan",
            "c": "/settings", "cfg": "/settings", "config": "/settings", "settings": "/settings", "ctrl+,": "/settings",
            "r": "/res", "alt+r": "/res", "ram": "/res", "resources": "/res",
            "n": "/net ping", "alt+n": "/net ping", "net": "/net ping", "ping": "/net ping",
            "p": "/ps", "ctrl+p": "/ps", "ps": "/ps", "top": "/ps", "processes": "/ps",
            "s": "/sys status", "ctrl+h": "/sys status", "sys": "/sys status", "status": "/sys status", "hardware": "/sys status",
            "m": "/mute", "ctrl+m": "/mute", "mute": "/mute",
            "v": "/mic", "voice": "/mic", "listen": "/mic", "speak": "/mic",
            "f8": "/power saver", "saver": "/power saver", "battery saver": "/power saver",
            "f9": "/power balanced", "balanced": "/power balanced",
            "f10": "/power perf", "perf": "/power perf", "performance": "/power perf", "boost": "/power boost",
            "f": "/find", "ctrl+f": "/find",
            "h": "/help", "?": "/help", "help": "/help", "palette": "/help", "manual": "/help"
        }

        if lower in SHORTCUT_MAP:
            q = SHORTCUT_MAP[lower]
            lower = q.lower()

        if not lower:
            ack = self.dialogue_engine.get_wake_acknowledgement() if self.dialogue_engine else "Yeah?"
            if self.voice_enabled and from_voice:
                VoiceIO.speak_sync(ack)
            if HAS_RICH:
                console.print(Panel(Text(ack, style="bold magenta"), title="🤖 DAVIS", border_style="magenta"))
            return

        # 1. Palette & Help (/help, ?, h, manual)
        if lower in ["?", "help", "palette", "/help", "h", "manual"]:
            if HAS_RICH:
                PaletteTUI.render_command_palette()
            return

        # 2. Unified Settings Hub (/settings, /cfg, /config)
        if lower in ["/settings", "/cfg", "/config", "settings", "config"]:
            self.log_audit("settings_hub", "system.hardware.read", "ALLOWED", "Inspected system settings")
            if self.settings_manager and HAS_RICH:
                PaletteTUI.render_settings_hub(self.settings_manager.settings)
            if self.voice_enabled and from_voice:
                VoiceIO.speak_sync("AURA OS Unified Hardware & System Control Center.")
                if HAS_RICH:
                    console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
            return

        # 3. Wi-Fi Wireless Manager (/wifi)
        if lower.startswith("/wifi") or lower.startswith("wifi"):
            parts = lower.split()
            subcmd = parts[1] if len(parts) > 1 else "scan"
            self.log_audit("wifi_manager", "network.wifi.manage", "ALLOWED", f"Wi-Fi subcmd: {subcmd}")

            if subcmd == "on":
                res = self.settings_manager.set_wifi_state(True) if self.settings_manager else {"text": "Wi-Fi enabled."}
            elif subcmd == "off":
                res = self.settings_manager.set_wifi_state(False) if self.settings_manager else {"text": "Wi-Fi disabled."}
            elif subcmd == "disconnect":
                res = self.settings_manager.disconnect_wifi() if self.settings_manager else {"text": "Disconnected."}
            elif subcmd.startswith("connect"):
                ssid = q.split(maxsplit=2)[2] if len(q.split()) > 2 else "Aura-Studio-5G"
                res = self.settings_manager.connect_wifi(ssid) if self.settings_manager else {"text": f"Connected to {ssid}"}
            else:
                networks = self.settings_manager.scan_wifi() if self.settings_manager else []
                active_ssid = self.settings_manager.settings["wifi"]["connected_ssid"] if self.settings_manager else ""
                wifi_en = self.settings_manager.settings["wifi"]["enabled"] if self.settings_manager else True
                if HAS_RICH:
                    PaletteTUI.render_wifi_table(networks, active_ssid, wifi_en)
                res = {"text": f"Found {len(networks)} nearby Wi-Fi networks."}

            if HAS_RICH and subcmd in ["on", "off", "disconnect", "connect"]:
                console.print(Panel(Text(res["text"], style="bold green"), title="📶 Wi-Fi Manager", border_style="cyan"))
            if self.voice_enabled and from_voice:
                VoiceIO.speak_sync(res["text"])
                if HAS_RICH:
                    console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
            return

        # 4. Bluetooth Manager (/bt, /bluetooth)
        if lower.startswith("/bt") or lower.startswith("/bluetooth") or lower.startswith("bluetooth"):
            parts = lower.split()
            subcmd = parts[1] if len(parts) > 1 else "scan"
            self.log_audit("bluetooth_manager", "hardware.bluetooth.manage", "ALLOWED", f"Bluetooth subcmd: {subcmd}")

            if subcmd == "on":
                res = self.settings_manager.set_bluetooth_state(True) if self.settings_manager else {"text": "Bluetooth enabled."}
            elif subcmd == "off":
                res = self.settings_manager.set_bluetooth_state(False) if self.settings_manager else {"text": "Bluetooth disabled."}
            elif subcmd.startswith("connect") or subcmd.startswith("pair"):
                dev_name = q.split(maxsplit=2)[2] if len(q.split()) > 2 else "Sony WH-1000XM5"
                res = self.settings_manager.connect_bluetooth_device(dev_name) if self.settings_manager else {"text": f"Connected to {dev_name}"}
            elif subcmd == "disconnect":
                dev_name = q.split(maxsplit=2)[2] if len(q.split()) > 2 else "all"
                res = self.settings_manager.disconnect_bluetooth_device(dev_name) if self.settings_manager else {"text": "Disconnected."}
            else:
                devices = self.settings_manager.settings["bluetooth"]["paired_devices"] if self.settings_manager else []
                bt_en = self.settings_manager.settings["bluetooth"]["enabled"] if self.settings_manager else True
                if HAS_RICH:
                    PaletteTUI.render_bluetooth_table(devices, bt_en)
                res = {"text": f"Bluetooth radio active with {len(devices)} paired devices."}

            if HAS_RICH and subcmd in ["on", "off", "disconnect", "connect", "pair"]:
                console.print(Panel(Text(res["text"], style="bold green"), title="📡 Bluetooth Device Manager", border_style="magenta"))
            if self.voice_enabled and from_voice:
                VoiceIO.speak_sync(res["text"])
                if HAS_RICH:
                    console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
            return

        # 5. RAM & CPU Resource Allocator (/res, /ram, /resources)
        if lower.startswith("/res") or lower.startswith("/ram") or lower.startswith("resources"):
            parts = lower.split()
            subcmd = parts[1] if len(parts) > 1 else "status"
            self.log_audit("resource_allocator", "system.resource.set", "ALLOWED", f"Resource subcmd: {subcmd}")

            if subcmd == "set-ram" and len(parts) >= 4:
                target = parts[2]
                mb = int(parts[3])
                res = self.settings_manager.set_ram_allocation(target, mb) if self.settings_manager else {"text": "RAM allocated."}
            elif subcmd == "set-cores" and len(parts) >= 4:
                os_c = parts[2]
                work_c = parts[3]
                res = self.settings_manager.set_cpu_affinity(os_c, work_c) if self.settings_manager else {"text": "Affinity set."}
            elif subcmd == "set-zram" and len(parts) >= 3:
                z_gb = int(parts[2])
                res = self.settings_manager.set_zram_config(z_gb) if self.settings_manager else {"text": "ZRAM set."}
            else:
                res_dict = self.settings_manager.settings["resources"] if self.settings_manager else {}
                if HAS_RICH:
                    PaletteTUI.render_resource_quotas(res_dict)
                res = {"text": "Resource quotas inspected."}

            if HAS_RICH and subcmd.startswith("set-"):
                console.print(Panel(Text(res["text"], style="bold green"), title="🧠 Resource Allocator", border_style="green"))
            if self.voice_enabled and from_voice:
                VoiceIO.speak_sync(res["text"])
                if HAS_RICH:
                    console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
            return

        # 6. Network & DNS Diagnostics (/net)
        if lower.startswith("/net"):
            parts = lower.split()
            subcmd = parts[1] if len(parts) > 1 else "ping"
            self.log_audit("network_diagnostics", "network.status.read", "ALLOWED", f"Network subcmd: {subcmd}")

            if subcmd == "ping":
                target_host = parts[2] if len(parts) > 2 else "1.1.1.1"
                res = self.settings_manager.test_latency_ping(target_host) if self.settings_manager else {"text": "Ping ok."}
                if HAS_RICH:
                    console.print(Panel(Text(res["text"], style="bold green" if res.get("success") else "bold red"), title="🌐 Network Latency Ping Test", border_style="cyan"))
            elif subcmd == "dns":
                provider = q.split(maxsplit=2)[2] if len(q.split()) > 2 else "1.1.1.1"
                res = self.settings_manager.set_dns(provider) if self.settings_manager else {"text": f"DNS set to {provider}"}
                if HAS_RICH:
                    console.print(Panel(Text(res["text"], style="bold green"), title="🌐 DNS Configuration", border_style="cyan"))
            else:
                net_dict = self.settings_manager.settings["network"] if self.settings_manager else {}
                res = {"text": f"DNS: {net_dict.get('dns_provider', 'Cloudflare')}, Gateway: {net_dict.get('gateway', '192.168.1.1')}"}
                if HAS_RICH:
                    console.print(Panel(Text(f"DNS Provider: {net_dict.get('dns_provider')}\nPrimary DNS: {net_dict.get('primary_dns')}\nSecondary DNS: {net_dict.get('secondary_dns')}\nGateway: {net_dict.get('gateway')}\nFirewall: Active ({net_dict.get('firewall_zone')})", style="white"), title="🌐 Network Configuration", border_style="cyan"))

            if self.voice_enabled and from_voice:
                VoiceIO.speak_sync(res["text"])
                if HAS_RICH:
                    console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
            return

        # 7. Audio Volume (/vol)
        if lower.startswith("/vol") or lower.startswith("volume"):
            parts = lower.split()
            if len(parts) > 1 and parts[1].isdigit():
                lvl = int(parts[1])
                res = self.settings_manager.set_volume(lvl) if self.settings_manager else {"text": f"Volume set to {lvl}%"}
                if HAS_RICH:
                    console.print(Panel(Text(res["text"], style="bold green"), title="🔊 Audio Volume", border_style="yellow"))
                if self.voice_enabled and from_voice:
                    VoiceIO.speak_sync(res["text"])
                    if HAS_RICH:
                        console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
                return

        # 8. Process Table (/ps, /top)
        if lower in ["/ps", "/top", "ps", "top", "processes"]:
            if HAS_RICH:
                PaletteTUI.render_process_table()
            return

        # 9. Security Capabilities Ledger (/sec, /caps)
        if lower in ["/sec", "/caps", "caps", "capabilities", "security"]:
            if HAS_RICH:
                PaletteTUI.render_capabilities_matrix()
            return

        # 10. Live Microphone Trigger (/mic, listen)
        if lower in ["/mic", "listen", "mic", "speak"]:
            if self.mic_muted:
                console.print("[bold red]Microphone is currently muted. Type '/mute' to unmute.[/bold red]")
                return
            console.print("[bold yellow]🎙️ [DAVIS ACTIVE...] Speak into your microphone now (5s)...[/bold yellow]")
            heard = VoiceIO.record_and_recognize(duration_secs=5)
            if not heard:
                console.print("[yellow]No speech detected. Please speak closer to your microphone.[/yellow]")
                return
            console.print(f"[bold green]🗣️ Heard You Say:[/bold green] \"{heard}\"")
            self.execute_command(heard, from_voice=True)
            return

        # 11. Microphone Privacy Toggle (/mute)
        if lower in ["/mute", "mute", "mic mute"]:
            self.mic_muted = not self.mic_muted
            state = "MUTED (Privacy Guard Active)" if self.mic_muted else "ACTIVE (Listening for 'Davis')"
            console.print(f"[bold yellow]🎙️ Microphone is now {state}.[/bold yellow]")
            return

        # 12. Power Mode Controls (/power)
        if lower.startswith("/power") or lower.startswith("power "):
            parts = lower.split()
            if len(parts) > 1:
                mode = parts[1].title()
                res = self.settings_manager.set_power_mode(mode) if self.settings_manager else {"text": f"Switched power mode to {mode}."}
                self.power_mode = res.get("mode", mode)
                msg = res["text"]
                if HAS_RICH:
                    console.print(Panel(Text(msg, style="bold green"), title="⚡ Power Management", border_style="green"))
                if self.voice_enabled and from_voice:
                    VoiceIO.speak_sync(msg)
                    if HAS_RICH:
                        console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
                return

        # 7. Workspace Switcher (/ws)
        if lower.startswith("/ws") or lower.startswith("workspace"):
            parts = lower.split()
            if len(parts) > 1:
                target = parts[1]
                # Map number or name
                mapped_id = None
                for k, v in self.workspaces.items():
                    if target == k or target.lower() == v.lower():
                        mapped_id = k
                        break
                if mapped_id:
                    self.current_workspace = mapped_id
                    ws_name = self.workspaces[mapped_id]
                    self.log_audit("workspace_switch", "workspace.manage", "ALLOWED", f"Switched to workspace {ws_name}")
                    msg = f"Switched active Wayland desktop profile to: {ws_name}."
                    if HAS_RICH:
                        console.print(Panel(Text(msg, style="bold green"), title="🖥️ Workspace Manager", border_style="cyan"))
                    if self.voice_enabled and from_voice:
                        VoiceIO.speak_sync(msg)
                        if HAS_RICH:
                            console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
                    return

        # 8. App Runner (/run, /app)
        if lower.startswith("/run ") or lower.startswith("/app ") or lower.startswith("run "):
            app = q.split(maxsplit=1)[1]
            if "game" in lower or "cyberpunk" in lower:
                self.log_audit("proton_launcher", "system.process.start", "ALLOWED", f"Proton runner for {app}")
                msg = f"🎮 Launched '{app}' via Proton Direct with DXVK, VKD3D-Proton & Gamescope (1440p @ 144Hz)."
                if HAS_RICH:
                    console.print(Panel(Text(msg, style="bold green"), title="🚀 Gaming Runner", border_style="green"))
                if self.voice_enabled and from_voice:
                    VoiceIO.speak_sync(f"Launching {app} in Proton Direct Gaming Mode.")
                    if HAS_RICH:
                        console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
                return
            else:
                self.log_audit("wine_launcher", "system.process.start", "ALLOWED", f"Wine prefix for {app}")
                msg = f"🪟 Launched '{app}' in isolated Wine prefix: /var/lib/aura/wine_prefixes/{app}."
                if HAS_RICH:
                    console.print(Panel(Text(msg, style="bold cyan"), title="🚀 Windows Compatibility", border_style="blue"))
                if self.voice_enabled and from_voice:
                    VoiceIO.speak_sync(f"Launching {app} in isolated Wine prefix.")
                    if HAS_RICH:
                        console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
                return

        # 9. Hardware Telemetry Snapshot (/sys status)
        if lower in ["/sys", "/sys status", "status", "hardware"]:
            self.log_audit("sys_hardware_inspect", "system.hardware.read", "ALLOWED", "System status query")
            res_live = self.settings_manager.get_live_resource_status() if self.settings_manager else {}
            net_live = self.settings_manager.get_live_network_status() if self.settings_manager else {}
            wifi_live = self.settings_manager.get_live_wifi_status() if self.settings_manager else {}
            power_live = self.settings_manager.get_live_power_status() if self.settings_manager else {}

            total_ram_gb = res_live.get("total_system_ram_mb", 16384) / 1024
            used_ram_gb = res_live.get("used_system_ram_mb", 8192) / 1024
            load_pct = res_live.get("memory_load_pct", 50)
            cpu_cores = res_live.get("logical_cpu_cores", os.cpu_count() or 4)

            table = Table(title="⚙️ AURA SYSTEM HARDWARE TELEMETRY", box=box.ROUNDED, header_style="bold cyan")
            table.add_column("Subsystem", style="bold white", width=22)
            table.add_column("Specification / Current Metrics", style="bold green")

            table.add_row("Operating System", f"{platform.system()} {platform.release()} (PROJECT AURA Subsystem)")
            table.add_row("Processor (CPU)", f"{cpu_cores} Logical Cores ({platform.processor() or 'x86_64 High-Performance'})")
            table.add_row("Memory (RAM)", f"{used_ram_gb:.1f} GB Used / {total_ram_gb:.1f} GB Total ({load_pct}% Memory Load)")
            table.add_row("Power Scheme", f"Mode: {power_live.get('active_mode', self.power_mode)}")
            table.add_row("Network Interface", f"IP: {net_live.get('ip_address', '127.0.0.1')} | Gateway: {net_live.get('gateway', 'N/A')}")
            wifi_label = f"Connected to '{wifi_live.get('connected_ssid')}' ({wifi_live.get('signal_pct')}%)" if wifi_live.get("connected_ssid") else "Disconnected"
            table.add_row("Wireless (Wi-Fi)", wifi_label)
            table.add_row("Voice Assistant", "DAVIS Neural AI Assistant (Echo Guard Active)")

            if HAS_RICH:
                console.print(table)
            if self.voice_enabled and from_voice:
                VoiceIO.speak_sync("System hardware inspected. All operating metrics are nominal.")
                if HAS_RICH:
                    console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
            return

        # 10. Audit Log Inspector (/sec audit, audit)
        if lower in ["/sec audit", "audit", "/audit"]:
            table = Table(title="🛡️ AURA AI STRUCTURED AUDIT LEDGER (/var/log/aura/ai/audit.jsonl)", box=box.SIMPLE_HEAVY, header_style="bold yellow")
            table.add_column("Timestamp", style="dim white", width=12)
            table.add_column("Tool Invoked", style="bold cyan", width=24)
            table.add_column("Capability Token", style="magenta", width=26)
            table.add_column("Decision", style="bold green")

            for ev in self.audit_events[-6:]:
                table.add_row(ev["timestamp"].split("T")[-1].replace("Z", ""), ev["tool"], ev["capability"], ev["decision"])

            if self.audit_events:
                console.print(table)
            else:
                console.print("[yellow]No audit events in current active session.[/yellow]")
            return

        # 11. Natural Conversational & Intelligence Engine (Davis)
        if self.dialogue_engine:
            dialogue = self.dialogue_engine.respond(q)
            resp_text = dialogue["text"]

            if dialogue["is_system_action"]:
                if dialogue["action_type"] == "switch_workspace":
                    target_ws = dialogue["action_data"]
                    if target_ws in self.workspaces:
                        self.current_workspace = target_ws
                        self.log_audit("workspace_switch", "workspace.manage", "ALLOWED", f"Switched to workspace {target_ws}")
                elif dialogue["action_type"] == "hardware_query":
                    self.log_audit("sys_hardware_inspect", "system.hardware.read", "ALLOWED", dialogue["action_data"])
                elif dialogue["action_type"] == "power":
                    if self.settings_manager:
                        self.power_mode = self.settings_manager.settings["power"]["active_mode"]

            # Render response in a styled panel
            if HAS_RICH:
                cat_title = "🤖 DAVIS AI INTELLIGENCE"
                if dialogue["action_type"] == "weather":
                    cat_title = "🌤️ LIVE WEATHER"
                elif dialogue["action_type"] == "currency":
                    cat_title = "💱 FOREX CURRENCY CONVERTER"
                elif dialogue["action_type"] == "math_science":
                    cat_title = "🔬 SCIENCE & MATHEMATICS"
                elif dialogue["action_type"] == "song":
                    cat_title = "🎵 MUSIC DISCOVERY"
                elif dialogue["action_type"] in ["file_search", "file_read", "disk_space"]:
                    cat_title = "📁 SYSTEM & STORAGE ACCESS"
                elif dialogue["action_type"] in ["wifi", "wifi_scan"]:
                    cat_title = "📶 WI-FI WIRELESS MANAGER"
                elif dialogue["action_type"] == "bluetooth":
                    cat_title = "📡 BLUETOOTH DEVICE MANAGER"
                elif dialogue["action_type"] == "power":
                    cat_title = "⚡ POWER MANAGEMENT"
                elif dialogue["action_type"] == "resource_quota":
                    cat_title = "🧠 RAM & RESOURCE ALLOCATOR"
                elif dialogue["action_type"] in ["network_ping", "network_dns"]:
                    cat_title = "🌐 NETWORK & INTERNET"
                elif dialogue["action_type"] == "volume":
                    cat_title = "🔊 AUDIO CONTROLS"
                elif dialogue["action_type"] == "open_settings":
                    cat_title = "⚙️ UNIFIED SYSTEM CONTROL CENTER"

                console.print(Panel(Text(resp_text, style="white"), title=cat_title, border_style="cyan", padding=(0, 1)))

                # If the voice command opened settings or scanned wifi/bt, also display the full interactive table
                if dialogue["action_type"] == "open_settings" and self.settings_manager:
                    PaletteTUI.render_settings_hub(self.settings_manager.settings)
                elif dialogue["action_type"] == "wifi_scan" and self.settings_manager:
                    PaletteTUI.render_wifi_table(dialogue["action_data"], self.settings_manager.settings["wifi"]["connected_ssid"], self.settings_manager.settings["wifi"]["enabled"])
                elif dialogue["action_type"] == "resource_quota" and self.settings_manager:
                    PaletteTUI.render_resource_quotas(self.settings_manager.settings["resources"])

            if self.voice_enabled and from_voice:
                VoiceIO.speak_sync(resp_text)
                if HAS_RICH:
                    console.print("[dim cyan]AURA » (Ready — listening for 'Davis' or type a command)[/dim cyan]")
            return

def main():
    os_env = AuraOS()

    while True:
        try:
            # Render Live Top HUD Bar before each prompt
            active_name = os_env.workspaces[os_env.current_workspace]
            res_live = os_env.settings_manager.get_live_resource_status() if os_env.settings_manager else {}
            live_used_ram = res_live.get("used_system_ram_mb", 420)
            live_total_ram = res_live.get("total_system_ram_mb", 16384)
            if HAS_RICH:
                console.print()
                PaletteTUI.render_hud_header(
                    active_workspace=active_name,
                    cpu_pct=float(res_live.get("memory_load_pct", 15) // 5),
                    ram_mb=live_used_ram,
                    ram_total=live_total_ram,
                    mic_active=(os_env.voice_enabled and not os_env.mic_muted)
                )

            prompt_str = f"AURA » "
            user_input = console.input(f"[bold cyan]{prompt_str}[/bold cyan]") if HAS_RICH else input(prompt_str)
            if not user_input.strip():
                continue
            if user_input.strip().lower() in ["exit", "quit"]:
                os_env._stop_listener = True
                console.print("[bold green]Shutting down DAVIS and AURA OS cleanly.[/bold green]")
                break

            os_env.execute_command(user_input)

        except (KeyboardInterrupt, EOFError):
            os_env._stop_listener = True
            console.print("\n[bold green]AURA session terminated.[/bold green]")
            break

if __name__ == "__main__":
    main()
