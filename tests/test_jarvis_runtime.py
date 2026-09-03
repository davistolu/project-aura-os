import unittest
import time

class ModelRouter:
    def __init__(self, allow_cloud=True, force_offline=False):
        self.allow_cloud = allow_cloud
        self.force_offline = force_offline

    def route(self, query):
        q = query.strip().lower()
        if q.startswith("open ") or q.startswith("launch "):
            return {"type": "deterministic", "cmd": "app_launch", "target": q.split()[1]}
        if q.startswith("switch workspace "):
            return {"type": "deterministic", "cmd": "workspace_switch", "target": q.split()[-1]}
        if q in ["status", "doctor", "hardware"]:
            return {"type": "deterministic", "cmd": "sys_hardware_inspect", "target": None}
        if self.force_offline or not self.allow_cloud:
            return {"type": "local_slm", "model": "llama3.2:3b"}
        if len(q) > 100 or "refactor" in q or "architect" in q:
            return {"type": "cloud_llm", "model": "claude-3-5-sonnet"}
        return {"type": "local_slm", "model": "llama3.2:3b"}

class MemoryEngine:
    def __init__(self):
        self.working = {}
        self.session = []
        self.preferences = {}

    def set_preference(self, key, value):
        self.preferences[key] = value

    def get_preference(self, key):
        return self.preferences.get(key)

    def reset_all(self):
        self.working.clear()
        self.session.clear()
        self.preferences.clear()

class TestJarvisRuntime(unittest.TestCase):
    def test_deterministic_router_fast_path(self):
        router = ModelRouter()
        decision = router.route("open firefox")
        self.assertEqual(decision["type"], "deterministic")
        self.assertEqual(decision["cmd"], "app_launch")
        self.assertEqual(decision["target"], "firefox")

    def test_offline_mode_router(self):
        router = ModelRouter(force_offline=True)
        decision = router.route("Explain quantum computing algorithms in detail")
        self.assertEqual(decision["type"], "local_slm")

    def test_cloud_router_complex_task(self):
        router = ModelRouter(allow_cloud=True, force_offline=False)
        decision = router.route("Architect a distributed transaction coordination layer")
        self.assertEqual(decision["type"], "cloud_llm")

    def test_memory_engine_isolation_and_purge(self):
        mem = MemoryEngine()
        mem.set_preference("editor_theme", "aura-dark")
        self.assertEqual(mem.get_preference("editor_theme"), "aura-dark")

        mem.reset_all()
        self.assertIsNone(mem.get_preference("editor_theme"))

if __name__ == "__main__":
    unittest.main()
