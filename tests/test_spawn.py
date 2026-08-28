import importlib.machinery
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("albert_spawn", str(ROOT / "bin" / "albert-spawn"))
spec = importlib.util.spec_from_loader(loader.name, loader)
spawn = importlib.util.module_from_spec(spec)
loader.exec_module(spawn)


class AlbertSpawnTests(unittest.TestCase):
    def test_default_model_is_added_to_supported_agents(self):
        args = spawn.with_default_model(["opencode", "gcp"])
        self.assertEqual(args[-2:], ["--model", "deepseek-v4-flash"])

    def test_explicit_model_is_preserved(self):
        args = ["hermes", "hetzner", "--model", "other-model"]
        self.assertEqual(spawn.with_default_model(args), args)

    def test_meta_commands_are_unchanged(self):
        args = ["matrix"]
        self.assertEqual(spawn.with_default_model(args), args)

    def test_oauth_patch_prefers_albert_key(self):
        source = '''export async function getOrPromptApiKey(agentSlug?: string, cloudSlug?: string): Promise<string> {
  process.stderr.write("\\n");
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oauth.ts"
            path.write_text(source)
            spawn.patch_oauth(path)
            patched = path.read_text()
        self.assertIn("process.env.ALBERT_API_KEY", patched)
        self.assertIn("return process.env.ALBERT_API_KEY", patched)

    def test_sandbox_defaults_workspace_to_current_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                args, workspace = spawn.extract_workspace(["opencode", "sandbox"])
            finally:
                os.chdir(old_cwd)
        self.assertEqual(args, ["opencode", "sandbox"])
        self.assertEqual(workspace, str(Path(tmp).resolve()))

    def test_explicit_workspace_is_removed_before_spawn(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, workspace = spawn.extract_workspace(
                ["hermes", "sandbox", "--workspace", tmp, "--fast"]
            )
        self.assertEqual(args, ["hermes", "sandbox", "--fast"])
        self.assertEqual(workspace, str(Path(tmp).resolve()))

    def test_workspace_rejected_outside_sandbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                spawn.extract_workspace(["opencode", "gcp", "--workspace", tmp])

    def test_spawn_bridge_uses_custom_openai(self):
        source = (ROOT / "bin" / "albert-spawn").read_text()
        self.assertIn("model: custom_openai/${model}", source)
        self.assertIn("drop_params: true", source)


if __name__ == "__main__":
    unittest.main()
