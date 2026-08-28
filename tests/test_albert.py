import importlib.machinery
import importlib.util
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("albert_cli", str(ROOT / "bin" / "albert"))
spec = importlib.util.spec_from_loader(loader.name, loader)
albert = importlib.util.module_from_spec(spec)
loader.exec_module(albert)


class AlbertHarnessTests(unittest.TestCase):
    def setUp(self):
        self.old_base = albert.API_BASE
        albert.API_BASE = "https://albert.example/v1"

    def tearDown(self):
        albert.API_BASE = self.old_base

    def test_opencode_config_preserves_existing_settings(self):
        existing = {"theme": "system", "provider": {"other": {"name": "Other"}}}
        config = albert.opencode_config("deepseek-v4-flash", existing)
        self.assertEqual(config["theme"], "system")
        self.assertEqual(config["provider"]["other"]["name"], "Other")
        self.assertEqual(config["model"], "albert/deepseek-v4-flash")
        self.assertEqual(
            config["provider"]["albert"]["options"]["apiKey"],
            "{env:ALBERT_API_KEY}",
        )
        self.assertEqual(
            config["provider"]["albert"]["models"]["deepseek-v4-flash"]["limit"]["context"],
            131072,
        )

    def test_litellm_bridge_keeps_secret_out_of_config(self):
        config = albert.litellm_config("deepseek-v4-flash")
        self.assertIn("openai/chat_completions/deepseek-v4-flash", config)
        self.assertIn("api_key: os.environ/ALBERT_API_KEY", config)
        self.assertNotIn(os.environ.get("ALBERT_API_KEY", "secret-that-should-not-appear"), config)


if __name__ == "__main__":
    unittest.main()
