import importlib.machinery
import importlib.util
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("nim_cli", str(ROOT / "bin" / "nim"))
spec = importlib.util.spec_from_loader(loader.name, loader)
nim = importlib.util.module_from_spec(spec)
loader.exec_module(nim)


class NimHarnessTests(unittest.TestCase):
    def setUp(self):
        self.old_base = nim.API_BASE
        nim.API_BASE = "https://nim.example/v1"

    def tearDown(self):
        nim.API_BASE = self.old_base

    def test_default_model(self):
        self.assertEqual(nim.DEFAULT_MODEL, os.environ.get("NIM_MODEL", "openai/gpt-oss-120b"))

    def test_opencode_config_preserves_existing_settings(self):
        existing = {"theme": "system", "provider": {"other": {"name": "Other"}}}
        config = nim.opencode_config("openai/gpt-oss-120b", existing)
        self.assertEqual(config["theme"], "system")
        self.assertEqual(config["provider"]["other"]["name"], "Other")
        self.assertEqual(config["model"], "nim/openai/gpt-oss-120b")
        self.assertEqual(config["provider"]["nim"]["options"]["apiKey"], "{env:NVIDIA_API_KEY}")
        self.assertEqual(config["provider"]["nim"]["options"]["baseURL"], "https://nim.example/v1")

    def test_litellm_bridge_uses_custom_openai(self):
        config = nim.litellm_config("openai/gpt-oss-120b")
        self.assertIn("drop_params: true", config)
        self.assertIn("custom_openai/openai/gpt-oss-120b", config)
        self.assertIn("api_key: os.environ/NVIDIA_API_KEY", config)
        self.assertNotIn(os.environ.get("NVIDIA_API_KEY", "secret-that-should-not-appear"), config)


if __name__ == "__main__":
    unittest.main()
