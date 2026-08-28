import importlib.machinery
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
