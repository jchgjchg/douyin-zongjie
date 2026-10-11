#!/bin/bash
# 一键处理「看本质的三步法」抖音视频
# 用法：在 Terminal 里  bash /Users/changliu/douyinzongjie/downloads/run_101_看本质三步法.sh
# 前置：~/.douyin_cookies.txt 已存在（Netscape 格式）。若无，先按文末提示导出。
set -e

export PATH="/opt/homebrew/bin:$PATH"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy
export NO_PROXY="*" no_proxy="*"

PROJ=/Users/changliu/douyinzongjie
PY=/Users/changliu/.workbuddy/binaries/python/envs/default/bin/python3
URL="https://v.douyin.com/M5_LrDTd2u0/"
OUT="$PROJ/downloads/101_看本质三步法"
NAME="看本质三步法"
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
echo "[3/3] 尝试 whisper 转写"
echo "============================================"
VIDEO="$OUT/$NAME.mp4"
if [ -f "$VIDEO" ]; then
  echo "视频已就绪: $VIDEO ($(du -h "$VIDEO" | cut -f1))"
  if "$PY" -m whisper --help >/dev/null 2>&1; then
    echo "whisper 可用，开始转写中文..."
    "$PY" -m whisper "$VIDEO" --model large-v3-turbo --language zh \
          --output_format txt --output_dir "$OUT" 2>&1 | tail -5
    echo "转写输出: $OUT/$NAME.txt"
  else
    echo "whisper 未安装。请改用剪映(CapCut)导出字幕稿，"
    echo "  或安装: $PY -m pip install openai-whisper"
    echo "  然后把字幕文本粘贴给 WorkBuddy 即可出分析。"
  fi
else
  echo "ERROR: mux.py 未产出成片，请检查上方 capture 日志。"
  exit 1
fi

echo "============================================"
echo "完成。产物在: $OUT/"
echo "把 $OUT/$NAME.txt (或剪映字幕稿) 发给 WorkBuddy 出分析。"
echo "============================================"
