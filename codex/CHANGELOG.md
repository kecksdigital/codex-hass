# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-07-14

### Added
- Documented the design for requesting a one-shot Codex CLI update from the add-on configuration, including the retry cycle.

## [0.2.15] - 2026-05-31

### Fixed
- Stopped exposing `/root/.npm` as the runtime npm cache so Codex CLI updates no longer fail with `EACCES` after the terminal drops to the unprivileged `codex` user
- Gave interactive Codex sessions a persistent user-owned npm cache and global prefix under the persistent Codex user home so `npm install -g @openai/codex@latest` works from the terminal and stays on `PATH`
- Isolated optional startup-time root CLI updates to a temporary root-owned npm cache instead of reusing the interactive session cache

## [0.2.14] - 2026-05-24

### Added
- Installed `bubblewrap` so Codex workspace sandbox mode has the Linux sandbox runtime it expects

### Fixed
- Added a default `BUILD_FROM` value to silence Docker's invalid default build-arg warning while preserving Home Assistant's per-architecture build argument override

## [0.2.13] - 2026-05-24

### Fixed
- Repair saved Codex UI state when `tui.model_availability_nux` is stored as a table/map instead of the integer expected by current Codex CLI versions
- Back up semantically repaired config files as `config.toml.repaired.bak`

## [0.2.12] - 2026-05-24

### Fixed
- Quote TOML table keys for project paths such as `/homeassistant` so generated `config.toml` remains valid after Codex records trusted projects
- Repair legacy invalid `[projects./homeassistant]` config sections by backing up the bad file and rewriting them as `[projects."/homeassistant"]`
- Re-run Codex config merge and repair before every Codex launch from the terminal shell, including retries after Codex exits

## [0.2.11] - 2026-05-24

### Added
- Added a `codex_approval_policy` App option with `on-request`, `untrusted`, and `never` choices
- Documented autonomous mode using `codex_permissions: full_access` together with `codex_approval_policy: never`

### Changed
- Generate Codex `approval_policy` from the App option so users can disable per-action approval prompts when they explicitly choose autonomous mode

## [0.2.10] - 2026-05-24

### Added
- Added a GitHub Actions workflow to publish prebuilt `amd64` and `aarch64` Codex App images to GitHub Container Registry
- Added the `image` field so Home Assistant pulls `ghcr.io/kecksdigital/codex-hass:<version>` instead of building locally

### Fixed
- Passed the per-architecture Home Assistant base image into the GHCR build workflow so Docker builds do not rely on local Supervisor build arguments

### Changed
- Documented the difference between Home Assistant App updates and optional Codex CLI startup updates

## [0.2.9] - 2026-05-24

### Changed
- Rewrote Codex documentation as a standalone Home Assistant App guide with first-run authentication, model, access, MCP, persistence, and update guidance
- Changed new installs to start with `session_persistence` disabled for a cleaner first sign-in flow
- Reduced tmux history, ttyd client count, and ttyd scrollback for safer startup on smaller Home Assistant systems
- Increased healthcheck startup grace and capped Node heap usage to improve reliability during heavier Codex CLI starts

### Added
- Added optional bounded Codex CLI startup updates with `auto_update_codex` and `codex_update_timeout`
- Added startup validation for the generated Codex config when the installed CLI exposes `codex debug prompt-input`
- Added SHA256 verification for downloaded `ttyd` binaries

### Fixed
- Sanitized terminal font size and update timeout values before using them in startup commands
- Prevented optional Codex CLI runtime updates from inheriting the Home Assistant Supervisor token
- Removed unnecessary `net_admin` from the AppArmor profile

## [0.2.8] - 2026-05-24

### Changed
- Set the starter `default_model` add-on option to `gpt-5.4` instead of leaving Codex to choose its current default
- Added a `codex_permissions` add-on option with `workspace` and `full_access` choices
- Generate Codex `sandbox_mode` from the add-on option, mapping `full_access` to `danger-full-access`
- Documented how to change the model and access level from Home Assistant options

## [0.2.7] - 2026-05-24

### Fixed
- Pre-created the unprivileged Codex runtime user at image build time instead of trying to run `adduser` inside Home Assistant AppArmor at terminal connection time
- Kept the terminal open with an unprivileged diagnostic shell if session startup fails, instead of letting ttyd fall back to its restart prompt
- Made direct-ttyd mode explicitly use the shared `anonymous` Codex home instead of partially emulating per-user runtime accounts
- Moved the tmux socket into the managed Codex state directory and made generated Codex config writable by the runtime user
- Serialized startup config generation and atomically replaced `config.toml` to avoid races when multiple terminals connect
- Added base terminfo data for tmux compatibility with `xterm-256color`

## [0.2.6] - 2026-05-24

### Fixed
- Restored direct ttyd ingress serving on port 7681 so the WebSocket console works behind Home Assistant ingress
- Removed the nginx proxy and ttyd auth-header mode that caused `/ws` 502 responses and ttyd restart prompts
- Updated the healthcheck to probe ttyd directly after removing nginx from the runtime path
- Updated documentation to describe the current shared direct-ttyd ingress identity accurately

### Changed
- Start Codex automatically when the Web UI opens so unauthenticated users are taken directly into the Codex sign-in flow
- Retry Codex by default when startup exits before completion, with an explicit diagnostic shell escape

## [0.2.5] - 2026-05-24

### Fixed
- Fixed the per-user tmux launcher so ttyd opens an interactive shell instead of falling back to its restart prompt
- Added visible session startup errors in the browser terminal when the shell wrapper fails before bash starts

## [0.2.4] - 2026-05-24

### Changed
- Reduced nginx health-check log noise so Web UI proxy errors are easier to see in add-on logs

## [0.2.3] - 2026-05-24

### Fixed
- Switched the nginx upstream from a Unix socket to `127.0.0.1:7682` so ttyd no longer depends on socket permission compatibility
- Expanded the ingress allowlist from a single hard-coded Supervisor IP to private network ranges used by Home Assistant installations

## [0.2.2] - 2026-05-24

### Fixed
- Allowed AppArmor execution of `/usr/sbin/nginx` so the hardened ingress proxy can start correctly
- Moved Codex startup validation out of `/tmp` to avoid Codex helper-binary warnings during MCP config checks

## [0.2.1] - 2026-05-24

### Changed
- Rewrote the Codex documentation to explain installation, per-user sessions, MCP wiring, persistence, and everyday usage more clearly
- Replaced upstream repository links and metadata with the `kecksdigital/codex-hass` repository
- Updated the add-on branding, description, and panel icon so the Codex add-on no longer ships with Claude-oriented presentation

## [0.2.0] - 2026-05-23

### Added
- Per-user Codex homes under `/data/codex-home/users/<ha-user-id>/.codex`
- Dedicated Unix users for each Home Assistant ingress user before the shell starts
- Per-user tmux session isolation keyed by the Home Assistant ingress user id
- Reverse-proxied ingress terminal with nginx in front of ttyd and ttyd bound to a local Unix socket
- `hass-mcp-wrapper` and a privileged root helper so the Supervisor token stays out of the interactive shell
- Non-destructive merging of add-on-managed Codex defaults into each user's `~/.codex/config.toml`
- One-time backup of legacy shared Codex state from `/homeassistant/.codex-home` without auto-assigning it to a user

### Changed
- Moved persistent Codex state out of `/homeassistant` and into `/data/codex-home`
- Removed the shared global ttyd/tmux session model in favor of per-user sessions
- Added startup validation for the generated per-user Codex MCP configuration
- Removed inherited `docker_api` and `full_access` privileges from the Codex add-on

## [0.1.0] - 2026-05-23

### Added
- Initial Codex add-on release alongside the existing Claude Code add-on
- OpenAI Codex CLI installed during image build with `codex --version` validation
- Home Assistant ingress terminal powered by ttyd on port 7681
- Persistent Codex home directory at `/homeassistant/.codex-home`
- Generated `~/.codex/AGENTS.md` with Home Assistant path mapping, log guidance, and MCP notes
- Generated `~/.codex/config.toml` with optional default model selection and Home Assistant MCP wiring
- Session persistence via tmux with the `codex` session name
- Initial architecture support for amd64 and aarch64

### Changed
- Removed Playwright MCP and Claude-specific runtime behavior from the new Codex add-on
- Removed inherited Modbus/serial tooling and UART access from the Codex v1 scope
