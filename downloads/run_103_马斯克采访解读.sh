#!/bin/bash
# 处理抖音视频：央视马斯克采访精华版解读（https://v.douyin.com/btRbQ9CYOhU/）
# 用法：在 Terminal 里  bash /Users/changliu/douyinzongjie/downloads/run_103_马斯克采访解读.sh
# 前置：~/.douyin_cookies.txt 已存在（Netscape 格式）。若无，先按文末提示导出。
set -e

export PATH="/opt/homebrew/bin:$PATH"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy
export NO_PROXY="*" no_proxy="*"

PROJ=/Users/changliu/douyinzongjie
PY=/Users/changliu/.workbuddy/binaries/python/envs/default/bin/python3
URL="https://v.douyin.com/btRbQ9CYOhU/"
OUT="$PROJ/downloads/103_马斯克采访解读"
NAME="马斯克采访解读"
COOKIE=~/.douyin_cookies.txt

cd "$PROJ"
mkdir -p "$OUT"

echo "============================================"
echo "[1/3] 抓直链 (capture.py)"
echo "============================================"
if [ ! -f "$COOKIE" ]; then
  echo "ERROR: 缺少 $COOKIE"
  echo "请先导出抖音 cookie (Netscape 格式)，二选一："
  echo "  方式A (pip install browser-cookie3 后):"
  echo "    $PY -c \"import browser_cookie3,http.cookiejar; cj=browser_cookie3.load_domain('douyin.com'); j=http.cookiejar.MozillaCookieJar('$COOKIE'); [j.set_cookie(c) for c in cj]; j.save()\""
  echo "  方式B: Chrome 开发者工具 -> Application -> Cookies -> 手动复制为 Netscape 格式存到 $COOKIE"
  exit 1
fi
$PY scripts/capture.py --url "$URL" --out "$OUT" --name "$NAME"

echo "============================================"
echo "[2/3] 下载并合成 (mux.py)"
echo "============================================"
$PY scripts/mux.py --out "$OUT" --name "$NAME"

echo "============================================"
echo "[3/3] whisper 中文转写"
echo "============================================"
VIDEO="$OUT/$NAME.mp4"
if [ -f "$VIDEO" ]; then
  echo "视频已就绪: $VIDEO ($(du -h "$VIDEO" | cut -f1))"
  if "$PY" -m whisper --help >/dev/null 2>&1; then
    echo "whisper 可用，开始转写中文..."
    "$PY" -m whisper "$VIDEO" --model large-v3-turbo --language zh \
          --output_format txt --output_dir "$OUT" 2>&1 | tail -5
    echo ""
    echo "✅ 完成。产物："
    echo "   视频: $OUT/$NAME.mp4"
    echo "   转写: $OUT/$NAME.txt"
  else
    echo "whisper 未安装。请改用剪映(CapCut)导出字幕稿，"
    echo "  或安装: $PY -m pip install openai-whisper"
    echo "  然后把字幕文本粘贴给 WorkBuddy 即可出分析。"
    echo "视频位置: $OUT/$NAME.mp4"
  fi
else
  echo "ERROR: mux.py 未产出成片，请检查上方 capture 日志。"
  exit 1
fi
echo "============================================"
