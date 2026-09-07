#!/usr/bin/env python3
"""
PROJECT AURA - Live Interactive Terminal Desktop & JARVIS Voice Assistant Runtime
Run this script to immediately experience and test AURA OS, the Wayland Command Palette,
Voice Assistant ("Hey Jarvis", "Aura"), Hardware Inspector, and Capability-Gated Security.
"""

import sys
import os
import json
import time
import uuid

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class AuraColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class VoiceSynthesizer:
    @staticmethod
    def speak(text):
        """Speak response using Windows SAPI TTS or fallback gracefully"""
        if sys.platform == "win32":
            try:
                # Use Windows native PowerShell SAPI voice synthesizer without external dependencies
                clean_text = text.replace('"', '').replace("'", "").replace("\n", " ")
                cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{clean_text}\')"'
                # Run async so it doesn't block terminal typing
                import subprocess
                subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

class MockHardware:
    @staticmethod
    def get_metrics():
        return {
            "os": "AURA OS 1.0 (Linux 6.9-aura / NixOS)",
            "cpu_usage": "3.8%",
            "ram_used": "420 MB / 32,768 MB (Ultra-Lightweight Idle Budget)",
            "gpu": "Vulkan 1.3 Direct Rendering (Mesa 24.1)",
            "audio_subsystem": "PipeWire 1.0 Low-Latency Audio + VAD",
            "voice_assistant": "JARVIS Voice Engine (Neural Male)",
            "active_workspace": "Development",
            "audit_log": "/var/log/aura/ai/audit.jsonl"
        }

class JarvisSimulator:
    def __init__(self):
        self.granted_caps = {
            "system.hardware.read",
            "system.process.list",
            "workspace.manage",
            "filesystem.read[*]",
            "notification.send",
            "audio.capture",
            "audio.playback"
        }
        self.workspaces = {
            "1": "General (Browser, Notes)",
            "2": "Development (Code, Terminal, Podman)",
            "3": "Gaming (Gamescope, Proton, DXVK)",
            "4": "Creative (Audio/Video Suite)",
            "5": "AI Workflows (Local SLM + Tools)"
        }
        self.current_workspace = "2"
        self.audit_events = []
        self.voice_enabled = True
        self.mic_muted = False

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

    def handle_command(self, query):
        q = query.strip()
        lower = q.lower()

        # Check for Voice Wake-Word
        is_voice = False
        voice_phrase = q
        if lower.startswith("hey jarvis") or lower.startswith("jarvis"):
            is_voice = True
            voice_phrase = q.split(maxsplit=2)[-1] if len(q.split()) > 2 else ""
            lower = voice_phrase.lower()
        elif lower.startswith("aura"):
            is_voice = True
            voice_phrase = q.split(maxsplit=1)[-1] if len(q.split()) > 1 else ""
            lower = voice_phrase.lower()

        # Voice Assistant Controls
        if lower in ["voice", "voice status"]:
            status_mic = f"{AuraColors.FAIL}MUTED{AuraColors.ENDC}" if self.mic_muted else f"{AuraColors.GREEN}ACTIVE (Listening for 'Hey Jarvis' / 'Aura'){AuraColors.ENDC}"
            status_tts = f"{AuraColors.GREEN}ENABLED (Speaks through speakers){AuraColors.ENDC}" if self.voice_enabled else f"{AuraColors.FAIL}DISABLED{AuraColors.ENDC}"
            return f"{AuraColors.MAGENTA}🎙️ [JARVIS Voice Assistant Subsystem]{AuraColors.ENDC}\n" \
                   f" - Microphone (AudioCapture): {status_mic}\n" \
                   f" - Speech Synthesis (AudioPlayback): {status_tts}\n" \
                   f" - Wake Words: 'Hey Jarvis', 'Aura', 'Jarvis'\n" \
                   f" - STT Pipeline: Whisper Neural V3\n" \
                   f" - TTS Engine: Piper Neural Voice Model (Low-Latency < 50ms)"

        if lower in ["listen", "mic", "speak"]:
            if self.mic_muted:
                return f"{AuraColors.FAIL}Microphone is muted. Type 'mute' to unmute first.{AuraColors.ENDC}"
            print(f"{AuraColors.YELLOW}🎙️ [LISTENING TO YOUR MICROPHONE...] Speak now...{AuraColors.ENDC}")
            script_path = os.path.join(os.path.dirname(__file__), "listen_mic.ps1")
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path, "-TimeoutSeconds", "6"]
            try:
                import subprocess
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=9)
                transcription = proc.stdout.strip()
                if not transcription or "__NO_SPEECH_DETECTED__" in transcription:
                    return f"{AuraColors.YELLOW}No speech was detected from your microphone.{AuraColors.ENDC}"
                print(f"{AuraColors.GREEN}🗣️ Heard from Microphone:{AuraColors.ENDC} \"{transcription}\"")
                return self.handle_command(transcription)
            except Exception as e:
                return f"{AuraColors.FAIL}Microphone capture error: {e}{AuraColors.ENDC}"

        # 1. Deterministic Fast-Path
        if lower in ["status", "hardware", "sys"]:
            self.log_audit("sys_hardware_inspect", "system.hardware.read", "ALLOWED", "System status query")
            metrics = MockHardware.get_metrics()
            if self.voice_enabled and is_voice:
                VoiceSynthesizer.speak("System hardware inspected. All platform parameters are nominal.")
            return f"{AuraColors.CYAN}[AURA System Daemon - Hardware Snapshot]{AuraColors.ENDC}\n" + \
                   json.dumps(metrics, indent=2)

        if lower.startswith("workspace"):
            parts = lower.split()
            if len(parts) > 1 and parts[1] in self.workspaces:
                self.current_workspace = parts[1]
                self.log_audit("workspace_switch", "workspace.manage", "ALLOWED", f"Switched to workspace {parts[1]}")
                msg = f"Switched to {self.workspaces[parts[1]].split()[0]} profile."
                if self.voice_enabled and is_voice:
                    VoiceSynthesizer.speak(msg)
                return f"{AuraColors.GREEN}[OK] Switched active desktop profile to: {self.workspaces[parts[1]]}{AuraColors.ENDC}"
            else:
                out = f"{AuraColors.CYAN}Available Workspaces:{AuraColors.ENDC}\n"
                for k, v in self.workspaces.items():
                    prefix = f"{AuraColors.GREEN}* [Active] " if k == self.current_workspace else "  "
                    out += f"{prefix}{k}: {v}{AuraColors.ENDC}\n"
                return out

        if lower.startswith("compat ") or lower.startswith("run "):
            app = q.split(maxsplit=1)[1]
            if "game" in lower or "cyberpunk" in lower:
                self.log_audit("proton_launcher", "system.process.start", "ALLOWED", f"Proton runner for {app}")
                if self.voice_enabled and is_voice:
                    VoiceSynthesizer.speak(f"Launching {app} in Proton Direct Gaming Mode.")
                return f"{AuraColors.GREEN}[Proton Direct Runtime]{AuraColors.ENDC} Launched '{app}' with DXVK, VKD3D-Proton & Gamescope (1440p @ 144Hz)."
            elif "notepad" in lower or "office" in lower:
                self.log_audit("wine_launcher", "system.process.start", "ALLOWED", f"Wine prefix for {app}")
                if self.voice_enabled and is_voice:
                    VoiceSynthesizer.speak(f"Launching {app} in isolated Wine prefix.")
                return f"{AuraColors.BLUE}[Wine Staging Runtime]{AuraColors.ENDC} Launched '{app}' in isolated prefix: /var/lib/aura/wine_prefixes/{app}."
            else:
                self.log_audit("kvm_launcher", "vm.manage", "ALLOWED", f"KVM Fallback for {app}")
                if self.voice_enabled and is_voice:
                    VoiceSynthesizer.speak(f"Routing {app} to Windows Virtual Machine fallback.")
                return f"{AuraColors.YELLOW}[KVM VM Fallback]{AuraColors.ENDC} Non-Wine compatible app '{app}' routed to virtio-accelerated Windows VM."

        if lower.startswith("doctor") or lower.startswith("dev"):
            self.log_audit("dev_environment_doctor", "filesystem.read[*]", "ALLOWED", "Checked project environment")
            if self.voice_enabled and is_voice:
                VoiceSynthesizer.speak("Developer environments and toolchains are verified healthy.")
            return f"{AuraColors.CYAN}[AURA Dev Doctor]{AuraColors.ENDC}\n" \
                   f" - Detected Stacks: Rust (Cargo), Nix Flake, TypeScript SDK, Python 3.12\n" \
                   f" - Sandboxed Toolchains: Ready\n" \
                   f" - Status: All developer environment invariants healthy."

        if lower == "audit":
            out = f"{AuraColors.YELLOW}[AURA AI Audit Log - /var/log/aura/ai/audit.jsonl]{AuraColors.ENDC}\n"
            for ev in self.audit_events[-5:]:
                out += f" [{ev['timestamp']}] Tool: {ev['tool']} | Cap: {ev['capability']} | Decision: {ev['decision']}\n"
            return out if self.audit_events else "No audit events in current session."

        # 2. AI Reasoning & Capability Enforcement
        if "delete" in lower or "rm -rf" in lower:
            ev = self.log_audit("filesystem_delete", "filesystem.delete", "APPROVAL_REQUIRED", q)
            if self.voice_enabled and is_voice:
                VoiceSynthesizer.speak("Security alert: Privileged operation requires user approval.")
            return f"{AuraColors.YELLOW}[JARVIS Security Gate: EXECUTE_PRIVILEGED]{AuraColors.ENDC}\n" \
                   f"Action '{q}' requires explicit user approval modal.\n" \
                   f"Capability 'filesystem.delete' is not granted automatically in standard profile."

        if "sudo" in lower or "root" in lower:
            ev = self.log_audit("terminal_exec", "system.privileged", "DENIED", q)
            if self.voice_enabled and is_voice:
                VoiceSynthesizer.speak("Access denied. The AI runtime is not permitted to execute root commands.")
            return f"{AuraColors.FAIL}[JARVIS Security Violation: Zero Ambient Authority]{AuraColors.ENDC}\n" \
                   f"AI models in PROJECT AURA cannot invoke raw sudo/root commands. Action blocked."

        # Safe AI Voice/Text Response
        self.log_audit("jarvis_reasoning", "ai.reasoning", "ALLOWED", q)
        response_text = f"I have processed your request for '{q}' within the capability-bounded security sandbox."
        if is_voice:
            response_text = f"Understood. Operating systems and workspace parameters are configured for '{voice_phrase}'."
        if self.voice_enabled:
            VoiceSynthesizer.speak(response_text)

        prefix = f"{AuraColors.MAGENTA}🎙️ [JARVIS Voice Assistant]: {AuraColors.ENDC}" if is_voice else f"{AuraColors.BLUE}[JARVIS Local SLM]: {AuraColors.ENDC}"
        return f"{prefix}{response_text}"

def print_banner():
    banner = f"""{AuraColors.CYAN}
================================================================================
  PROJECT AURA - Linux + Wayland + JARVIS Voice Assistant + NixOS Base
================================================================================{AuraColors.ENDC}
  * Platform Running in Host Emulation Mode (Type 'exit' to quit)
--------------------------------------------------------------------------------
  {AuraColors.MAGENTA}🎙️ Voice Assistant Commands (Wake words: 'Hey Jarvis', 'Aura'):{AuraColors.ENDC}
    * {AuraColors.BOLD}Hey Jarvis, status{AuraColors.ENDC}       - Spoken hardware & resource inspection
    * {AuraColors.BOLD}Hey Jarvis, workspace 3{AuraColors.ENDC}  - Voice-triggered Gaming Mode profile switch
    * {AuraColors.BOLD}voice{AuraColors.ENDC}                    - Check Voice Assistant audio & microphone status
    * {AuraColors.BOLD}listen / mic{AuraColors.ENDC}             - Capture LIVE audio from your real physical microphone
    * {AuraColors.BOLD}voice on / voice off{AuraColors.ENDC}     - Enable/disable speech synthesizer voice audio
--------------------------------------------------------------------------------
  Hands-Free Mode: Run 'python scripts/run_live_voice.py' for continuous mic listening
  Keyboard / Command Palette:
    * status | workspace [1-5] | run <app.exe> | dev doctor | audit
================================================================================
"""
    print(banner)

def main():
    print_banner()
    sim = JarvisSimulator()

    while True:
        try:
            prompt_str = f"{AuraColors.CYAN}AURA Shell [{sim.workspaces[sim.current_workspace].split()[0]}] » {AuraColors.ENDC}"
            user_input = input(prompt_str)
            if not user_input.strip():
                continue
            if user_input.strip().lower() in ["exit", "quit"]:
                print(f"{AuraColors.GREEN}Shutting down AURA session cleanly.{AuraColors.ENDC}")
                break

            response = sim.handle_command(user_input)
            print(f"\n{response}\n")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{AuraColors.GREEN}AURA session terminated.{AuraColors.ENDC}")
            break

if __name__ == "__main__":
    main()
