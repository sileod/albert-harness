import os
from unittest import TestCase

from harness_link import cli
from harness_link.providers import PROVIDERS


class NimHarnessTests(TestCase):
    def setUp(self):
        self.provider = PROVIDERS["nim"]
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

    def test_opencode_config(self):
        config = cli.opencode_config(self.provider, "openai/gpt-oss-20b")
        self.assertEqual(config["model"], "nim/openai/gpt-oss-20b")
        self.assertEqual(config["provider"]["nim"]["options"]["apiKey"], "{env:NVIDIA_API_KEY}")
        self.assertEqual(config["provider"]["nim"]["options"]["baseURL"], "https://nim.example/v1")

    def test_mini_preserves_full_nim_model_id(self):
        config = cli.mini_config(self.provider, "openai/gpt-oss-20b")
        self.assertIn('model_name: "openai/openai/gpt-oss-20b"', config)
        self.assertIn('api_base: "https://nim.example/v1"', config)
