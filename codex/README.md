# Codex App for Home Assistant

Codex App puts the OpenAI Codex CLI inside Home Assistant so you can inspect, edit, and troubleshoot your Home Assistant configuration from the sidebar.

It is designed as a Home Assistant-native App, not a copied terminal wrapper. The App prepares Codex with Home Assistant path guidance, safe starter defaults, optional Home Assistant MCP access, and persistent Codex state that survives restarts.

## How It Works

1. Home Assistant opens Codex through ingress.
2. `ttyd` serves a browser terminal on port `7681`.
3. The terminal starts in `/homeassistant`, which is the Home Assistant configuration folder inside this container.
4. Codex state is stored under `/data/codex-home/users/anonymous/.codex`.
5. The App generates user-level Codex defaults in `~/.codex/config.toml`.
6. The App generates `~/.codex/AGENTS.md` with Home Assistant path mapping, log commands, and MCP notes.
7. If MCP is enabled, Codex gets a managed `homeassistant` MCP server that talks to Home Assistant through `hass-mcp`.

The App keeps OpenAI credentials out of Home Assistant options. Codex signs in using its own CLI authentication flow and stores its own auth state in the persistent Codex home.

## Install

1. Add `https://github.com/kecksdigital/codex-hass` to the Home Assistant Add-on Store repositories.
2. Install **Codex**.
3. Review the App options.
4. Start Codex.
5. Open Codex from the Home Assistant sidebar.

The App is published as a prebuilt GitHub Container Registry image, so Home Assistant should download the image instead of compiling it on your Home Assistant machine.

## First Sign-In

When the terminal opens, Codex starts automatically.

If you have not authenticated yet, Codex asks you to sign in. The Codex CLI supports two normal paths:

- ChatGPT sign-in for subscription or workspace-based Codex access.
- OpenAI API key sign-in for usage billed through your OpenAI Platform account.

On Home Assistant OS, the browser callback flow may not always be reachable from the container. If the normal login flow does not complete, choose device-code login in Codex or run:

```bash
codex login --device-auth
```

Open the displayed URL on your phone or computer, enter the one-time code, and return to the Home Assistant terminal. Codex caches the login in the persistent Codex home so you should not need to sign in every time.

## Everyday Use

Use Codex as your Home Assistant working terminal:

```bash
codex
ha-config
ha-logs
```

The useful paths are:

| Path | Purpose | Access |
|------|---------|--------|
| `/homeassistant` | Home Assistant configuration | Read-write |
| `/share` | Shared Home Assistant files | Read-write |
| `/media` | Media files | Read-write |
| `/ssl` | SSL certificates | Read-only |
| `/backup` | Backups | Read-only |

When Codex or a prompt mentions `/config`, treat it as `/homeassistant` in this App.

## App Options

| Option | Default | What it does |
|--------|---------|--------------|
| `enable_mcp` | `true` | Adds the managed `homeassistant` MCP server to Codex |
| `terminal_font_size` | `14` | Sets terminal font size, clamped to `10-24` |
| `terminal_theme` | `dark` | Chooses the terminal color theme |
| `working_directory` | `/homeassistant` | Sets the starting folder |
| `session_persistence` | `false` | Reattaches terminal sessions through tmux when enabled |
| `default_model` | `gpt-5.4` | Writes the managed startup model for Codex |
| `codex_permissions` | `workspace` | Selects Codex local sandbox behavior |
| `codex_approval_policy` | `on-request` | Selects when Codex asks before running actions |
| `auto_update_codex` | `false` | Optionally updates Codex CLI at startup |
| `update_codex_cli` | `false` | Requests one Codex CLI update on the next add-on start |
| `codex_update_timeout` | `300` | Maximum seconds for the optional startup update |

## Models

The App starts with `gpt-5.4` because it is a practical default for Home Assistant work. This is only a default, not a lock.

Change models in either place:

- Set `default_model` in Home Assistant options for the persistent startup default.
- Use `/model` inside Codex for the current session.

Leave `default_model` blank if you want Codex to use its own default or if you manage the model in project config.

## Access Levels

`codex_permissions` writes Codex's `sandbox_mode` default:

| Option | Codex setting | Use when |
|--------|---------------|----------|
| `workspace` | `workspace-write` | Normal Home Assistant configuration work |
| `full_access` | `danger-full-access` | You deliberately want broad local access inside the container |

`full_access` does not grant access outside the container or outside the folders Home Assistant maps into this App. It does remove Codex's local workspace sandbox restrictions inside those available paths.

When `workspace` is selected, Codex uses its Linux sandbox runtime inside the App container. Version `0.2.14` includes `bubblewrap` for this path. If Home Assistant or the host still blocks sandbox creation, switch to `full_access` only if you deliberately want to bypass Codex's local sandbox.

## Approval Prompts and Autonomous Mode

`codex_approval_policy` controls whether Codex asks before running actions:

| Option | Codex setting | Behavior |
|--------|---------------|----------|
| `on-request` | `approval_policy = "on-request"` | Codex asks when it decides approval is needed |
| `untrusted` | `approval_policy = "untrusted"` | Trusted read-style commands run, higher-risk commands ask |
| `never` | `approval_policy = "never"` | Codex does not ask for approval before actions |

For autonomous operation, set:

```yaml
codex_permissions: full_access
codex_approval_policy: never
```

This is intentionally explicit. `full_access` removes the local sandbox and `never` removes action approval prompts. Only use both when you are comfortable letting Codex run commands inside the App container without per-action confirmation.

## Home Assistant MCP

When `enable_mcp` is `true`, the App registers a `homeassistant` MCP server in Codex. This lets Codex query entities, inspect state, read Home Assistant information, and call services through MCP tools.

The Supervisor token is not exported into the interactive shell. It is written to a protected runtime file and passed only through the helper path used by `hass-mcp`.

Disable MCP if you only want a terminal and file-editing workflow.

## Persistence

The persistent Codex home is:

```text
/data/codex-home/users/anonymous/.codex
```

That location stores Codex login state, generated user config, logs, and the generated Home Assistant `AGENTS.md`.

Project-specific Codex configuration belongs here:

```text
/homeassistant/.codex/config.toml
```

Project-specific instructions belong here:

```text
/homeassistant/AGENTS.md
```

Codex loads project config only after the project is trusted.

## Session Persistence

Session persistence is off by default because first-time authentication is usually simpler without tmux.

After Codex is authenticated, enable `session_persistence` if you want browser refreshes and disconnects to reattach to the same tmux session.

Useful tmux keys:

| Key | Action |
|-----|--------|
| `Ctrl+b d` | Detach and leave work running |
| `Ctrl+b [` | Enter scroll/copy mode |
| `q` | Exit scroll/copy mode |

If copying text behaves oddly while tmux is active, hold `Ctrl+Shift` while selecting text.

## Codex CLI Updates

The image installs Codex CLI during build. For predictable startup, the App does not auto-update Codex by default.

Enable `auto_update_codex` if you want the App to run this on startup:

```bash
npm install -g @openai/codex@latest
```

The update is bounded by `codex_update_timeout`. If the update fails or times out, the App continues with the image-installed Codex version and logs the failure.

To request a single manual update from the add-on configuration page, enable
`update_codex_cli`, save the options, and restart the Codex App. The App runs
the same bounded npm update once, logs the installed version or failure, and
records that the request was consumed. Disable the option after the restart;
to retry after a failure, save it as disabled first, then enable it again.

`update_codex_cli` is a one-shot request. `auto_update_codex` remains the
persistent setting for updating Codex at every App start.

When you run npm global installs from the interactive terminal, the App uses a persistent user-owned npm cache and prefix under the Codex user's home directory. That keeps `npm install -g @openai/codex@latest` writable for the unprivileged runtime user and makes the installed `codex` binary available on `PATH` in later sessions.

## Home Assistant App Updates

Home Assistant App updates are separate from Codex CLI updates.

The App version comes from `codex/config.yaml`. When a new version is pushed to this repository, the GitHub Actions workflow publishes matching images to:

```text
ghcr.io/kecksdigital/codex-hass:<version>
```

Home Assistant then sees the higher version and pulls the matching prebuilt image. Enable **Auto update** on the Codex App page if you want Home Assistant to install those App updates automatically.

If a new version does not appear immediately, open the Add-on Store and run **Check for updates** from the menu. Home Assistant may cache custom repository metadata briefly.

## Troubleshooting

### The terminal opens but Codex is not authenticated

Run:

```bash
codex login --device-auth
```

Use the displayed URL and one-time code from another browser, then return to Home Assistant.

### Codex starts but exits immediately

Type `shell` at the retry prompt to enter a diagnostic shell, then run:

```bash
codex --version
codex
```

Check the App log for startup validation errors.

### `config.toml` mentions `[projects./homeassistant]`

Older App versions could write an invalid project table after Codex trusted `/homeassistant`. Version `0.2.12` repairs that automatically before Codex starts.

If you are already at a shell prompt, run:

```bash
codex
```

The shell launcher repairs the managed config before starting Codex. If the file was invalid, the old copy is kept beside it as `config.toml.invalid.bak`.

### `config.toml` mentions `tui.model_availability_nux`

Some Codex CLI versions changed the expected type of this UI state value. If an older saved config stores it as a table/map, newer Codex versions refuse to start.

Version `0.2.13` removes that incompatible UI state automatically and keeps the previous file as `config.toml.repaired.bak`.

### MCP is missing

1. Confirm `enable_mcp` is `true`.
2. Restart the App after changing the option.
3. In Codex, check whether the `homeassistant` MCP server appears.
4. Check the App log for `hass-mcp` or Supervisor token errors.

### Project config is ignored

1. Confirm the file is `/homeassistant/.codex/config.toml`.
2. Trust `/homeassistant` in Codex.
3. Restart Codex after changing project-level config.

### Startup is slow

Disable `auto_update_codex` unless you specifically need the newest CLI on every start. Keep `session_persistence` off until authentication is complete.

## Upstream Codex References

- [Codex CLI](https://developers.openai.com/codex/cli)
- [Codex authentication](https://developers.openai.com/codex/auth)
- [Codex config basics](https://developers.openai.com/codex/config-basic)
- [Codex config reference](https://developers.openai.com/codex/config-reference)

## Support

- [Repository](https://github.com/kecksdigital/codex-hass)
- [Issues](https://github.com/kecksdigital/codex-hass/issues)
- [Home Assistant Community](https://community.home-assistant.io/)
