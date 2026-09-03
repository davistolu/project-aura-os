import unittest

class TestCompatDatabase(unittest.TestCase):
    def setUp(self):
        self.db = {
            "cyberpunk2077": {"tier": "ProtonDirect", "dxvk": True, "vkd3d": True},
            "notepadplusplus": {"tier": "WineStaging", "dxvk": False, "vkd3d": False},
            "proprietary_kernel_app": {"tier": "KvmVmFallback", "dxvk": False, "vkd3d": False},
        }

    def test_proton_game_profile(self):
        entry = self.db.get("cyberpunk2077")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["tier"], "ProtonDirect")
        self.assertTrue(entry["dxvk"])

    def test_wine_desktop_app_profile(self):
        entry = self.db.get("notepadplusplus")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["tier"], "WineStaging")

    def test_vm_fallback_selection(self):
        entry = self.db.get("proprietary_kernel_app")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["tier"], "KvmVmFallback")

if __name__ == "__main__":
    unittest.main()
