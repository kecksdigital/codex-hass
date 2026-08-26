import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


CODEX_DIR = Path(__file__).resolve().parents[1]
START_SCRIPT = CODEX_DIR / "rootfs/usr/local/bin/codex-start"
MERGE_CONFIG = CODEX_DIR / "rootfs/usr/local/bin/codex-merge-config"


class BundledMcpOptionTests(unittest.TestCase):
    def test_explicit_false_is_not_replaced_by_default(self):
        start_text = START_SCRIPT.read_text(encoding="utf-8")

        self.assertNotIn(".enable_mcp // true", start_text)
        result = subprocess.run(
            ["jq", "-r", ".enable_mcp"],
            input=json.dumps({"enable_mcp": False}),
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "false")

    def test_disabling_bundled_mcp_removes_managed_server(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.toml"

            enabled = subprocess.run(
                [sys.executable, MERGE_CONFIG, config_path, "", "true", "workspace", "on-request"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(enabled.returncode, 0, enabled.stderr)
            self.assertIn(
                "homeassistant",
                tomllib.loads(config_path.read_text(encoding="utf-8"))["mcp_servers"],
            )

            disabled = subprocess.run(
                [sys.executable, MERGE_CONFIG, config_path, "", "false", "workspace", "on-request"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(disabled.returncode, 0, disabled.stderr)
            config = tomllib.loads(config_path.read_text(encoding="utf-8"))
            self.assertNotIn("mcp_servers", config)
            self.assertNotIn(
                "managed_homeassistant_mcp",
                config.get("__homeassistant_app", {}),
            )


if __name__ == "__main__":
    unittest.main()
