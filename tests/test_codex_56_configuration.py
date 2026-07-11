#!/usr/bin/env python3
"""Configuration contract for the Codex 5.6 Home Assistant App."""

from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


class Codex56ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.config = yaml.safe_load((ROOT / "codex/config.yaml").read_text())
        self.start = (ROOT / "codex/rootfs/usr/local/bin/codex-start").read_text()
        self.session = (ROOT / "codex/rootfs/usr/local/bin/codex-session").read_text()
        self.dockerfile = (ROOT / "codex/Dockerfile").read_text()
        self.merge = (ROOT / "codex/rootfs/usr/local/bin/codex-merge-config").read_text()

    def test_56_autonomous_role_defaults_are_provisioned(self):
        options = self.config["options"]
        self.assertEqual(options["default_model"], "gpt-5.6-sol")
        self.assertEqual(options["codex_permissions"], "full_access")
        self.assertEqual(options["codex_approval_policy"], "never")
        self.assertTrue(options["auto_update_codex"])
        self.assertTrue(options["run_as_root"])
        self.assertIn("run_as_root: bool", self._serialized_config())
        self.assertIn("CODEX_RUN_AS_ROOT", self.start)
        self.assertIn("CODEX_RUN_AS_ROOT", self.session)
        self.assertIn("profile-*.config.toml", self.session)

    def test_remote_control_is_not_advertised_for_the_linux_container(self):
        self.assertNotIn("codex_connection_mode", self._serialized_config())
        self.assertNotIn("CODEX_CONNECTION_MODE", self.start)
        self.assertNotIn("CODEX_CONNECTION_MODE", self.session)
        self.assertNotIn("remote-control", self.dockerfile)
        self.assertFalse((ROOT / "codex/rootfs/usr/local/bin/codex-remote-session").exists())

    def test_role_profiles_are_managed_and_selectable(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "config.toml"
            subprocess.run(
                [
                    "python3",
                    str(ROOT / "codex/rootfs/usr/local/bin/codex-merge-config"),
                    str(config_path),
                    "gpt-5.6-sol",
                    "true",
                    "full_access",
                    "never",
                ],
                check=True,
            )
            for profile, effort in (("sol", "xhigh"), ("terra", "high"), ("luna", "medium")):
                profile_file = config_path.parent / f"profile-{profile}.config.toml"
                self.assertTrue(profile_file.exists())
                self.assertIn('model = "gpt-5.6-sol"', profile_file.read_text())
                self.assertIn(f'model_reasoning_effort = "{effort}"', profile_file.read_text())

    def _serialized_config(self):
        return (ROOT / "codex/config.yaml").read_text()


if __name__ == "__main__":
    unittest.main()
