import unittest
from pathlib import Path

import yaml


CODEX_DIR = Path(__file__).resolve().parents[1]
CONFIG = CODEX_DIR / "config.yaml"
DOCKERFILE = CODEX_DIR / "Dockerfile"
APPARMOR = CODEX_DIR / "apparmor.txt"
SSHD_CONFIG = CODEX_DIR / "rootfs/etc/ssh/sshd_config"
PROFILE = CODEX_DIR / "rootfs/etc/profile.d/codex.sh"
START_SCRIPT = CODEX_DIR / "rootfs/usr/local/bin/codex-start"


class SshConfigurationTests(unittest.TestCase):
    def test_app_exposes_disabled_by_default_ssh_options(self):
        config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

        self.assertIsNone(config["ports"]["22/tcp"])
        self.assertFalse(config["options"]["ssh_enabled"])
        self.assertEqual(config["options"]["ssh_password"], "")
        self.assertEqual(config["options"]["authorized_keys"], [])
        self.assertEqual(config["schema"]["ssh_password"], "password")

    def test_sshd_is_restricted_to_unprivileged_codex_user(self):
        sshd = SSHD_CONFIG.read_text(encoding="utf-8")

        for directive in (
            "PermitRootLogin no",
            "AllowUsers codex",
            "PermitEmptyPasswords no",
            "X11Forwarding no",
            "AllowAgentForwarding no",
            "AllowTcpForwarding no",
            "AllowStreamLocalForwarding no",
            "DisableForwarding yes",
            "PermitTunnel no",
            "PermitUserEnvironment no",
            "PermitUserRC no",
        ):
            self.assertIn(directive, sshd)

    def test_image_and_apparmor_include_only_required_ssh_runtime(self):
        dockerfile = DOCKERFILE.read_text(encoding="utf-8")
        apparmor = APPARMOR.read_text(encoding="utf-8")

        self.assertIn("openssh-server", dockerfile)
        self.assertIn("capability net_bind_service,", apparmor)
        self.assertIn("capability sys_chroot,", apparmor)
        self.assertIn("/run/sshd/** rwk,", apparmor)

    def test_ssh_sessions_preserve_mcp_state_and_safe_logging(self):
        profile = PROFILE.read_text(encoding="utf-8")
        start = START_SCRIPT.read_text(encoding="utf-8")

        self.assertNotIn(".enable_mcp // true", profile)
        self.assertIn('CODEX_MCP_ENVIRONMENT=/data/codex-managed/mcp-environment.json', profile)
        self.assertIn('.data.network["22/tcp"] // empty', start)
        self.assertIn("host port ${ssh_host_port} (mapped to container port 22)", start)
        self.assertIn("chpasswd >/dev/null 2>&1", start)


if __name__ == "__main__":
    unittest.main()
