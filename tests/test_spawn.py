import importlib.machinery
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("harness_link_spawn", str(ROOT / "bin" / "harness-link-spawn"))
spec = importlib.util.spec_from_loader(loader.name, loader)
spawn = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = spawn
loader.exec_module(spawn)


class AlbertSpawnTests(unittest.TestCase):
    def setUp(self):
        self.provider = spawn.PROVIDERS["albert"]

    def test_default_model_is_added_to_supported_agents(self):
        args = spawn.with_default_model(self.provider, ["opencode", "gcp"])
        self.assertEqual(args[-2:], ["--model", "deepseek-v4-flash"])

    def test_explicit_model_is_preserved(self):
        args = ["hermes", "hetzner", "--model", "other-model"]
        self.assertEqual(spawn.with_default_model(self.provider, args), args)

    def test_meta_commands_are_unchanged(self):
        self.assertEqual(spawn.with_default_model(self.provider, ["matrix"]), ["matrix"])

    def test_oauth_patch_prefers_provider_key(self):
        source = '''export async function getOrPromptApiKey(agentSlug?: string, cloudSlug?: string): Promise<string> {
  process.stderr.write("\\n");
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oauth.ts"
            path.write_text(source)
            spawn.patch_oauth(self.provider, path)
            patched = path.read_text()
        self.assertIn("process.env.ALBERT_API_KEY", patched)
        self.assertIn("return process.env.ALBERT_API_KEY", patched)

    def test_sandbox_defaults_workspace_to_current_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                args, workspace = spawn.extract_workspace(self.provider, ["opencode", "sandbox"])
            finally:
                os.chdir(old_cwd)
        self.assertEqual(args, ["opencode", "sandbox"])
        self.assertEqual(workspace, str(Path(tmp).resolve()))

    def test_explicit_workspace_is_removed_before_spawn(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, workspace = spawn.extract_workspace(
                self.provider, ["hermes", "sandbox", "--workspace", tmp, "--fast"]
            )
        self.assertEqual(args, ["hermes", "sandbox", "--fast"])
        self.assertEqual(workspace, str(Path(tmp).resolve()))

    def test_workspace_rejected_outside_sandbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                spawn.extract_workspace(self.provider, ["opencode", "gcp", "--workspace", tmp])

    def test_provider_render_keeps_albert_limits(self):
        rendered = spawn.render("@@KEY_ENV@@ @@DEFAULT_MODEL@@ @@OPENCODE_LIMIT@@", self.provider)
        self.assertIn("ALBERT_API_KEY", rendered)
        self.assertIn("deepseek-v4-flash", rendered)
        self.assertIn("context: 131072", rendered)

    def test_sandbox_patch_uses_shared_workspace_env(self):
        source = '''  await runLocalArgs([
    "docker",
    "run",
    "-d",
    "--name",
    DOCKER_CONTAINER_NAME,
    image,
  ]);'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "local.ts"
            path.write_text(source)
            spawn.patch_sandbox(self.provider, path)
            patched = path.read_text()
        self.assertIn("process.env.HARNESS_LINK_WORKSPACE", patched)
        self.assertIn(":/workspace", patched)


if __name__ == "__main__":
    unittest.main()
