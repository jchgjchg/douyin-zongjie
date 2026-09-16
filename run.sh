#!/usr/bin/env bash
# 一条命令跑完整条流水线: 抓流 → 合成 → 转写 → 清洗 → 分析
# 用法:
#   bash run.sh "<抖音链接>" downloads/NN_主题 主题名
#
# 前置（见 README）: ffmpeg 在 PATH、Chrome 或 playwright chromium、抖音 cookie 文件、
#                   OPENAI_API_KEY（或本地网关）已导出。
set -euo pipefail

URL="${1:?用法: bash run.sh <抖音链接> <输出目录> <主题名>}"
OUT="${2:?缺少输出目录}"
NAME="${3:-$(basename "$OUT")}"

mkdir -p "$OUT" analysis

echo "==[1/5] 抓流=="
python scripts/capture.py --url "$URL" --out "$OUT" --name "$NAME"

echo "==[2/5] 合成视频=="
python scripts/mux.py --out "$OUT" --name "$NAME"

echo "==[3/5] 转写=="
python scripts/transcribe.py "$OUT/$NAME.mp4" "$OUT"

echo "==[4/5] 清洗=="
python scripts/clean.py "$OUT/transcript.txt" "$OUT/transcript_clean.txt"

echo "==[5/5] 分析=="
python scripts/analyze.py "$OUT/transcript_clean.txt" "analysis/分析报告_$NAME.md"

echo "完成 -> analysis/分析报告_$NAME.md"
