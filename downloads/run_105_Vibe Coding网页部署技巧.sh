#!/bin/bash
# 一键复现「Vibe Coding网页部署技巧，完整实操演示」抖音视频的下载+转写
# 用法：bash /Users/changliu/douyinzongjie/downloads/run_105_Vibe\ Coding网页部署技巧.sh
set -e

export PATH="/opt/homebrew/bin:$PATH"
export HF_HUB_OFFLINE=1
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy
export NO_PROXY="*" no_proxy="*"

PROJ=/Users/changliu/douyinzongjie
SCRIPTS=/Users/changliu/WorkBuddy/2026-09-27-23-11-21/scripts
PY=/Users/changliu/.workbuddy/binaries/python/envs/default/bin/python3
URL="https://v.douyin.com/BKPUVcOsjMw/"
VID=7691946627389777521
NAME="Vibe Coding网页部署技巧"
DEST="$PROJ/downloads/105_$NAME"
WORK="$PROJ/.work/v105"

mkdir -p "$WORK" "$DEST"
cd "$WORK"

echo "=== [1/2] 下载视频 + 元信息 (douyin_fetch.py) ==="
"$PY" "$SCRIPTS/douyin_fetch.py" "$URL"

echo "=== [2/2] 抽音频 + ASR 转写 (asr.py) ==="
ffmpeg -y -i "video_$VID.mp4" -vn -ac 1 -ar 16000 -f wav audio.wav
"$PY" "$SCRIPTS/asr.py"

echo "=== 归位到 $DEST ==="
mv -f "video_$VID.mp4" "$DEST/"
mv -f video_meta.json transcript_plain.txt transcript.srt transcript_segments.json "$DEST/"
echo "完成。分析稿请手写出： $PROJ/analysis/分析报告_$NAME.md"
