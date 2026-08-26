import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


CODEX_DIR = Path(__file__).resolve().parents[1]
PREPARE_MCP = CODEX_DIR / "rootfs/usr/local/bin/codex-prepare-mcp"
MERGE_CONFIG = CODEX_DIR / "rootfs/usr/local/bin/codex-merge-config"


class McpOptionsTests(unittest.TestCase):
    def run_prepare(self, directory, options):
        options_path = directory / "options.json"
        servers_path = directory / "servers.json"
        environment_path = directory / "environment.json"
        options_path.write_text(json.dumps(options), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, PREPARE_MCP, options_path, servers_path, environment_path],
            check=False,
            capture_output=True,
            text=True,
        )
        return result, servers_path, environment_path

    def test_prepares_remote_server_and_automatic_bearer_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            result, servers_path, environment_path = self.run_prepare(
                directory,
                {
                    "mcp_servers": [
                        {
                            "name": "example-cloud",
                            "url": "https://mcp.example.com/mcp",
                            "bearer_token": "secret-token",
                        }
                    ],
                    "environment_variables": [{"name": "EXAMPLE_TENANT", "value": "home"}],
                },
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(servers_path.read_text(encoding="utf-8")),
                [
                    {
                        "name": "example-cloud",
                        "url": "https://mcp.example.com/mcp",
                        "bearer_token_env_var": "CODEX_MCP_EXAMPLE_CLOUD_BEARER_TOKEN",
                    }
                ],
            )
            self.assertEqual(
                json.loads(environment_path.read_text(encoding="utf-8")),
                [
                    {"name": "EXAMPLE_TENANT", "value": "home"},
                    {"name": "CODEX_MCP_EXAMPLE_CLOUD_BEARER_TOKEN", "value": "secret-token"},
                ],
            )
            self.assertEqual(environment_path.stat().st_mode & 0o777, 0o600)
            self.assertNotIn("secret-token", servers_path.read_text(encoding="utf-8"))

    def test_rejects_environment_collision_with_generated_bearer_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            result, _, _ = self.run_prepare(
                directory,
                {
                    "mcp_servers": [
                        {"name": "example", "url": "https://example.com/mcp", "bearer_token": "secret"}
                    ],
                    "environment_variables": [
                        {"name": "CODEX_MCP_EXAMPLE_BEARER_TOKEN", "value": "other"}
                    ],
                },
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("conflicts", result.stderr)


class McpMergeTests(unittest.TestCase):
    def run_merge(self, config_path, servers_path):
        return subprocess.run(
            [
                sys.executable,
                MERGE_CONFIG,
                config_path,
                "",
                "true",
                "workspace",
                "on-request",
                servers_path,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_adds_managed_server_without_secret_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            config_path = directory / "config.toml"
            servers_path = directory / "servers.json"
            servers_path.write_text(
                json.dumps(
                    [
                        {
                            "name": "example",
                            "url": "https://example.com/mcp",
                            "bearer_token_env_var": "CODEX_MCP_EXAMPLE_BEARER_TOKEN",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            result = self.run_merge(config_path, servers_path)

            self.assertEqual(result.returncode, 0, result.stderr)
            config_text = config_path.read_text(encoding="utf-8")
            config = tomllib.loads(config_text)
            self.assertEqual(config["mcp_servers"]["example"]["url"], "https://example.com/mcp")
            self.assertEqual(
                config["mcp_servers"]["example"]["bearer_token_env_var"],
                "CODEX_MCP_EXAMPLE_BEARER_TOKEN",
            )
            self.assertNotIn("secret", config_text)

    def test_restores_preexisting_same_name_server_when_management_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            config_path = directory / "config.toml"
            servers_path = directory / "servers.json"
            config_path.write_text(
                '[mcp_servers.example]\ncommand = "original-command"\nargs = ["serve"]\n',
                encoding="utf-8",
            )
            servers_path.write_text(
                json.dumps([{"name": "example", "url": "https://example.com/mcp"}]),
                encoding="utf-8",
            )

            first_result = self.run_merge(config_path, servers_path)
            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            managed_config = tomllib.loads(config_path.read_text(encoding="utf-8"))
            self.assertNotIn("command", managed_config["mcp_servers"]["example"])

            servers_path.write_text("[]\n", encoding="utf-8")
            second_result = self.run_merge(config_path, servers_path)

            self.assertEqual(second_result.returncode, 0, second_result.stderr)
            restored_config = tomllib.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(restored_config["mcp_servers"]["example"]["command"], "original-command")
            self.assertEqual(restored_config["mcp_servers"]["example"]["args"], ["serve"])


if __name__ == "__main__":
    unittest.main()
