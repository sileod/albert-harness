import importlib.machinery
import importlib.util
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("harness_link_cli", str(ROOT / "bin" / "harness-link"))
spec = importlib.util.spec_from_loader(loader.name, loader)
core = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = core
loader.exec_module(core)


class AlbertHarnessTests(unittest.TestCase):
    def setUp(self):
        self.provider = core.PROVIDERS["albert"]
        self.old_base = os.environ.get("ALBERT_BASE_URL")
        os.environ["ALBERT_BASE_URL"] = "https://albert.example/v1"

    def tearDown(self):
        if self.old_base is None:
            os.environ.pop("ALBERT_BASE_URL", None)
        else:
            os.environ["ALBERT_BASE_URL"] = self.old_base

    def test_provider_defaults(self):
        self.assertEqual(self.provider.default_model, "deepseek-v4-flash")
        self.assertEqual(self.provider.key_env, "ALBERT_API_KEY")

    def test_opencode_config_preserves_existing_settings(self):
        existing = {"theme": "system", "provider": {"other": {"name": "Other"}}}
        config = core.opencode_config(self.provider, "deepseek-v4-flash", existing)
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

    def test_litellm_bridge_uses_custom_openai(self):
        config = core.litellm_config(self.provider, "deepseek-v4-flash")
        self.assertIn("model: custom_openai/deepseek-v4-flash", config)
        self.assertIn("drop_params: true", config)
        self.assertIn("api_key: os.environ/ALBERT_API_KEY", config)
        self.assertNotIn(os.environ.get("ALBERT_API_KEY", "secret-that-should-not-appear"), config)


if __name__ == "__main__":
    unittest.main()
