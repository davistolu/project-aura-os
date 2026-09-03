import unittest
import json
import os
import tempfile

class TestPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.granted_capabilities = {
            "system.hardware.read",
            "system.process.list",
            "filesystem.read[*]",
            "workspace.manage",
            "notification.send"
        }
        self.secret_vault = {
            "github_token": "ghp_super_secret_token_1234567890",
            "db_pass": "super_secret_db_pass_987654"
        }

    def evaluate_tool_request(self, tool_name, capability, tier, arguments):
        # 1. Scan for leaked secrets
        args_str = json.dumps(arguments)
        for name, secret in self.secret_vault.items():
            if secret in args_str:
                return {"status": "ERROR_SECRET_LEAK", "error": f"Plaintext secret for '{name}' detected"}

        # 2. Check capability
        if capability not in self.granted_capabilities:
            return {"status": "DENIED", "error": f"Capability '{capability}' not granted"}

        # 3. Check tier approval
        if tier in ["SUGGEST", "EXECUTE_PRIVILEGED"]:
            return {"status": "APPROVAL_REQUIRED", "tier": tier}

        return {"status": "ALLOWED"}

    def test_safe_read_hardware(self):
        res = self.evaluate_tool_request(
            "sys_hardware_inspect",
            "system.hardware.read",
            "OBSERVE",
            {}
        )
        self.assertEqual(res["status"], "ALLOWED")

    def test_unauthorized_capability_blocked(self):
        res = self.evaluate_tool_request(
            "dangerous_package_install",
            "package.manage",
            "EXECUTE_PRIVILEGED",
            {"pkg": "malware"}
        )
        self.assertEqual(res["status"], "DENIED")

    def test_privileged_requires_approval(self):
        res = self.evaluate_tool_request(
            "workspace_switch",
            "workspace.manage",
            "EXECUTE_PRIVILEGED",
            {"workspace": "gaming"}
        )
        self.assertEqual(res["status"], "APPROVAL_REQUIRED")

    def test_secret_leak_prevention(self):
        res = self.evaluate_tool_request(
            "notification_send",
            "notification.send",
            "EXECUTE_SAFE",
            {"title": "Alert", "body": "Token: ghp_super_secret_token_1234567890"}
        )
        self.assertEqual(res["status"], "ERROR_SECRET_LEAK")

if __name__ == "__main__":
    unittest.main()
