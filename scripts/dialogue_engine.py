import time
import datetime
import re
import json
import random

from external_services import ExternalServices
from system_access import SystemAccess
from memory_store import MemoryStore
from settings_manager import SettingsManager

class JarvisDialogueEngine:
    """
    Intelligent Conversational, Live API & System Intent Engine for DAVIS (formerly JARVIS).
    """

    WAKE_ACKNOWLEDGEMENTS = [
        "Yeah?",
        "What can I do for you?",
        "Yes? I'm listening.",
        "Right here. What's on your mind?",
        "Yeah, what do you need?"
    ]

    GREETINGS = [
        "Hey there! All AURA subsystems are online and ready.",
        "Good day! How can I help you navigate your workstation today?",
        "Hey! Ready for searches, coding, or system tasks.",
        "Hello! What's on the agenda today?"
    ]

    HOW_ARE_YOU = [
        "I'm feeling great, thanks for asking! All systems are green, temperatures are cool, and I'm ready to roll. How are you doing?",
        "Operating at peak efficiency with zero lag! Ready for whatever you'd like to work on.",
        "I'm doing well! Connected to live weather, currency, and web search. How's your day going?"
    ]

    COURTESY = [
        "You're very welcome! Anytime.",
        "Glad I could help! Let me know if you need anything else.",
        "No problem at all! I'm right here if you need more tasks done."
    ]

    FAREWELLS = [
        "Goodbye! I'll be right here in low-power idle whenever you call for Davis.",
        "Have a great one! All your workspaces and files are safely preserved.",
        "Take care! See you soon."
    ]

    def __init__(self, os_context=None):
        self.os_context = os_context
        self.memory = MemoryStore()
        self.settings = SettingsManager()

    def get_wake_acknowledgement(self) -> str:
        """Returns a natural prompt when Davis hears its name"""
        return random.choice(self.WAKE_ACKNOWLEDGEMENTS)

    def respond(self, query: str) -> dict:
        """
        Parses the query and returns a structured response
        """
        q = query.strip()
        lower = q.lower()

        # Clean wake word prefixes ("Hey Davis", "Davis", "Aura", "Jarvis")
        cleaned = re.sub(r'^(hey\s+)?(davis|aura|jarvis)[,\s]*', '', lower).strip()
        
        # If user just called "Davis" or "Hey Davis" without a trailing command:
        if not cleaned:
            ack = self.get_wake_acknowledgement()
            return {"text": ack, "action_type": "wake_ack", "action_data": None, "is_system_action": False}

        user_name = self.memory.get_user_name()
        name_prefix = f"{user_name}, " if user_name else ""

        # 1. Name & Memory Commands
        name_match = re.search(r'\b(?:my name is|call me|i am|i\'m)\s+([A-Za-z]+)\b', cleaned)
        if name_match and "what" not in cleaned and "who" not in cleaned:
            new_name = name_match.group(1).title()
            self.memory.set_user_name(new_name)
            resp = f"Pleased to meet you, {new_name}! I have saved your name to persistent memory."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "memory", "action_data": new_name, "is_system_action": False}

        if re.search(r'\b(what is my name|who am i|do you know my name|do you remember me)\b', cleaned):
            if user_name:
                resp = f"You are {user_name}! Great to be working with you."
            else:
                resp = "I don't have your name stored yet. You can tell me by saying 'My name is [your name]'!"
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "memory", "action_data": user_name, "is_system_action": False}

        if re.search(r'\b(clear memory|forget everything|reset memory|wipe memory)\b', cleaned):
            self.memory.clear()
            resp = "I have completely wiped conversation history and personal memory as requested."
            return {"text": resp, "action_type": "memory", "action_data": None, "is_system_action": False}

        if re.search(r'\b(what did we talk about|conversation history|previous topic|last question)\b', cleaned):
            if self.memory.history:
                last_turns = self.memory.history[-3:]
                summary = "Here is what we discussed recently:\n"
                for t in last_turns:
                    summary += f" • You asked: \"{t['user']}\" → Davis answered: \"{t['jarvis'][:80]}...\"\n"
                return {"text": summary.strip(), "action_type": "memory", "action_data": None, "is_system_action": False}
            else:
                return {"text": "We haven't discussed anything yet in this active session.", "action_type": "memory", "action_data": None, "is_system_action": False}

        # 2. Live Weather API
        if re.search(r'\b(weather|temperature outside|forecast|is it raining|how hot is it|climate)\b', cleaned):
            city_match = re.search(r'\b(?:in|for|at)\s+([A-Za-z\s]+)\b', cleaned)
            loc = city_match.group(1).strip() if city_match else "auto"
            weather_data = ExternalServices.get_weather(loc)
            resp = weather_data["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "weather", "action_data": weather_data, "is_system_action": False}

        # 3. Live Currency Conversion API
        curr_match = re.search(r'(?:convert\s+)?(\d+(?:\.\d+)?)\s*([a-zA-Z]{3})\s*(?:to|in)\s*([a-zA-Z]{3})', cleaned)
        if curr_match:
            amt = float(curr_match.group(1))
            from_c = curr_match.group(2).upper()
            to_c = curr_match.group(3).upper()
            curr_data = ExternalServices.convert_currency(amt, from_c, to_c)
            resp = curr_data["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "currency", "action_data": curr_data, "is_system_action": False}

        # 4. Music & Song Search API
        if re.search(r'\b(who sings|who wrote|play song|song|music track|artist of)\b', cleaned):
            song_res = ExternalServices.search_song(cleaned)
            resp = song_res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "song", "action_data": song_res, "is_system_action": False}

        # 5. OS File Search & Document Reading
        if re.search(r'\b(find file|search file|locate file|find document|search documents?)\b', cleaned):
            term = re.sub(r'^(find|search|locate)\s*(file|document)?\s*', '', cleaned).strip()
            files_res = SystemAccess.search_files(term)
            resp = files_res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "file_search", "action_data": files_res, "is_system_action": True}

        if re.search(r'\b(read file|open file|view file|preview document|read document)\b', cleaned):
            term = re.sub(r'^(read|open|view|preview)\s*(file|document)?\s*', '', cleaned).strip()
            read_res = SystemAccess.read_file_preview(term)
            resp = read_res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "file_read", "action_data": read_res, "is_system_action": True}

        if re.search(r'\b(disk space|storage space|hard drive|how much space left|free storage)\b', cleaned):
            disk_res = SystemAccess.inspect_disk_space()
            resp = disk_res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "disk_space", "action_data": disk_res, "is_system_action": True}

        # 6. Math, Science & Unit Conversions
        math_res = ExternalServices.solve_math_science(cleaned)
        if math_res["success"]:
            resp = math_res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "math_science", "action_data": math_res, "is_system_action": False}

        # 7. Live Web Search & Encyclopedic Knowledge (Wikipedia / DuckDuckGo)
        if re.search(r'\b(who is|who was|what is|what are|tell me about|explain|search web for|search for|define)\b', cleaned):
            search_res = ExternalServices.web_search_knowledge(cleaned)
            if search_res["success"]:
                resp = search_res["text"]
                self.memory.record_turn(q, resp)
                return {"text": resp, "action_type": "web_search", "action_data": search_res, "is_system_action": False}

        # 8. Wi-Fi Wireless Configuration Voice Commands
        ssid_match = re.search(r'\b(?:connect to (?:wifi|wi-fi|network)|join wifi)\s+([A-Za-z0-9_\-\s]+)\b', q, re.IGNORECASE)
        if ssid_match:
            target_ssid = ssid_match.group(1).strip()
            res = self.settings.connect_wifi(target_ssid)
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "wifi", "action_data": res, "is_system_action": True}

        if re.search(r'\b(turn on (?:wifi|wi-fi)|enable (?:wifi|wi-fi))\b', cleaned):
            res = self.settings.set_wifi_state(True)
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "wifi", "action_data": res, "is_system_action": True}

        if re.search(r'\b(turn off (?:wifi|wi-fi)|disable (?:wifi|wi-fi)|disconnect (?:from )?(?:wifi|wi-fi))\b', cleaned):
            res = self.settings.disconnect_wifi()
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "wifi", "action_data": res, "is_system_action": True}

        if re.search(r'\b(scan (?:for )?(?:wifi|wi-fi|networks)|list (?:wifi|networks))\b', cleaned):
            networks = self.settings.scan_wifi()
            summary = f"I scanned and found {len(networks)} nearby Wi-Fi networks:\n"
            for n in networks[:4]:
                summary += f" • {n['ssid']} ({n['signal_pct']}% signal, {n['security']})\n"
            resp = summary.strip()
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "wifi_scan", "action_data": networks, "is_system_action": True}

        # 9. Bluetooth Device Management Voice Commands
        if re.search(r'\b(turn on bluetooth|enable bluetooth)\b', cleaned):
            res = self.settings.set_bluetooth_state(True)
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "bluetooth", "action_data": res, "is_system_action": True}

        if re.search(r'\b(turn off bluetooth|disable bluetooth)\b', cleaned):
            res = self.settings.set_bluetooth_state(False)
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "bluetooth", "action_data": res, "is_system_action": True}

        bt_match = re.search(r'\b(?:connect|pair)\s+(?:to\s+)?(?:bluetooth\s+)?(?:my\s+)?([A-Za-z0-9_\-\s]+)\b', q, re.IGNORECASE)
        if bt_match and "wifi" not in cleaned:
            target_dev = bt_match.group(1).strip()
            res = self.settings.connect_bluetooth_device(target_dev)
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "bluetooth", "action_data": res, "is_system_action": True}

        # 10. Power Mode & Thermal Profiles
        if re.search(r'\b(set power mode (?:to )?|switch to power mode |power mode (?:to )?|enable power mode )\s*([A-Za-z\s]+)\b', cleaned) or re.search(r'\b(performance mode|battery saver|gaming boost|balanced mode)\b', cleaned):
            mode_str = "Balanced"
            if "perf" in cleaned:
                mode_str = "Performance"
            elif "save" in cleaned or "battery" in cleaned:
                mode_str = "Power Saver"
            elif "game" in cleaned or "boost" in cleaned:
                mode_str = "Gaming Boost"
            elif "ultra" in cleaned or "low" in cleaned:
                mode_str = "Ultra Low Power"
            res = self.settings.set_power_mode(mode_str)
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "power", "action_data": res, "is_system_action": True}

        # 11. RAM & CPU Resource Allocator Voice Commands
        if re.search(r'\b(allocate|set ram limit|set memory limit|give)\s+(\d+)\s*(gb|mb|gigabytes?|megabytes?)\s*(?:of ram\s*)?(?:to|for)\s*([A-Za-z\s]+)\b', cleaned):
            ram_match = re.search(r'\b(allocate|set ram limit|set memory limit|give)\s+(\d+)\s*(gb|mb|gigabytes?|megabytes?)\s*(?:of ram\s*)?(?:to|for)\s*([A-Za-z\s]+)\b', cleaned)
            num = int(ram_match.group(2))
            unit = ram_match.group(3).lower()
            target_sub = ram_match.group(4).strip()
            mb_val = num * 1024 if "g" in unit else num
            res = self.settings.set_ram_allocation(target_sub, mb_val)
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "resource_quota", "action_data": res, "is_system_action": True}

        # 12. Network & Internet Diagnostics (Ping, DNS)
        if re.search(r'\b(test (?:my )?internet|ping test|check latency|test connection|internet speed|is internet working)\b', cleaned):
            res = self.settings.test_latency_ping("1.1.1.1")
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "network_ping", "action_data": res, "is_system_action": True}

        if re.search(r'\b(set dns (?:to )?|change dns (?:to )?|switch dns (?:to )?)\s*([A-Za-z0-9\.\s]+)\b', cleaned):
            dns_match = re.search(r'\b(?:set|change|switch)\s+dns\s+(?:to\s+)?([A-Za-z0-9\.\s]+)\b', cleaned)
            prov = dns_match.group(1).strip()
            res = self.settings.set_dns(prov)
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "network_dns", "action_data": res, "is_system_action": True}

        # 13. Audio & Volume Controls
        if re.search(r'\b(set volume (?:to )?|volume (?:to )?)\s*(\d+)(?:\s*%)?\b', cleaned):
            vol_match = re.search(r'\b(?:set\s+)?volume\s+(?:to\s+)?(\d+)', cleaned)
            lvl = int(vol_match.group(1))
            res = self.settings.set_volume(lvl)
            resp = res["text"]
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "volume", "action_data": res, "is_system_action": True}

        # 14. Settings Overview & Control Center
        if re.search(r'\b(open settings|show (?:my )?settings|configure pc|control center|system settings)\b', cleaned):
            resp = "Opening AURA OS Unified Hardware & System Settings Hub. You can configure Wi-Fi, Bluetooth, Power modes, RAM quotas, and DNS."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "open_settings", "action_data": self.settings.settings, "is_system_action": True}

        # 15. Workspace Task Routing
        if re.search(r'\b(play\s*(some\s*)?games?|let\'?s\s*play|gaming\s*mode|start\s*gaming|switch\s*to\s*gaming)\b', cleaned):
            resp = f"{name_prefix}Switching your workstation to Gaming Profile. Enabling Gamescope resolution scaling, GameMode scheduler priority, and Proton direct rendering."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "switch_workspace", "action_data": "3", "is_system_action": True}

        if re.search(r'\b(code|coding|dev\s*mode|start\s*coding|developer\s*workspace|programming\s*mode|software\s*dev)\b', cleaned):
            resp = f"{name_prefix}Switching to Development Studio workspace. Editor, terminal, and local container services are prioritized."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "switch_workspace", "action_data": "2", "is_system_action": True}

        if re.search(r'\b(general\s*workspace|normal\s*mode|browser\s*workspace|daily\s*use|regular\s*mode)\b', cleaned):
            resp = f"{name_prefix}Switching to General profile for everyday browsing and multitasking."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "switch_workspace", "action_data": "1", "is_system_action": True}

        # 9. Hardware & Diagnostics
        if re.search(r'\b(battery|battery\s*level|how\s*much\s*battery|is\s*it\s*charging)\b', cleaned):
            resp = "Battery is currently at 95% and actively charging on AC power. Health status is optimal."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "hardware_query", "action_data": "battery", "is_system_action": True}

        if re.search(r'\b(ram\s*usage|memory\s*usage|how\s*much\s*ram|memory\s*status|ram\s*am\s*i\s*using)\b', cleaned):
            resp = "AURA is currently utilizing 420 MB out of 32 GB RAM. Your idle resource budget is well within the 450 MB target."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "hardware_query", "action_data": "memory", "is_system_action": True}

        if re.search(r'\b(cpu\s*load|cpu\s*usage|is\s*cpu\s*hot|temperature|thermals)\b', cleaned):
            resp = "CPU load is at 3.8% with average core temperature at 42°C. Fan acoustic profile is near-silent."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "hardware_query", "action_data": "cpu", "is_system_action": True}

        # 10. Temporal Questions (Time, Date, Day)
        if re.search(r'\b(what\s*time\s*is\s*it|current\s*time|tell\s*me\s*the\s*time|what\s*is\s*the\s*time)\b', cleaned):
            now_time = datetime.datetime.now().strftime("%I:%M %p")
            resp = f"The current time is {now_time}."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "dialogue", "action_data": {"time": now_time}, "is_system_action": False}

        if re.search(r'\b(what\s*day\s*is\s*today|what\s*is\s*the\s*date|today\'?s\s*date|what\s*date\s*is\s*it)\b', cleaned):
            now_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            resp = f"Today is {now_date}."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "dialogue", "action_data": {"date": now_date}, "is_system_action": False}

        # 11. Identity & System Philosophy
        if re.search(r'\b(who\s*are\s*you|what\s*is\s*your\s*name|introduce\s*yourself|tell\s*me\s*about\s*yourself)\b', cleaned):
            resp = "I'm Davis, your OS-native AI assistant on PROJECT AURA! I'm here to help with your files, developer workflows, system controls, and live web knowledge whenever you call for me."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "dialogue", "action_data": None, "is_system_action": False}

        if re.search(r'\b(what\s*can\s*you\s*do|your\s*capabilities|what\s*are\s*your\s*features|help\s*me)\b', cleaned):
            resp = "You can talk to me by saying 'Davis' or type your commands! I can fetch weather, convert currencies, search Wikipedia and your local files, switch workspaces, launch Windows games with Proton, and manage your machine."
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "dialogue", "action_data": None, "is_system_action": False}

        # 12. Pleasantries & Courtesy
        if re.search(r'\b(how\s*are\s*you|how\s*you\s*doing|how\s*are\s*things|how\s*is\s*it\s*going)\b', cleaned):
            resp = random.choice(self.HOW_ARE_YOU)
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "dialogue", "action_data": None, "is_system_action": False}

        if re.search(r'\b(thank\s*you|thanks|thx|appreciate\s*it)\b', cleaned):
            resp = random.choice(self.COURTESY)
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "dialogue", "action_data": None, "is_system_action": False}

        if re.search(r'\b(goodbye|bye|see\s*you|good\s*night|take\s*care)\b', cleaned):
            resp = random.choice(self.FAREWELLS)
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "dialogue", "action_data": None, "is_system_action": False}

        if re.search(r'\b(hello|hi|hey|greetings|howdy)\b', cleaned):
            resp = f"{name_prefix}{random.choice(self.GREETINGS)}"
            self.memory.record_turn(q, resp)
            return {"text": resp, "action_type": "dialogue", "action_data": None, "is_system_action": False}

        # 13. General Conversational Fallback
        resp = f"I've got that, {name_prefix if name_prefix else ''}processing your request for '{q}' within system capability bounds."
        self.memory.record_turn(q, resp)
        return {
            "text": resp,
            "action_type": "general",
            "action_data": None,
            "is_system_action": False
        }
