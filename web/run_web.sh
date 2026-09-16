#!/usr/bin/env bash
# 启动抖音转写分析平台的 Web 界面
# 前置（同 scripts/ 流水线）: ffmpeg、Chrome 或 playwright chromium、抖音 cookie、OPENAI_API_KEY
#   - cookie 默认读 ~/.douyin_cookies.txt
#   - LLM: export OPENAI_API_KEY=...  （可选 OPENAI_BASE_URL / OPENAI_MODEL 指向本地网关）
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="/opt/homebrew/bin:$PATH"
PORT="${PORT:-8000}" HOST="${HOST:-127.0.0.1}"
echo "→ http://${HOST}:${PORT}"
exec python web/app.py
