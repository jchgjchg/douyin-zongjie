#!/usr/bin/env python3
"""mlx-whisper 转写（M3 Max GPU 加速，使用本地缓存的 large-v3-turbo，不联网）"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"  # 强制离线，只用本地缓存

from mlx_whisper import transcribe

WAV = "/Users/changliu/douyinzongjie/downloads/audio.wav"
MODEL = "mlx-community/whisper-large-v3-turbo"
OUT_SRT = "/Users/changliu/douyinzongjie/downloads/transcript.srt"
OUT_TXT = "/Users/changliu/douyinzongjie/downloads/transcript.txt"

def fmt_ts(sec):
    h = int(sec // 3600); m = int(sec % 3600 // 60); s = int(sec % 60); ms = int((sec - int(sec)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

print(f"[1/2] 加载本地模型 {MODEL} (MLX/GPU) ...", flush=True)
result = transcribe(
    WAV,
    path_or_hf_repo=MODEL,
    language="zh",
    verbose=False,
)
segs = result.get("segments", [])
lines_srt, lines_txt = [], []
for i, seg in enumerate(segs, 1):
    text = seg["text"].strip()
    lines_srt.append(f"{i}\n{fmt_ts(seg['start'])} --> {fmt_ts(seg['end'])}\n{text}\n")
    lines_txt.append(text)
with open(OUT_SRT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_srt))
with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_txt))
print(f"[2/2] 完成：{len(segs)} 段 | {OUT_SRT} | {OUT_TXT}", flush=True)
