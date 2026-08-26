# ttyd mobile key bar

The Codex App uses a customized HTML frontend built from ttyd 1.7.7. The
generated, self-contained frontend is installed at
`rootfs/usr/share/ttyd/mobile-index.html`; ttyd serves it through its `--index`
option.

`ttyd-1.7.7-mobile-keys.patch` contains the source changes. It adds the mobile
key bar, sends terminal escape sequences through ttyd's existing WebSocket,
implements one-shot `Ctrl` and `Alt` modifiers for both key-bar and software-
keyboard input, and converts vertical touch gestures into page navigation. The
App's tmux configuration maps those page controls to copy mode when persistent
sessions are enabled.

To regenerate the bundled frontend:

```bash
git clone --depth 1 --branch 1.7.7 https://github.com/tsl0922/ttyd.git /tmp/ttyd-1.7.7
git -C /tmp/ttyd-1.7.7 apply /path/to/ttyd-1.7.7-mobile-keys.patch
cd /tmp/ttyd-1.7.7/html
corepack enable
yarn install --immutable
yarn check
yarn build
cp dist/inline.html /path/to/codex/rootfs/usr/share/ttyd/mobile-index.html
```

The customized frontend remains covered by ttyd's MIT license, included beside
this file.
