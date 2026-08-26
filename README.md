# Codex App for Home Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Run OpenAI Codex from the Home Assistant sidebar.

This repository publishes one Home Assistant App: `Codex`. It gives you a browser terminal inside Home Assistant, starts in your Home Assistant configuration directory, and can optionally connect Codex to Home Assistant through MCP.

## Install

[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fkecksdigital%2Fcodex-hass)

Manual install:

1. Open **Settings** -> **Add-ons** -> **Add-on Store** in Home Assistant.
2. Open **Repositories** from the three-dot menu.
3. Add `https://github.com/kecksdigital/codex-hass`.
4. Install **Codex**.
5. Start the App and open it from the sidebar.

## What You Get

- OpenAI Codex CLI running in Home Assistant.
- A web terminal served through Home Assistant ingress.
- Prebuilt GHCR images for faster installs and Home Assistant updates.
- Direct access to `/homeassistant`, `/share`, and `/media`.
- Read-only access to `/ssl` and `/backup`.
- Optional Home Assistant MCP integration for entity lookup and service calls.
- App options for additional remote MCP servers, bearer tokens, and environment variables.
- Persistent Codex auth and settings under `/data/codex-home`.
- Home Assistant options for model default, sandbox access, MCP servers, environment variables, terminal theme, and session persistence.

## Authentication

Codex authentication normally happens inside the terminal, so Home Assistant does not need to store your OpenAI API key, ChatGPT session, or Codex access token in App options. Credentials deliberately added through the optional MCP or environment-variable settings are stored as App options.

On first launch, Codex prompts you to sign in. The Codex CLI supports ChatGPT sign-in for subscription access and API-key sign-in for usage-based access. On headless or remote systems, use the Codex device-code login option if the normal browser callback flow cannot complete.

## Defaults

- Model: `gpt-5.4`
- Access: `workspace`
- Approval policy: `on-request`
- Session persistence: off for a cleaner first sign-in
- MCP: on
- Auto-update Codex CLI: off

Use `full_access` only when you want Codex to run with broad local access inside the App container.
Use `codex_approval_policy: never` only when you want autonomous execution without per-action approval prompts.

## Updates

Home Assistant updates the Codex App when this repository publishes a higher version in `codex/config.yaml`.

The App uses prebuilt images from GitHub Container Registry:

```text
ghcr.io/kecksdigital/codex-hass:<version>
```

Enable **Auto update** on the Codex App page in Home Assistant if you want Home Assistant to install future App versions automatically.

## Documentation

Read the full usage guide in [codex/README.md](codex/README.md).

Useful upstream docs:

- [Codex CLI](https://developers.openai.com/codex/cli)
- [Codex authentication](https://developers.openai.com/codex/auth)
- [Codex configuration](https://developers.openai.com/codex/config-basic)
- [Codex configuration reference](https://developers.openai.com/codex/config-reference)

## Support

- [Issues](https://github.com/kecksdigital/codex-hass/issues)
- [Home Assistant Community](https://community.home-assistant.io/)

## License

MIT License
