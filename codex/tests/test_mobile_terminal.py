import unittest
from pathlib import Path


CODEX_DIR = Path(__file__).resolve().parents[1]
START_SCRIPT = CODEX_DIR / "rootfs/usr/local/bin/codex-start"
TTYD_MOBILE_INDEX = CODEX_DIR / "rootfs/usr/share/ttyd/mobile-index.html"
TTYD_PATCH = CODEX_DIR / "ttyd-mobile-keys/ttyd-1.7.7-mobile-keys.patch"
DOCKERFILE = CODEX_DIR / "Dockerfile"


class MobileTerminalTests(unittest.TestCase):
    def test_mobile_terminal_special_keys_are_bundled_and_enabled(self):
        start_text = START_SCRIPT.read_text(encoding="utf-8")
        index_text = TTYD_MOBILE_INDEX.read_text(encoding="utf-8")

        self.assertIn("--index /usr/share/ttyd/mobile-index.html", start_text)
        for label in (
            "Escape",
            "Tab",
            "Ctrl",
            "Alt",
            "Left arrow",
            "Down arrow",
            "Up arrow",
            "Right arrow",
            "Scroll one page up",
            "Scroll one page down",
        ):
            self.assertIn(label, index_text)
        self.assertIn("mobile-key--modifier", index_text)
        self.assertIn("changedTouches", index_text)
        self.assertIn("touch-action:none", index_text)

    def test_tmux_page_keys_control_copy_mode(self):
        dockerfile_text = DOCKERFILE.read_text(encoding="utf-8")

        self.assertIn("bind -n PPage copy-mode", dockerfile_text)
        self.assertIn("bind -n NPage if-shell", dockerfile_text)
        self.assertIn("bind -T copy-mode PPage", dockerfile_text)
        self.assertIn("bind -T copy-mode-vi PPage", dockerfile_text)

    def test_web_terminal_preserves_codex_scrollback(self):
        shell_text = (CODEX_DIR / "rootfs/usr/local/bin/codex-shell").read_text(
            encoding="utf-8"
        )

        self.assertIn("tui.alternate_screen", shell_text)
        self.assertIn('"never"', shell_text)

    def test_ttyd_patch_source_and_license_are_included(self):
        self.assertTrue(TTYD_PATCH.is_file())
        self.assertTrue((CODEX_DIR / "ttyd-mobile-keys/LICENSE").is_file())
        self.assertTrue((CODEX_DIR / "ttyd-mobile-keys/README.md").is_file())


if __name__ == "__main__":
    unittest.main()
