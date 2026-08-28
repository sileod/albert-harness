import os
from unittest import TestCase

from harness_link import cli
from harness_link.providers import PROVIDERS


class AlbertHarnessTests(TestCase):
    def setUp(self):
        self.provider = PROVIDERS["albert"]
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
        config = cli.opencode_config(self.provider, "deepseek-v4-flash", existing)
        self.assertEqual(config["theme"], "system")
        self.assertEqual(config["provider"]["other"]["name"], "Other")
        self.assertEqual(config["model"], "albert/deepseek-v4-flash")
        self.assertEqual(config["provider"]["albert"]["options"]["apiKey"], "{env:ALBERT_API_KEY}")
        self.assertEqual(
            config["provider"]["albert"]["models"]["deepseek-v4-flash"]["limit"]["context"],
            131072,
        )

    def test_litellm_bridge_forces_chat_completions(self):
        config = cli.litellm_config(self.provider, "deepseek-v4-flash")
        self.assertIn('model: "openai/deepseek-v4-flash"', config)
        self.assertIn("use_chat_completions_api: true", config)
        self.assertIn("drop_params: true", config)
        self.assertIn("api_key: os.environ/ALBERT_API_KEY", config)

    def test_mini_config_is_direct_and_secret_free(self):
        config = cli.mini_config(self.provider, "deepseek-v4-flash")
        self.assertIn('model_name: "openai/deepseek-v4-flash"', config)
        self.assertIn('api_base: "https://albert.example/v1"', config)
        self.assertIn('cost_tracking: "ignore_errors"', config)
        self.assertNotIn("ALBERT_API_KEY", config)
