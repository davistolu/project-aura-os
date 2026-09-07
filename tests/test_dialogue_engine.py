import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from dialogue_engine import JarvisDialogueEngine

class TestDialogueEngine(unittest.TestCase):
    def setUp(self):
        self.engine = JarvisDialogueEngine()

    def test_greeting_response(self):
        res = self.engine.respond("Hello Jarvis")
        self.assertFalse(res["is_system_action"])
        self.assertTrue(any(w in res["text"].lower() for w in ["hello", "good day", "greetings", "assist", "online"]))

    def test_how_are_you_response(self):
        res = self.engine.respond("How are you doing today?")
        self.assertFalse(res["is_system_action"])
        self.assertTrue(len(res["text"]) > 10)

    def test_time_query(self):
        res = self.engine.respond("What time is it right now?")
        self.assertIn("The current time is", res["text"])

    def test_date_query(self):
        res = self.engine.respond("What day is today?")
        self.assertIn("Today is", res["text"])

    def test_math_calculation(self):
        res = self.engine.respond("What is 15 * 6?")
        self.assertIn("90", res["text"])

    def test_natural_gaming_intent(self):
        res = self.engine.respond("Hey Jarvis, let's play some games")
        self.assertTrue(res["is_system_action"])
        self.assertEqual(res["action_type"], "switch_workspace")
        self.assertEqual(res["action_data"], "3")

    def test_natural_coding_intent(self):
        res = self.engine.respond("Let's do some coding")
        self.assertTrue(res["is_system_action"])
        self.assertEqual(res["action_type"], "switch_workspace")
        self.assertEqual(res["action_data"], "2")

    def test_hardware_ram_query(self):
        res = self.engine.respond("How much RAM am I using?")
        self.assertTrue(res["is_system_action"])
        self.assertIn("RAM", res["text"])

    def test_voice_wifi_intent(self):
        res = self.engine.respond("Davis, connect to wifi Aura-Studio-5G")
        self.assertTrue(res["is_system_action"])
        self.assertEqual(res["action_type"], "wifi")
        self.assertIn("Aura-Studio-5G", res["text"])

    def test_voice_bluetooth_intent(self):
        res = self.engine.respond("Davis, turn on bluetooth")
        self.assertTrue(res["is_system_action"])
        self.assertEqual(res["action_type"], "bluetooth")
        self.assertIn("Bluetooth", res["text"])

    def test_voice_power_mode_intent(self):
        res = self.engine.respond("Davis, switch to performance mode")
        self.assertTrue(res["is_system_action"])
        self.assertEqual(res["action_type"], "power")
        self.assertIn("Performance", res["text"])

    def test_voice_ram_allocation_intent(self):
        res = self.engine.respond("Davis, allocate 8 gb of ram to ai")
        self.assertTrue(res["is_system_action"])
        self.assertEqual(res["action_type"], "resource_quota")
        self.assertIn("8192 MB", res["text"])

    def test_voice_dns_intent(self):
        res = self.engine.respond("Davis, set dns to cloudflare")
        self.assertTrue(res["is_system_action"])
        self.assertEqual(res["action_type"], "network_dns")
        self.assertIn("Cloudflare", res["text"])

if __name__ == "__main__":
    unittest.main()

