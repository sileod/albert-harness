import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("nim_spawn", str(ROOT / "bin" / "nim-spawn"))
spec = importlib.util.spec_from_loader(loader.name, loader)
spawn = importlib.util.module_from_spec(spec)
loader.exec_module(spawn)


class NimSpawnTests(unittest.TestCase):
    def test_default_model_is_added_to_supported_agents(self):
        args = spawn.with_default_model(["opencode", "gcp"])
        self.assertEqual(args[-2:], ["--model", "openai/gpt-oss-120b"])

    def test_explicit_model_is_preserved(self):
        args = ["hermes", "hetzner", "--model", "other-model"]
        self.assertEqual(spawn.with_default_model(args), args)

    def test_meta_commands_are_unchanged(self):
        self.assertEqual(spawn.with_default_model(["matrix"]), ["matrix"])

    def test_oauth_patch_prefers_nvidia_key(self):
        source = '''export async function getOrPromptApiKey(agentSlug?: string, cloudSlug?: string): Promise<string> {
  process.stderr.write("\\n");
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oauth.ts"
            path.write_text(source)
            spawn.patch_oauth(path)
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
            spawn.patch_sandbox(path)
            patched = path.read_text()
        self.assertIn("process.env.NIM_WORKSPACE", patched)
        self.assertIn(":/workspace", patched)
        self.assertIn('"-w", "/workspace"', patched)

    def test_bridge_patch_uses_custom_openai(self):
        source = "// ─── Default Agent Definitions ───────────────────────────────────────────────\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent-setup.ts"
            path.write_text(source)
            with self.assertRaises(SystemExit):
                spawn.patch_agent_setup(path)
            patched = path.read_text()
        self.assertIn("custom_openai/", patched)
        self.assertIn("NVIDIA_API_KEY", patched)


if __name__ == "__main__":
    unittest.main()
