#!/usr/bin/env python3
"""transcribe.py — 把视频/音频转写成 SRT + 纯文本稿件。

支持两种后端（自动选择）:
  - Apple Silicon (MLX):  mlx-whisper   （GPU 加速，离线，吃本地 HF 缓存）
  - 其他平台:             faster-whisper（自动下载模型，需联网首次）

用法:
  python scripts/transcribe.py <video_or_audio> <out_dir> [model]

  video_or_audio : 视频或音频文件（内部用 ffmpeg 解码，需 PATH 含 ffmpeg）
  out_dir        : 输出目录（生成 transcript.srt / transcript.txt）
  model          : 默认 large-v3-turbo
                   mlx 后端会自动拼成 mlx-community/<model>

注意: mlx 后端默认 HF_HUB_OFFLINE=1（只吃本地缓存）。若用 faster-whisper 且模型未缓存，
      请先 `export HF_HUB_OFFLINE=0` 允许下载。
"""
import os, sys

# MLX 后端离线；非 MLX 用户在未缓存模型时请 unset 此变量。
os.environ.setdefault("HF_HUB_OFFLINE", "1")


def fmt_ts(sec):
    h = int(sec // 3600); m = int(sec % 3600 // 60)
    s = int(sec % 60); ms = int((sec - int(sec)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def load_engine(model):
    """返回 (backend, engine)。"""
    try:
        from mlx_whisper import transcribe
        return "mlx", transcribe, f"mlx-community/{model}"
    except ImportError:
        from faster_whisper import WhisperModel
        m = WhisperModel(model, device="auto", compute_type="auto")
        return "faster", m, model


def main():
    if len(sys.argv) < 3:
        print("用法: python transcribe.py <video_or_audio> <out_dir> [model]")
        sys.exit(1)
    audio, out_dir = sys.argv[1], sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "large-v3-turbo"
    os.makedirs(out_dir, exist_ok=True)
    out_srt = os.path.join(out_dir, "transcript.srt")
    out_txt = os.path.join(out_dir, "transcript.txt")

    backend, engine, real_model = load_engine(model)
    print(f"[1/2] 加载模型 {real_model} ({backend} 后端) ...", flush=True)

    lines_srt, lines_txt = [], []
    if backend == "mlx":
        result = engine(audio, path_or_hf_repo=real_model, language="zh", verbose=False)
        for i, seg in enumerate(result.get("segments", []), 1):
            text = seg["text"].strip()
            lines_srt.append(f"{i}\n{fmt_ts(seg['start'])} --> {fmt_ts(seg['end'])}\n{text}\n")
            lines_txt.append(text)
    else:
        segs, _ = engine.transcribe(audio, language="zh", verbose=False)
        for i, seg in enumerate(segs, 1):
            text = seg.text.strip()
            lines_srt.append(f"{i}\n{fmt_ts(seg.start)} --> {fmt_ts(seg.end)}\n{text}\n")
            lines_txt.append(text)

    with open(out_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines_srt))
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines_txt))
    print(f"[2/2] 完成：{len(lines_txt)} 段 | {out_srt} | {out_txt}", flush=True)


if __name__ == "__main__":
    main()
