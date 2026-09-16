#!/usr/bin/env python3
"""faster-whisper 转写抖音音频 → SRT + 文本稿件"""
import sys, os
from faster_whisper import WhisperModel

WAV = "/Users/changliu/douyinzongjie/downloads/audio.wav"
OUT_SRT = "/Users/changliu/douyinzongjie/downloads/transcript.srt"
OUT_TXT = "/Users/changliu/douyinzongjie/downloads/transcript.txt"

def fmt_ts(sec):
    h = int(sec // 3600); m = int(sec % 3600 // 60); s = int(sec % 60); ms = int((sec - int(sec)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def main():
    model_size = os.environ.get("WHISPER_MODEL", "small")
    print(f"[1/3] 加载模型 {model_size} (int8/CPU)...", flush=True)
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    print("[2/3] 转写中（约13分钟音频，请稍候）...", flush=True)
    segments, info = model.transcribe(
        WAV, language="zh", beam_size=5, vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )
    lines_srt, lines_txt = [], []
    n = 0
    for seg in segments:
        n += 1
        text = seg.text.strip()
        lines_srt.append(f"{n}\n{fmt_ts(seg.start)} --> {fmt_ts(seg.end)}\n{text}\n")
        lines_txt.append(text)
    with open(OUT_SRT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines_srt))
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines_txt))
    print(f"[3/3] 完成：{n} 段 | {OUT_SRT} | {OUT_TXT}", flush=True)

if __name__ == "__main__":
    main()
