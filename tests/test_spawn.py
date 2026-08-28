import os
from pathlib import Path
import tempfile
from unittest import TestCase, mock

from harness_link import spawn
from harness_link.providers import PROVIDERS


class SpawnTests(TestCase):
    def test_default_model_is_added(self):
        provider = PROVIDERS["albert"]
        args = spawn.with_default_model(provider, ["opencode", "gcp"])
        self.assertEqual(args[-2:], ["--model", "deepseek-v4-flash"])

    def test_orfree_explicit_paid_model_is_rejected(self):
        provider = PROVIDERS["orfree"]
        with self.assertRaises(SystemExit):
            spawn.with_default_model(provider, ["opencode", "gcp", "--model", "paid/model"])

    def test_orfree_uses_dynamic_model(self):
        provider = PROVIDERS["orfree"]
        with mock.patch("harness_link.spawn.resolve_model", return_value="minimax/minimax-m3:free"):
            args = spawn.with_default_model(provider, ["opencode", "sandbox"])
        self.assertEqual(args[-2:], ["--model", "minimax/minimax-m3:free"])

    def test_orfree_keeps_upstream_openrouter_agent_setup(self):
        self.assertTrue(PROVIDERS["orfree"].spawn_native)

    def test_oauth_patch_prefers_albert_key(self):
        provider = PROVIDERS["albert"]
        source = '''export async function getOrPromptApiKey(agentSlug?: string, cloudSlug?: string): Promise<string> {\n  process.stderr.write("\\n");\n}\n'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oauth.ts"
            path.write_text(source)
            spawn.patch_oauth(provider, path)
            patched = path.read_text()
        self.assertIn("process.env.ALBERT_API_KEY", patched)

    def test_sandbox_defaults_workspace_to_current_directory(self):
        provider = PROVIDERS["albert"]
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                args, workspace = spawn.extract_workspace(provider, ["opencode", "sandbox"])
            finally:
                os.chdir(old_cwd)
        self.assertEqual(args, ["opencode", "sandbox"])
        self.assertEqual(workspace, str(Path(tmp).resolve()))

    def test_sandbox_patch_uses_shared_workspace_env(self):
        provider = PROVIDERS["nim"]
        source = '''  await runLocalArgs([\n    "docker",\n    "run",\n    "-d",\n    "--name",\n    DOCKER_CONTAINER_NAME,\n    image,\n  ]);'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "local.ts"
            path.write_text(source)
            spawn.patch_sandbox(provider, path)
            patched = path.read_text()
        self.assertIn("process.env.HARNESS_LINK_WORKSPACE", patched)
        self.assertIn(":/workspace", patched)
