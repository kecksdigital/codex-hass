import unittest
from pathlib import Path


CODEX_DIR = Path(__file__).resolve().parents[1]
START_SCRIPT = CODEX_DIR / "rootfs/usr/local/bin/codex-start"
SHELL_SCRIPT = CODEX_DIR / "rootfs/usr/local/bin/codex-shell"
APPARMOR_PROFILE = CODEX_DIR / "apparmor.txt"


class CliUpdateTests(unittest.TestCase):
    def test_startup_update_uses_persistent_unprivileged_prefix(self):
        start_text = START_SCRIPT.read_text(encoding="utf-8")

        self.assertIn('update_user_root="$CODEX_STATE_ROOT/users/anonymous"', start_text)
        self.assertIn('update_npm_prefix="$update_user_root/.local"', start_text)
        self.assertIn("su-exec 22000:0 env", start_text)
        self.assertIn('"NPM_CONFIG_PREFIX=$update_npm_prefix"', start_text)
        self.assertNotIn("npm-root-cache", start_text)

    def test_persistent_cli_is_executable_under_apparmor(self):
        profile_text = APPARMOR_PROFILE.read_text(encoding="utf-8")

        self.assertIn("/data/codex-home/users/*/.local/bin/** ixr,", profile_text)
        self.assertIn(
            "/data/codex-home/users/*/.local/lib/node_modules/** ixmr,",
            profile_text,
        )

    def test_broken_persisted_update_falls_back_to_image_cli(self):
        shell_text = SHELL_SCRIPT.read_text(encoding="utf-8")

        self.assertIn('codex_status" -eq 126', shell_text)
        self.assertIn('codex_command="/usr/local/bin/codex"', shell_text)


if __name__ == "__main__":
    unittest.main()
