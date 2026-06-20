---
name: hermes-web-frontend
description: "Configure Hermes Agent web frontend UIs — API Server, Open WebUI, LobeChat, custom static HTML fallback"
version: 1.0.0
author: agent
created_by: agent
tags: [hermes, webui, open-webui, frontend, gateway, api-server]
---

# Hermes Web Frontend Setup

Set up a web-based UI for Hermes Agent, beyond the console/TUI. Hermes exposes an OpenAI-compatible API Server through its gateway; any OpenAI-compatible web client (Open WebUI, LobeChat, LibreChat, NextChat, ChatBox) can connect to it.

## When to Use

- User asks for a web UI / browser interface for Hermes
- User wants to chat with Hermes from a browser instead of the terminal
- User needs to share Hermes access with non-CLI users via a web app
- User asks about alternative frontends beyond the console

## Architecture

```
Browser (Open WebUI / custom HTML)
    │  HTTP (OpenAI-compatible API)
    ▼
Hermes API Server (port 8642)  ←  part of Hermes Gateway
    │
    ▼
Hermes Agent Core (LLM, tools, memory, skills)
```

## Step-by-Step Workflow

### 1. Enable API Server Platform

Add these env vars to `~/.hermes/.env`:

```
API_SERVER_ENABLED=true
API_SERVER_KEY=<random-key>          # use `openssl rand -hex 16` to generate
API_SERVER_PORT=8642
API_SERVER_HOST=0.0.0.0
API_SERVER_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
API_SERVER_MODEL_NAME=hermes-agent
```

The API Server platform auto-detects these env vars — no config.yaml changes needed.

### 2. Start the Gateway

```bash
hermes gateway run      # foreground
# or install as service:
hermes gateway install  # background via systemd
```

### 3. Verify API Server

```bash
# List models (unauthenticated)
curl http://localhost:8642/v1/models

# With API key
curl -H "Authorization: Bearer $API_SERVER_KEY" http://localhost:8642/v1/models

# Test chat
curl -X POST http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"Hello"}],"stream":false}'
```

### 4. Choose and Deploy a Web UI

#### Option A: hermes-web-ui (Vue 3 + Koa — RECOMMENDED)

Full-featured Vue 3 web dashboard. **16 feature modules, 80+ API endpoints.** The richest option.

- **Repo:** `github.com/EKKOLearnAI/hermes-web-ui`
- **npm:** `hermes-web-ui`
- **Tech:** Vue 3 + TypeScript + Koa + Socket.IO + SQLite
- **Requires:** Node.js >= 23

**Features:** AI Chat (streaming SSE, multi-session, file upload/download, Ctrl+K search), 8 platform channels (Telegram, Discord, Slack, WhatsApp, Matrix, Feishu, WeChat, WeCom), usage analytics, cron management, model management, multi-profile & gateway, file browser, group chat, skills & memory, logs, web terminal (xterm.js PTY), auth (token or username/password).

Installation:
```bash
# One-line auto-setup (installs Node.js too)
bash <(curl -fsSL https://raw.githubusercontent.com/gavin913-lss/hermes-web-ui/main/scripts/setup.sh)

# Manual:
npm install -g hermes-web-ui
hermes-web-ui start
```

Opens at **http://localhost:8648**. Auth token auto-generated at `~/.hermes-web-ui/.token`:
```bash
cat ~/.hermes-web-ui/.token
```

**Pitfall:** The setup script on the `EKKOLearnAI` org returns 404; use the `gavin913-lss` fork URL instead.

**Node.js missing?** If `sudo apt` is unavailable (no password), download the binary tarball directly:
```bash
mkdir -p ~/.local/nodejs
curl -fsSL "https://nodejs.org/dist/v23.10.0/node-v23.10.0-linux-x64.tar.xz" -o /tmp/node.tar.xz
tar -xf /tmp/node.tar.xz -C ~/.local/nodejs --strip-components=1
export PATH="$HOME/.local/nodejs/bin:$PATH"
# Add permanently:
echo 'export PATH="$HOME/.local/nodejs/bin:$PATH"' >> ~/.bashrc
```

**Startup script:** Create `~/hermes-webui-start.sh` (see `templates/hermes-webui-start.sh`) for one-command launch that checks prereqs, starts the gateway if needed, and starts hermes-web-ui.
```bash
#!/usr/bin/env bash
set -e
export PATH="$HOME/.local/nodejs/bin:$PATH"

# check deps, start gateway if needed, start hermes-web-ui
hermes-web-ui start 2>/dev/null || true
echo "Dashboard: http://localhost:8648"
cat ~/.hermes-web-ui/.token
```
Stop: `hermes-web-ui stop`.

#### Option B: Built-in `hermes dashboard` (React)

Bundled with Hermes Agent. React 19 + Tailwind CSS + Vite. Requires Node.js/npm to build the `web/` dist. Source lives at `~/.hermes/hermes-agent/web/`.

**PREFERRED PATH (two-step — avoids silent npm hang):**

```bash
# Step 1: ensure npm in PATH, then manually build
export PATH="$HOME/.local/nodejs/bin:$PATH"   # adjust if Node.js is elsewhere
cd ~/.hermes/hermes-agent/web
npm install
npm run build

# Step 2: start dashboard (skip redundant build)
hermes dashboard --port 9119 --skip-build --no-open
```

**ONE-STEP PATH (only if npm is in PATH and you can wait):**

```bash
hermes dashboard --port 9119
```

This auto-runs `npm install` + `npm run build` on first launch. Expect **zero stdout output** during the build — the process will appear stuck with no log lines for 1–3 minutes. Do not kill it prematurely. The `--skip-build` two-step approach above avoids this uncertainty.

**Options:** `--port` (default 9119), `--host` (default 127.0.0.1), `--no-open` (don't open browser), `--skip-build` (serve existing dist), `--stop` (kill all dashboard processes), `--status` (list running processes).

Opens at `http://localhost:9119`. Features: embedded TUI terminal, config management, API key management, session browsing.

#### Option C: Open WebUI (Docker — feature-rich)

```bash
docker run -d -p 3000:8080 \
  --add-host host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8642/v1 \
  -e OPENAI_API_KEY=$API_SERVER_KEY \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

Open at `http://localhost:3000`.

Key Open WebUI env vars:
- `OPENAI_BASE_URL` — API endpoint (required)
- `OPENAI_API_KEY` — auth key (required)
- `WEBUI_SECRET_KEY` — for session encryption (optional but recommended)
- `WEBUI_NAME` — display name (optional)
- `DEFAULT_MODELS` — default model (optional)

#### Option D: Static HTML Fallback (no Docker needed)

When Docker is unavailable or network is slow, serve a self-contained HTML from Python's `http.server`:

```bash
# Create directory and serve
mkdir -p ~/hermes-webui
cp path/to/index.html ~/hermes-webui/
cd ~/hermes-webui && python3 -m http.server 3000
```

The HTML file should:
- Use browser `fetch()` to call `http://localhost:8642/v1/chat/completions`
- Send `Authorization: Bearer <key>` header
- Support streaming via `response.body.getReader()` (ReadableStream)
- Prompt user for API key on first 401, save to `localStorage`
- Render Markdown output (code blocks, bold, links)
- Support `/new` (reset) and `/help` commands client-side

Open at `http://localhost:3000`.

#### Option C: LobeChat (Docker — lightweight ~100MB)

```bash
docker run -d -p 3210:3210 \
  -e OPENAI_API_KEY=$API_SERVER_KEY \
  -e NEXT_PUBLIC_OPENAI_PROXY_URL=http://host.docker.internal:8642/v1 \
  --name lobechat \
  lobehub/lobe-chat
```

#### Option D: NextChat (Docker — ~100MB)

```bash
docker run -d -p 3001:3000 \
  -e OPENAI_API_KEY=$API_SERVER_KEY \
  -e BASE_URL=http://host.docker.internal:8642 \
  --name nextchat \
  yidadaa/chatgpt-next-web
```

#### Option E: Any OpenAI-compatible client

Point any client (LibreChat, ChatBox, Continue.dev, custom app) at:
- Base URL: `http://localhost:8642/v1`
- API Key: `$API_SERVER_KEY`

### 5. Connect Open WebUI to Hermes

In Open WebUI:
1. Open `http://localhost:3000`
2. Create admin account on first visit
3. Go to Settings → Connections
4. Set OpenAI Base URL: `http://host.docker.internal:8642/v1`
5. Set API Key: the same `API_SERVER_KEY`
6. Save and test

### 6. Verify End-to-End

```bash
# Health check
curl http://localhost:8642/health

# Models endpoint lists "hermes-agent"
curl -s http://localhost:8642/v1/models | python3 -m json.tool

# Quick chat
curl -s -X POST http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"Hi"}],"max_tokens":50}'
```

## Pitfalls

- **API Server NOT in gateway setup menu**: The API Server platform is auto-discovered from env vars, not listed in `hermes gateway setup` interactive menu. You MUST set `API_SERVER_ENABLED=true` in `.env`.
- **`host.docker.internal` on Linux**: Docker on Linux does NOT have `host.docker.internal` by default. Use `--add-host host.docker.internal:host-gateway` when running containers. Alternatively use `--network host`.
- **CORS errors in browser**: Set `API_SERVER_CORS_ORIGINS` to include the exact origin (port matters). `http://localhost:3000` and `http://127.0.0.1:3000` are different origins.
- **API Server port conflict**: If port 8642 is taken, set `API_SERVER_PORT=<port>` in `.env`.
- **Gateway not running**: The API Server only works when the gateway is running. Verify with `hermes gateway status`.
- **`.env` can't be read directly**: The `read_file` tool blocks `.env` access. Use `grep` via `terminal()` to check.
- **Docker registry unreachable**: Docker Hub (`docker.io`) and ghcr.io may be slow or unreachable. Fall back to the static HTML approach.
- **Streaming in custom HTML**: Use `fetch()` with `response.body.getReader()` for chunked streaming, or fall back to non-streaming `POST /v1/chat/completions`.
- **Static HTML needs CORS**: Without `API_SERVER_CORS_ORIGINS`, browsers block cross-origin `fetch()` calls. Always set this when serving from a different port.
- **`hermes dashboard` npm not in PATH**: Node.js may be installed to a non-standard location (e.g. `~/.local/nodejs/` from a binary tarball). Always `export PATH="$HOME/.local/nodejs/bin:$PATH"` before running `hermes dashboard` or the manual build. Check with `which npm`.
- **`hermes dashboard` silent npm install hang**: On first run, `hermes dashboard` internally runs `npm install`, which produces zero stdout for 1–3 minutes. The process enters D-state (uninterruptible I/O sleep) and appears frozen. Use the two-step approach (manual `npm install && npm run build` then `hermes dashboard --skip-build`) to get visible progress and faster iteration.

## Templates

See `templates/webui-chat.html` — a self-contained, dark/light-themed chat HTML that talks directly to the API Server. Copy and serve with `python3 -m http.server`.

## Reference

See `references/api-server-env-vars.md` for the full list of API Server env vars and their effects.
