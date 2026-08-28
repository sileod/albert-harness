import io
import json
import os
from pathlib import Path
import tempfile
from unittest import TestCase, mock

from harness_link import cli
from harness_link import providers
from harness_link.providers import PROVIDERS


class _Response(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class OpenRouterFreeTests(TestCase):
    def setUp(self):
        self.provider = PROVIDERS["orfree"]
        self.old_key = os.environ.get("OPENROUTER_API_KEY")
        self.old_cache = os.environ.get("XDG_CACHE_HOME")
        self.old_model = os.environ.get("ORFREE_MODEL")
        os.environ["OPENROUTER_API_KEY"] = "test"
        os.environ.pop("ORFREE_MODEL", None)
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["XDG_CACHE_HOME"] = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()
        for name, value in [
            ("OPENROUTER_API_KEY", self.old_key),
            ("XDG_CACHE_HOME", self.old_cache),
            ("ORFREE_MODEL", self.old_model),
        ]:
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_fetch_free_models_filters_and_keeps_api_popularity_order(self):
        payload = {
            "data": [
                {
                    "id": "minimax/minimax-m3:free",
                    "pricing": {"prompt": "0", "completion": "0"},
                    "supported_parameters": ["tools", "temperature"],
                },
                {
                    "id": "paid/model",
                    "pricing": {"prompt": "0", "completion": "0.1"},
                    "supported_parameters": ["tools"],
                },
                {
                    "id": "free/no-tools:free",
                    "pricing": {"prompt": "0", "completion": "0"},
                    "supported_parameters": ["temperature"],
                },
                {
                    "id": "openai/gpt-oss-20b:free",
                    "pricing": {"prompt": 0, "completion": 0},
                    "supported_parameters": ["tools"],
                },
            ]
        }
        with mock.patch("urllib.request.urlopen", return_value=_Response(json.dumps(payload).encode())) as urlopen:
            models = providers.fetch_free_models(self.provider)
        self.assertEqual(models, ["minimax/minimax-m3:free", "openai/gpt-oss-20b:free"])
        url = urlopen.call_args.args[0].full_url
        self.assertIn("sort=most-popular", url)
        self.assertIn("supported_parameters=tools", url)
        self.assertIn("max_price=0", url)

    def test_auto_resolution_is_cached(self):
        with mock.patch.object(providers, "fetch_free_models", return_value=["minimax/minimax-m3:free"]):
            self.assertEqual(providers.resolve_model(self.provider), "minimax/minimax-m3:free")
        cache = Path(self.tmp.name) / "harness-link" / "orfree-model.json"
        self.assertTrue(cache.exists())
        with mock.patch.object(providers, "fetch_free_models", side_effect=AssertionError("should use cache")):
            self.assertEqual(providers.resolve_model(self.provider), "minimax/minimax-m3:free")

    def test_auto_resolution_falls_back_to_free_router(self):
        with mock.patch.object(providers, "fetch_free_models", side_effect=OSError("offline")):
            self.assertEqual(providers.resolve_model(self.provider), "openrouter/free")

    def test_paid_model_is_rejected(self):
        with self.assertRaises(ValueError):
            providers.resolve_model(self.provider, "anthropic/claude-sonnet-4")

    def test_openrouter_native_protocols(self):
        self.assertTrue(self.provider.direct_responses)
        self.assertTrue(self.provider.direct_messages)
        self.assertTrue(self.provider.spawn_native)

    def test_mini_config_uses_openai_compatible_transport(self):
        config = cli.mini_config(self.provider, "minimax/minimax-m3:free")
        self.assertIn('model_name: "openai/minimax/minimax-m3:free"', config)
        self.assertIn('api_base: "https://openrouter.ai/api/v1"', config)
        self.assertNotIn("OPENROUTER_API_KEY", config)
