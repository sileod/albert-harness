from unittest import TestCase

from harness_link import spawn
from harness_link.providers import PROVIDERS


class NimSpawnTests(TestCase):
    def test_nim_default_model(self):
        provider = PROVIDERS["nim"]
        args = spawn.with_default_model(provider, ["hermes", "hetzner"])
        self.assertEqual(args[-2:], ["--model", "openai/gpt-oss-120b"])

    def test_nim_render_has_no_albert_limit(self):
        provider = PROVIDERS["nim"]
        rendered = spawn.render("@@KEY_ENV@@ @@DEFAULT_MODEL@@ @@OPENCODE_LIMIT@@", provider)
        self.assertIn("NVIDIA_API_KEY", rendered)
        self.assertIn("openai/gpt-oss-120b", rendered)
        self.assertNotIn("context: 131072", rendered)
