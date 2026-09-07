import os
import json
import time

class MemoryStore:
    """
    Persistent Contextual Memory Engine for JARVIS.
    Maintains multi-turn context, user profile preferences, and dialogue history.
    """

    MEMORY_FILE = os.path.join(os.path.expanduser("~"), ".aura_memory.json")

    def __init__(self):
        self.profile = {
            "user_name": None,
            "preferred_workspace": "Development",
            "voice_personality": "ChristopherNeural",
            "interests": [],
            "custom_preferences": {}
        }
        self.history = []
        self.load()

    def load(self):
        if os.path.exists(self.MEMORY_FILE):
            try:
                with open(self.MEMORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.profile.update(data.get("profile", {}))
                    self.history = data.get("history", [])[-20:] # Keep last 20 turns
            except Exception:
                pass

    def save(self):
        try:
            data = {
                "profile": self.profile,
                "history": self.history[-20:],
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            with open(self.MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def record_turn(self, user_msg: str, jarvis_msg: str):
        self.history.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "user": user_msg,
            "jarvis": jarvis_msg
        })
        self.save()

    def get_last_topic(self) -> str:
        if self.history:
            return self.history[-1]["user"]
        return "general system operations"

    def set_user_name(self, name: str):
        self.profile["user_name"] = name.strip().title()
        self.save()

    def get_user_name(self) -> str:
        return self.profile.get("user_name")

    def clear(self):
        self.history.clear()
        self.profile = {
            "user_name": None,
            "preferred_workspace": "Development",
            "voice_personality": "ChristopherNeural",
            "interests": [],
            "custom_preferences": {}
        }
        self.save()
