#!/usr/bin/env bash
# =========================================
# Hermes Web UI 一键启动脚本
# 用法: bash hermes-webui-start.sh
#
# 修改此模板: API_SERVER_PORT, WEBUI_PORT, TOKEN_PATH 等
# =========================================

set -e

# ---- Node.js PATH ----
export PATH="$HOME/.local/nodejs/bin:$PATH"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}  ✓${NC} $1"; }
warn() { echo -e "${YELLOW}  ⚠${NC} $1"; }
err()  { echo -e "${RED}  ✗${NC} $1"; }

API_PORT=8642
WEBUI_PORT=8648

echo ""
echo "  ⚡ Hermes Web UI 启动器"
echo "  ======================="
echo ""

# ---- 1. 检查 Node.js ----
if ! command -v node &>/dev/null; then
    err "Node.js 未安装"
    echo "    请先下载 node-v23-linux-x64.tar.xz 到 ~/.local/nodejs/"
    exit 1
fi
ok "Node.js $(node -v)"

# ---- 2. 检查 hermes-web-ui ----
if ! command -v hermes-web-ui &>/dev/null; then
    err "hermes-web-ui 未安装"
    echo "    安装命令: npm install -g hermes-web-ui"
    exit 1
fi
ok "hermes-web-ui OK"

# ---- 3. 检查 Hermes Agent ----
if ! command -v hermes &>/dev/null; then
    err "Hermes Agent 未安装"
    exit 1
fi
ok "Hermes Agent $(hermes --version 2>/dev/null | head -1)"

# ---- 4. 启动 API Server (若未运行) ----
echo ""
if curl -s -o /dev/null http://localhost:$API_PORT/v1/models 2>/dev/null; then
    ok "API Server 已在运行 (localhost:$API_PORT)"
else
    warn "API Server 未启动，正在启动..."
    hermes gateway run &
    sleep 4
    ok "Gateway / API Server 已启动"
fi

# ---- 5. 启动 hermes-web-ui (若未运行) ----
echo ""
if curl -s -o /dev/null http://localhost:$WEBUI_PORT 2>/dev/null; then
    ok "hermes-web-ui 已在运行 (localhost:$WEBUI_PORT)"
else
    warn "hermes-web-ui 未启动，正在启动..."
    hermes-web-ui start
    sleep 2
    ok "hermes-web-ui 已启动"
fi

# ---- 6. 打印总结 ----
TOKEN_PATH="$HOME/.hermes-web-ui/.token"
echo ""
echo "  ┌──────────────────────────────────────┐"
echo "  │  Hermes Web UI 已就绪                 │"
echo "  ├──────────────────────────────────────┤"
echo "  │  Dashboard: http://localhost:$WEBUI_PORT"
echo "  │  Token: $(cat $TOKEN_PATH 2>/dev/null || echo '见 '"$TOKEN_PATH")"
echo "  └──────────────────────────────────────┘"
echo ""
echo "  停止: hermes-web-ui stop"
echo ""
