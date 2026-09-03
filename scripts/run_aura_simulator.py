#!/usr/bin/env python3
"""
PROJECT AURA - Live Interactive Terminal Desktop & JARVIS Runtime
Run this script to immediately experience and test AURA OS, the Wayland Command Palette,
Hardware Inspector, Workspace Profiles, and JARVIS Capability-Gated Agent on your host machine.
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
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class MockHardware:
    @staticmethod
    def get_metrics():
        return {
            "os": "AURA OS 1.0 (Linux 6.9-aura / NixOS)",
            "cpu_usage": "3.8%",
            "ram_used": "420 MB / 32,768 MB (Ultra-Lightweight Idle Budget)",
            "gpu": "Vulkan 1.3 Direct Rendering (Mesa 24.1)",
            "power_mode": "Balanced",
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
            "notification.send"
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

        # 1. Deterministic Fast-Path
        if lower in ["status", "hardware", "sys"]:
            self.log_audit("sys_hardware_inspect", "system.hardware.read", "ALLOWED", "System status query")
            metrics = MockHardware.get_metrics()
            return f"{AuraColors.CYAN}[AURA System Daemon - Hardware Snapshot]{AuraColors.ENDC}\n" + \
                   json.dumps(metrics, indent=2)

        if lower.startswith("workspace"):
            parts = lower.split()
            if len(parts) > 1 and parts[1] in self.workspaces:
                self.current_workspace = parts[1]
                self.log_audit("workspace_switch", "workspace.manage", "ALLOWED", f"Switched to workspace {parts[1]}")
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
                return f"{AuraColors.GREEN}[Proton Direct Runtime]{AuraColors.ENDC} Launched '{app}' with DXVK, VKD3D-Proton & Gamescope (1440p @ 144Hz)."
            elif "notepad" in lower or "office" in lower:
                self.log_audit("wine_launcher", "system.process.start", "ALLOWED", f"Wine prefix for {app}")
                return f"{AuraColors.BLUE}[Wine Staging Runtime]{AuraColors.ENDC} Launched '{app}' in isolated prefix: /var/lib/aura/wine_prefixes/{app}."
            else:
                self.log_audit("kvm_launcher", "vm.manage", "ALLOWED", f"KVM Fallback for {app}")
                return f"{AuraColors.YELLOW}[KVM VM Fallback]{AuraColors.ENDC} Non-Wine compatible app '{app}' routed to virtio-accelerated Windows VM."

        if lower.startswith("doctor") or lower.startswith("dev"):
            self.log_audit("dev_environment_doctor", "filesystem.read[*]", "ALLOWED", "Checked project environment")
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
            return f"{AuraColors.YELLOW}[JARVIS Security Gate: EXECUTE_PRIVILEGED]{AuraColors.ENDC}\n" \
                   f"Action '{q}' requires explicit user approval modal.\n" \
                   f"Capability 'filesystem.delete' is not granted automatically in standard profile."

        if "sudo" in lower or "root" in lower:
            ev = self.log_audit("terminal_exec", "system.privileged", "DENIED", q)
            return f"{AuraColors.FAIL}[JARVIS Security Violation: Zero Ambient Authority]{AuraColors.ENDC}\n" \
                   f"AI models in PROJECT AURA cannot invoke raw sudo/root commands. Action blocked."

        # Safe AI Response
        self.log_audit("jarvis_reasoning", "ai.reasoning", "ALLOWED", q)
        return f"{AuraColors.BLUE}[JARVIS Local Runtime (SLM)]: {AuraColors.ENDC}Understood intent for '{q}'. " \
               f"Executed task deterministically within declared project capability sandbox."

def print_banner():
    banner = f"""{AuraColors.CYAN}
================================================================================
  PROJECT AURA - Linux + Wayland + JARVIS AI Runtime + NixOS Base
================================================================================{AuraColors.ENDC}
  * Platform Running in Host Emulation Mode (Type 'exit' to quit)
--------------------------------------------------------------------------------
  Commands / Global Palette (Ctrl+Space equivalent):
    * status           - Inspect hardware, CPU, RAM & idle budget
    * workspace [1-5]  - Switch Wayland workspace profiles (General, Dev, Gaming, etc.)
    * run <app.exe>    - Test Windows app/game runner (Proton / Wine / KVM)
    * dev doctor       - Check developer toolchains and isolated Nix shells
    * audit            - View real-time tamper-evident AI audit logs
    * <any question>   - Query JARVIS OS-Native AI Runtime
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
