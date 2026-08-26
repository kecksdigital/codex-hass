if [ "$(id -u)" -eq 22000 ]; then
    export HOME=/data/codex-home/users/anonymous
    export CODEX_HOME="${HOME}/.codex"
    export CODEX_STATE_ROOT=/data/codex-home
    export CODEX_MANAGED_ROOT=/data/codex-managed
    export CODEX_HA_URL=http://supervisor/core
    export CODEX_SUPERVISOR_TOKEN_FILE=/tmp/codex/ha-token
    export CODEX_MCP_CONFIG=/data/codex-managed/mcp-servers.json
    export CODEX_MCP_ENVIRONMENT=/data/codex-managed/mcp-environment.json
    export NPM_CONFIG_CACHE="${HOME}/.npm"
    export NPM_CONFIG_PREFIX="${HOME}/.local"
    export PATH="${NPM_CONFIG_PREFIX}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

    if [ -r /data/codex-managed/session-options.json ]; then
        export CODEX_WORK_DIR="$(jq -r '.working_directory // "/homeassistant"' /data/codex-managed/session-options.json)"
        export CODEX_DEFAULT_MODEL="$(jq -r '.default_model // ""' /data/codex-managed/session-options.json)"
        export CODEX_ENABLE_MCP="$(jq -r '.enable_mcp' /data/codex-managed/session-options.json)"
        export CODEX_PERMISSIONS="$(jq -r '.codex_permissions // "workspace"' /data/codex-managed/session-options.json)"
        export CODEX_APPROVAL_POLICY="$(jq -r '.codex_approval_policy // "on-request"' /data/codex-managed/session-options.json)"
    else
        export CODEX_WORK_DIR=/homeassistant
        export CODEX_ENABLE_MCP=true
        export CODEX_PERMISSIONS=workspace
        export CODEX_APPROVAL_POLICY=on-request
    fi

    if [ -r "$CODEX_MCP_ENVIRONMENT" ]; then
        while IFS= read -r -d '' env_name && IFS= read -r -d '' env_value; do
            case "$env_name" in
                ''|[0-9]*|*[!A-Za-z0-9_]*) continue ;;
            esac
            export "$env_name=$env_value"
        done < <(jq -j '.[] | .name, "\u0000", .value, "\u0000"' "$CODEX_MCP_ENVIRONMENT")
        unset env_name env_value
    fi

    source /etc/codex.bashrc

    if [ -d "${CODEX_WORK_DIR}" ]; then
        cd "${CODEX_WORK_DIR}"
    else
        cd /homeassistant
    fi
fi
