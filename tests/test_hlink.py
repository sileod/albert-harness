import io
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from harness_link import hlink


class HlinkTests(TestCase):
    def test_headless_translation(self):
        cases = {
            "claude": ["--dangerously-skip-permissions", "-p", "review"],
            "codex": ["exec", "--dangerously-bypass-approvals-and-sandbox", "review"],
            "opencode": ["run", "--auto", "review"],
            "hermes": ["--yolo", "-z", "review"],
            "mini": ["--yolo", "-t", "review"],
            "agy": ["--dangerously-skip-permissions", "-p", "review"],
        }
        for harness, expected in cases.items():
            with self.subTest(harness=harness):
                self.assertEqual(hlink.harness_args(harness, prompt="review", yolo=True), expected)

    def test_model_and_native_args(self):
        self.assertEqual(
            hlink.harness_args("codex", prompt="review", model="gpt-test", extra_args=["--json"]),
            ["exec", "--model", "gpt-test", "--json", "review"],
        )

    def test_stdin_prompt(self):
        self.assertEqual(hlink.resolve_prompt("-", io.StringIO("review stdin")), "review stdin")

    def test_aliases(self):
        self.assertEqual(hlink.canonical_harness("claude-code"), "claude")
        self.assertEqual(hlink.canonical_harness("mini-swe-agent"), "mini")
        self.assertEqual(hlink.canonical_harness("antigravity"), "agy")

    def test_provider_delegation_keeps_model_at_provider_layer(self):
        with patch.object(hlink.provider_cli, "main") as provider_main:
            hlink.run_provider("albert", "opencode", "deepseek-test", ["run", "--auto", "review"])
        provider_main.assert_called_once_with(
            ["albert", "opencode", "--model", "deepseek-test", "--", "run", "--auto", "review"]
        )

    def test_agy_rejects_provider_override(self):
        with self.assertRaises(SystemExit) as ctx:
            hlink.run_provider("albert", "agy", None, ["-p", "review"])
        self.assertEqual(ctx.exception.code, 2)

    def test_cwd_changes_before_launch(self):
        old = Path.cwd()
        try:
            with TemporaryDirectory() as tmp, patch.object(hlink, "run_native") as run_native:
                hlink.main(["claude", "-C", tmp, "-p", "review"])
                self.assertEqual(Path.cwd(), Path(tmp))
                run_native.assert_called_once_with("claude", ["-p", "review"])
        finally:
            os.chdir(old)

    def test_unknown_normalized_option_is_not_forwarded(self):
        with self.assertRaises(SystemExit) as ctx:
            hlink.main(["claude", "--modle", "opus"])
        self.assertEqual(ctx.exception.code, 2)

    def test_explicit_separator_forwards_native_options(self):
        with patch.object(hlink, "run_native") as run_native:
            hlink.main(["agy", "-p", "review", "--", "--effort", "high"])
        run_native.assert_called_once_with("agy", ["--effort", "high", "-p", "review"])
