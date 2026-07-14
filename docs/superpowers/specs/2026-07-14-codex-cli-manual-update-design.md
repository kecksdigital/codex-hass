# Codex CLI manual update option

## Goal

Allow a Home Assistant user to request a one-time update of the Codex CLI from
the add-on configuration page. The update targets only the npm package
`@openai/codex@latest`; it must not update or rebuild the Home Assistant
add-on image.

## User-facing behavior

- Add a boolean option named `update_codex_cli`, disabled by default.
- The option is presented with translated name and description in the existing
  add-on configuration form.
- When the user enables the option and saves the configuration, the next
  add-on start performs the update before launching `ttyd`.
- The option is treated as a one-shot request. After the request has been
  consumed, the running container records that it has been processed so a
  later restart does not repeat the update unless the user enables the option
  again.
- The existing `auto_update_codex` option remains available for users who want
  an update on every start. The two modes are independent; a one-shot request
  must not change the persistent automatic-update setting.

## Architecture and data flow

1. `codex/config.yaml` declares `update_codex_cli: false` and its boolean
   schema entry.
2. The translation files add the field label and help text.
3. `codex-start` reads the option from `/data/options.json` and checks a
   persistent marker under `/data/codex-managed`.
4. If the request is pending, `codex-start` invokes the existing bounded npm
   update path using the root-owned temporary npm cache, records success or
   failure in the add-on log, and writes a marker showing that the request was
   consumed.
5. The marker is written atomically and is not used to modify
   `/data/options.json`, since Supervisor owns that file. The managed state
   records the last observed boolean value. A `true` value triggers an update
   only when the previous observed value was `false` or no value exists; a
   `false` value is recorded without updating. This makes the
   `true -> false -> true` cycle a new request while a restart with `true` is
   ignored.
6. Codex startup continues with the newly installed version on success or the
   pre-existing version on failure.

The implementation should centralize the npm update command and timeout/error
handling in a small helper so automatic and one-shot updates cannot drift.

## Request de-duplication

Because Supervisor owns `/data/options.json`, the add-on must not attempt to
rewrite the configuration option after consuming it. The managed state records
the last observed value as `true` or `false`. A true option whose previous
state is already `true` is ignored; when the user disables and later re-enables
the option, the intervening `false` state allows the new update request.

If the add-on is restarted during an update, the request must remain pending
until the update command has returned. The marker is written only after the
command finishes, and the command is guarded by a lock to prevent concurrent
startup paths from running npm twice. A failed or timed-out command is still a
consumed request; the user can retry by saving `false`, then saving `true`.

## Error handling and security

- Keep the existing 30–300 second timeout bounds.
- Keep npm output in a temporary log and expose only a short tail in the
  add-on log on failure.
- Never pass the Supervisor token to npm.
- Use a root-owned temporary cache for startup updates and remove it after the
  command completes.
- Never prevent `ttyd` from starting solely because the update failed.
- The update remains limited to the globally installed Codex package; no
  arbitrary package name comes from user input.

## Documentation

Update `codex/README.md` to explain the one-shot option, the need to save and
restart the add-on, how to read the update result in the add-on log, and the
difference from `auto_update_codex`.

## Verification

- Validate YAML syntax for `config.yaml` and all translation files.
- Exercise the startup update decision logic with the option disabled, a first
  enabled request, a repeated start with the same request, and a disable/re-
  enable cycle.
- Verify that a failed or timed-out npm command still reaches terminal startup.
- Run shell syntax checks for all changed shell scripts and the repository's
  available tests/checks.
- Confirm the existing automatic-update behavior remains unchanged.

## Scope exclusions

- No custom frontend or Home Assistant core modification.
- No button injection into Home Assistant's native app page.
- No update of the Home Assistant add-on image itself.
