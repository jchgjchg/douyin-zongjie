#!/usr/bin/env python3
"""mux.py — 读取 capture.py 产出的 captured_urls.json，下载视频/音频流并用 ffmpeg 合成。

用法:
  python scripts/mux.py --out downloads/NN_主题 [--name 主题] [--ffmpeg /opt/homebrew/bin/ffmpeg]

依赖: ffmpeg 需在 PATH 中，或用 --ffmpeg 指定，或设环境变量 FFMPEG_BIN。
输出: <out>/<name>.mp4 （视频+音频合成后的完整视频）
"""
import os, sys, json, argparse, subprocess, urllib.request

for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"]:
    os.environ.pop(k, None)
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36")


def is_real_video(u):
    """排除音频流、贴纸特效、静态资源，挑出真正的视频清晰度流。"""
    return ("douyinvod.com" in u and "media-audio" not in u
            and "byteeffecttos" not in u and "douyinstatic" not in u)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="capture.py 的输出目录")
    ap.add_argument("--name", default=None, help="视频文件名，默认取 out 目录名")
    ap.add_argument("--ffmpeg", default=os.environ.get("FFMPEG_BIN", "ffmpeg"))
    args = ap.parse_args()

    out = args.out
    name = args.name or os.path.basename(out.rstrip("/"))
    with open(f"{out}/captured_urls.json") as f:
        data = json.load(f)
    urls = [c["url"] for c in data]

    video_url = next((u for u in urls if is_real_video(u)), None)
    audio_url = next((u for u in urls if "media-audio-und-mp4a" in u), None)
    if not video_url:
        sys.exit("ERROR: 找不到视频流直链，请检查 captured_urls.json（capture.py 是否成功）")
    if not audio_url:
        sys.exit("ERROR: 找不到音频流直链，请检查 captured_urls.json")

    def dl(url, path):
        req = urllib.request.Request(url, headers={
            "User-Agent": UA, "Referer": "https://www.douyin.com/"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
        print("saved", path, os.path.getsize(path))

    dl(video_url, f"{out}/video.mp4")
    dl(audio_url, f"{out}/audio.mp4")

    final = f"{out}/{name}.mp4"
    r = subprocess.run([args.ffmpeg, "-y",
                        "-i", f"{out}/video.mp4", "-i", f"{out}/audio.mp4",
                        "-c", "copy", final], capture_output=True, text=True)
    print("ffmpeg rc", r.returncode)
    if os.path.exists(final):
        print("final size", os.path.getsize(final), final)
    else:
        sys.exit("合成失败:\n" + (r.stderr or "")[:800])


if __name__ == "__main__":
    main()
