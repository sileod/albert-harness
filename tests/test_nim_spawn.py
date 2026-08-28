import importlib.machinery
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("harness_link_spawn_nim", str(ROOT / "bin" / "harness-link-spawn"))
spec = importlib.util.spec_from_loader(loader.name, loader)
spawn = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = spawn
loader.exec_module(spawn)


class NimSpawnTests(unittest.TestCase):
    def setUp(self):
        self.provider = spawn.PROVIDERS["nim"]

    def test_default_model_is_added_to_supported_agents(self):
        args = spawn.with_default_model(self.provider, ["opencode", "gcp"])
        self.assertEqual(args[-2:], ["--model", "openai/gpt-oss-120b"])

    def test_explicit_model_is_preserved(self):
        args = ["hermes", "hetzner", "--model", "other-model"]
        self.assertEqual(spawn.with_default_model(self.provider, args), args)

    def test_meta_commands_are_unchanged(self):
        self.assertEqual(spawn.with_default_model(self.provider, ["matrix"]), ["matrix"])

    def test_oauth_patch_prefers_nvidia_key(self):
        source = '''export async function getOrPromptApiKey(agentSlug?: string, cloudSlug?: string): Promise<string> {
  process.stderr.write("\\n");
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oauth.ts"
            path.write_text(source)
            spawn.patch_oauth(self.provider, path)
            patched = path.read_text()
        self.assertIn("process.env.NVIDIA_API_KEY", patched)
        self.assertIn("return process.env.NVIDIA_API_KEY", patched)

    def test_sandbox_patch_mounts_workspace(self):
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
        self.assertIn('"-w", "/workspace"', patched)

    def test_provider_render_has_no_albert_specific_model_limit(self):
        rendered = spawn.render("@@KEY_ENV@@ @@DEFAULT_MODEL@@ @@OPENCODE_LIMIT@@", self.provider)
        self.assertIn("NVIDIA_API_KEY", rendered)
        self.assertIn("openai/gpt-oss-120b", rendered)
        self.assertNotIn("context: 131072", rendered)


if __name__ == "__main__":
    unittest.main()
