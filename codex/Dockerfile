ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.13-alpine3.21
FROM ${BUILD_FROM}

LABEL maintainer="Kecks Digital"
LABEL org.opencontainers.image.title="Codex App for Home Assistant"
LABEL org.opencontainers.image.description="OpenAI Codex App for the Home Assistant sidebar with terminal access, model controls, and optional MCP integration"
LABEL org.opencontainers.image.source="https://github.com/kecksdigital/codex-hass"
LABEL org.opencontainers.image.licenses="MIT"

ENV \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TERM=xterm-256color \
    NODE_OPTIONS=--max-old-space-size=512

RUN apk add --no-cache \
    acl \
    bash \
    bubblewrap \
    ca-certificates \
    coreutils \
    curl \
    findutils \
    gawk \
    git \
    github-cli \
    grep \
    jq \
    nano \
    ncurses \
    ncurses-terminfo-base \
    nodejs \
    npm \
    openssh-client \
    openssl \
    p7zip \
    ripgrep \
    sed \
    sudo \
    su-exec \
    tmux \
    vim \
    libstdc++ \
    && update-ca-certificates

ARG BUILD_ARCH
RUN case "${BUILD_ARCH}" in \
        amd64) TTYD_ARCH="x86_64"; TTYD_SHA256="8a217c968aba172e0dbf3f34447218dc015bc4d5e59bf51db2f2cd12b7be4f55" ;; \
        aarch64) TTYD_ARCH="aarch64"; TTYD_SHA256="b38acadd89d1d396a0f5649aa52c539edbad07f4bc7348b27b4f4b7219dd4165" ;; \
        *) echo "Unsupported arch: ${BUILD_ARCH}" && exit 1 ;; \
    esac && \
    curl -fsSL "https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.${TTYD_ARCH}" -o /usr/bin/ttyd && \
    echo "${TTYD_SHA256}  /usr/bin/ttyd" | sha256sum -c - && \
    chmod +x /usr/bin/ttyd

RUN NPM_CONFIG_CACHE=/tmp/npm-cache npm install -g @openai/codex \
    && codex --version \
    && rm -rf /tmp/npm-cache

RUN pip3 install --no-cache-dir --break-system-packages hass-mcp

RUN case "${BUILD_ARCH}" in \
        amd64) HA_ARCH="amd64" ;; \
        aarch64) HA_ARCH="aarch64" ;; \
        *) HA_ARCH="amd64" ;; \
    esac && \
    curl -fsSL "https://github.com/home-assistant/cli/releases/latest/download/ha_${HA_ARCH}" -o /usr/local/bin/ha && \
    chmod +x /usr/local/bin/ha

RUN adduser -D -H -u 22000 -G root codex && \
    mkdir -p \
    /data/codex-home \
    /data/codex-managed \
    /homeassistant \
    /root/.local/bin

COPY rootfs/ /

RUN chmod +x \
    /usr/local/bin/hass-mcp-wrapper \
    /usr/local/bin/hass-mcp-root-helper \
    /usr/local/bin/codex-merge-config \
    /usr/local/bin/codex-prepare-mcp \
    /usr/local/bin/codex-shell \
    /usr/local/bin/codex-session \
    /usr/local/bin/codex-start \
    && chmod 440 /etc/sudoers.d/codex-hass-mcp

RUN cat > /etc/tmux.conf << 'EOF'
set -g history-limit 5000
set -ga terminal-overrides ',xterm*:smcup@:rmcup@'
set -g mouse on
set -g xterm-keys on
set -s set-clipboard on
set -g allow-passthrough on
bind -n WheelUpPane if-shell -F -t = "#{mouse_any_flag}" "send-keys -M" "if -Ft= '#{pane_in_mode}' 'send-keys -M' 'select-pane -t=; copy-mode -e; send-keys -M'"
bind -n WheelDownPane select-pane -t= \; send-keys -M
EOF

RUN ln -sf /etc/tmux.conf /root/.tmux.conf

RUN cat > /etc/codex.bashrc << 'EOF'
export TERM=xterm-256color
export LANG=C.UTF-8
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
PS1='\[\033[1;36m\]codex\[\033[0m\]:\[\033[1;34m\]\w\[\033[0m\]\$ '

alias ll='ls -la'
alias ha-config='cd /homeassistant'
alias ha-logs='cat /homeassistant/home-assistant.log 2>/dev/null || echo "Log not found"'
EOF

RUN echo 'source /etc/codex.bashrc' > /root/.profile

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /homeassistant

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -sf http://localhost:7681/ >/dev/null || exit 1

ENTRYPOINT []
CMD ["/usr/local/bin/codex-start"]
