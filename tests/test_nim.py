import importlib.machinery
import importlib.util
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("harness_link_cli_nim", str(ROOT / "bin" / "harness-link"))
spec = importlib.util.spec_from_loader(loader.name, loader)
core = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = core
loader.exec_module(core)


class NimHarnessTests(unittest.TestCase):
    def setUp(self):
        self.provider = core.PROVIDERS["nim"]
        self.old_base = os.environ.get("NIM_BASE_URL")
        os.environ["NIM_BASE_URL"] = "https://nim.example/v1"

    def tearDown(self):
        if self.old_base is None:
            os.environ.pop("NIM_BASE_URL", None)
        else:
            os.environ["NIM_BASE_URL"] = self.old_base

    def test_provider_defaults(self):
        self.assertEqual(self.provider.default_model, "openai/gpt-oss-120b")
        self.assertEqual(self.provider.key_env, "NVIDIA_API_KEY")

    def test_opencode_config_preserves_existing_settings(self):
        existing = {"theme": "system", "provider": {"other": {"name": "Other"}}}
        config = core.opencode_config(self.provider, "openai/gpt-oss-120b", existing)
        self.assertEqual(config["theme"], "system")
        self.assertEqual(config["provider"]["other"]["name"], "Other")
        self.assertEqual(config["model"], "nim/openai/gpt-oss-120b")
        self.assertEqual(config["provider"]["nim"]["options"]["apiKey"], "{env:NVIDIA_API_KEY}")
        self.assertEqual(config["provider"]["nim"]["options"]["baseURL"], "https://nim.example/v1")

    def test_litellm_bridge_uses_custom_openai(self):
        config = core.litellm_config(self.provider, "openai/gpt-oss-120b")
        self.assertIn("drop_params: true", config)
        self.assertIn("custom_openai/openai/gpt-oss-120b", config)
        self.assertIn("api_key: os.environ/NVIDIA_API_KEY", config)
        self.assertNotIn(os.environ.get("NVIDIA_API_KEY", "secret-that-should-not-appear"), config)


if __name__ == "__main__":
    unittest.main()
