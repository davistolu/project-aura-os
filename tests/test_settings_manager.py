import unittest
import os
import sys
import tempfile
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from settings_manager import SettingsManager

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.temp_file = os.path.join(tempfile.gettempdir(), f"aura_test_settings_{os.getpid()}.json")
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.mgr = SettingsManager(config_file=self.temp_file)

    def tearDown(self):
        if os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except Exception:
                pass

    def test_default_settings_loaded(self):
        self.assertIn("wifi", self.mgr.settings)
        self.assertIn("bluetooth", self.mgr.settings)
        self.assertIn("power", self.mgr.settings)
        self.assertIn("resources", self.mgr.settings)
        self.assertIn("network", self.mgr.settings)
        self.assertEqual(self.mgr.settings["power"]["active_mode"], "Balanced")

    def test_wifi_scan_and_connect(self):
        networks = self.mgr.scan_wifi()
        self.assertIsInstance(networks, list)
        self.assertGreater(len(networks), 0)

        # Connect to specific network
        res = self.mgr.connect_wifi("Aura-Studio-5G")
        self.assertTrue(res["success"])
        self.assertEqual(self.mgr.settings["wifi"]["connected_ssid"], "Aura-Studio-5G")

        # Disconnect
        disc_res = self.mgr.disconnect_wifi()
        self.assertTrue(disc_res["success"])
        self.assertIsNone(self.mgr.settings["wifi"]["connected_ssid"])

    def test_bluetooth_toggle_and_connect(self):
        self.mgr.set_bluetooth_state(False)
        self.assertFalse(self.mgr.settings["bluetooth"]["enabled"])

        self.mgr.set_bluetooth_state(True)
        self.assertTrue(self.mgr.settings["bluetooth"]["enabled"])

        res = self.mgr.connect_bluetooth_device("Sony WH-1000XM5")
        self.assertTrue(res["success"])
        self.assertEqual(res["device"]["name"], "Sony WH-1000XM5")

    def test_power_mode_switching(self):
        res = self.mgr.set_power_mode("Performance")
        self.assertTrue(res["success"])
        self.assertEqual(self.mgr.settings["power"]["active_mode"], "Performance")
        self.assertEqual(self.mgr.settings["power"]["cpu_governor"], "performance")
        self.assertEqual(self.mgr.settings["power"]["display_refresh_rate_hz"], 144)

        res_save = self.mgr.set_power_mode("Power Saver")
        self.assertTrue(res_save["success"])
        self.assertEqual(self.mgr.settings["power"]["active_mode"], "Power Saver")
        self.assertEqual(self.mgr.settings["power"]["cpu_governor"], "powersave")

    def test_ram_resource_allocation(self):
        res_ai = self.mgr.set_ram_allocation("davis_ai", 8192)
        self.assertTrue(res_ai["success"])
        self.assertEqual(self.mgr.settings["resources"]["davis_ai_ram_limit_mb"], 8192)

        res_game = self.mgr.set_ram_allocation("gaming", 20480)
        self.assertTrue(res_game["success"])
        self.assertEqual(self.mgr.settings["resources"]["gaming_proton_ram_limit_mb"], 20480)

    def test_cpu_affinity_and_zram(self):
        res_aff = self.mgr.set_cpu_affinity("0-1", "2-15")
        self.assertTrue(res_aff["success"])
        self.assertEqual(self.mgr.settings["resources"]["pinned_os_cores"], "0-1")
        self.assertEqual(self.mgr.settings["resources"]["pinned_workload_cores"], "2-15")

        res_zram = self.mgr.set_zram_config(16, "zstd")
        self.assertTrue(res_zram["success"])
        self.assertEqual(self.mgr.settings["resources"]["zram_size_gb"], 16)
        self.assertEqual(self.mgr.settings["resources"]["zram_algorithm"], "zstd")

    def test_dns_and_latency(self):
        res_dns = self.mgr.set_dns("Cloudflare")
        self.assertTrue(res_dns["success"])
        self.assertEqual(self.mgr.settings["network"]["primary_dns"], "1.1.1.1")

        res_ping = self.mgr.test_latency_ping("127.0.0.1")
        self.assertTrue(res_ping["success"])

    def test_volume_clamping(self):
        res_vol = self.mgr.set_volume(85)
        self.assertTrue(res_vol["success"])
        self.assertEqual(self.mgr.settings["audio_display"]["master_volume_pct"], 85)

        # Clamping test
        self.mgr.set_volume(150)
        self.assertEqual(self.mgr.settings["audio_display"]["master_volume_pct"], 100)

        self.mgr.set_volume(-20)
        self.assertEqual(self.mgr.settings["audio_display"]["master_volume_pct"], 0)

    def test_json_persistence(self):
        self.mgr.set_power_mode("Gaming Boost")
        self.mgr.set_ram_allocation("ai", 6144)

        # Reload from same file
        reloaded = SettingsManager(config_file=self.temp_file)
        self.assertEqual(reloaded.settings["power"]["active_mode"], "Gaming Boost")
        self.assertEqual(reloaded.settings["resources"]["davis_ai_ram_limit_mb"], 6144)

if __name__ == "__main__":
    unittest.main()
