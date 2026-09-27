#!/usr/bin/env python3
"""mux.py — 读取 capture.py 产出的 captured_urls.json，下载视频/音频流并用 ffmpeg 合成。

用法:
  python scripts/mux.py --out downloads/NN_主题 [--name 主题] [--ffmpeg /opt/homebrew/bin/ffmpeg] [--ffprobe 路径]

依赖: ffmpeg（及 ffprobe）需在 PATH 中，或用 --ffmpeg/--ffprobe 指定，或设环境变量 FFMPEG_BIN。
输出: <out>/<name>.mp4 （视频+音频合成后的完整视频）

说明（两条路径都会自动处理）:
  1. 抖音分片流：video（media-video-*）+ audio（media-audio-und-mp4a）分开 → 下载后 ffmpeg -c copy 合成。
  2. 抖音整段流：部分视频（如 tos-cn-ve-* 直路径，URL 不带 media-audio/media-video 标记）
     单条流本身就已含音视频 → 直接用该流作为成片，无需合成。
  多条候选流时按 br（码率）从高到低尝试，取第一个可用且画质最高的。
"""
import os, sys, json, argparse, subprocess, urllib.request, urllib.parse

for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"]:
    os.environ.pop(k, None)
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36")


def br_of(u):
    """取 URL 里的 br（码率）参数，用于排序挑最高画质；取不到返回 0。"""
    try:
        q = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
        return int(q.get("br", ["0"])[0])
    except Exception:
        return 0


def dedup_key(u):
    """同一路流会有多个不同签名的 URL；按 路径+br+qs 去重。"""
    p = urllib.parse.urlparse(u)
    q = urllib.parse.parse_qs(p.query)
    return (p.path, "".join(q.get("br", ["?"])), "".join(q.get("qs", ["?"])))


def is_content_stream(u):
    """排除贴纸特效、静态资源、detail 接口，只留抖音视频内容流。"""
    return ("douyinvod.com" in u and "/video/tos/" in u
            and "byteeffecttos" not in u and "douyinstatic" not in u)


def is_audio_only_url(u):
    return "media-audio" in u


def probe_streams(ffprobe, path):
    """返回该文件里存在的流类型列表，如 ['audio','video']；失败返回 None。"""
    try:
        r = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "stream=codec_type",
             "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=60)
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="capture.py 的输出目录")
    ap.add_argument("--name", default=None, help="视频文件名，默认取 out 目录名")
    ap.add_argument("--ffmpeg", default=os.environ.get("FFMPEG_BIN", "ffmpeg"))
    ap.add_argument("--ffprobe", default=os.environ.get("FFPROBE_BIN", "ffprobe"))
    args = ap.parse_args()

    out = args.out
    name = args.name or os.path.basename(out.rstrip("/"))
    with open(f"{out}/captured_urls.json") as f:
        data = json.load(f)
    raw_urls = [c["url"] for c in data]

    # 去重（同一条流可能有多个签名不同的 URL）
    seen, urls = set(), []
    for u in raw_urls:
        if not is_content_stream(u):
            continue
        k = dedup_key(u)
        if k in seen:
            continue
        seen.add(k)
        urls.append(u)
    if not urls:
        sys.exit("ERROR: 找不到视频流直链，请检查 captured_urls.json（capture.py 是否成功）")

    # 候选：优先非音频标记流（media-video-* 或整段流），按 br 从高到低
    video_cands = sorted([u for u in urls if not is_audio_only_url(u)], key=br_of, reverse=True)
    audio_url = next((u for u in urls if "media-audio-und-mp4a" in u), None)
    if not video_cands:
        vids = sorted(urls, key=br_of, reverse=True)
        video_cands = vids
    if not video_cands:
        sys.exit("ERROR: 找不到视频流直链，请检查 captured_urls.json")

    def dl(url, path):
        req = urllib.request.Request(url, headers={
            "User-Agent": UA, "Referer": "https://www.douyin.com/"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
        print("saved", path, os.path.getsize(path))

    final = f"{out}/{name}.mp4"
    streams = None

    # 依次尝试候选流，直到找到一个含视频轨的
    for i, vurl in enumerate(video_cands):
        cand = f"{out}/video.mp4" if i == 0 else f"{out}/video_{i}.mp4"
        dl(vurl, cand)
        streams = probe_streams(args.ffprobe, cand)
        print("probe", cand, "->", streams)

        if streams is None:
            # 无 ffprobe：退回旧逻辑（当作纯视频流，需配音频）
            streams = ["video"]
            if not audio_url:
                sys.exit("ERROR: 找不到音频流直链，且无 ffprobe 可判断流类型。请检查 captured_urls.json")
            break

        if "video" in streams:
            if "audio" in streams:
                # 整段流：本身已含音视频，直接作为成片
                print("检测到已是音视频合一的整段流，直接作为成片，无需合成")
                if os.path.exists(final):
                    os.remove(final)
                os.rename(cand, final)
            else:
                # 分片流：还需要单独下音频再合成
                if not audio_url:
                    sys.exit("ERROR: 视频流无音轨，且找不到音频流直链，请检查 captured_urls.json")
                dl(audio_url, f"{out}/audio.mp4")
                r = subprocess.run([args.ffmpeg, "-y",
                                    "-i", cand, "-i", f"{out}/audio.mp4",
                                    "-c", "copy", final], capture_output=True, text=True)
                print("ffmpeg rc", r.returncode)
                if not os.path.exists(final):
                    sys.exit("合成失败:\n" + (r.stderr or "")[:800])
            # 清掉未被选中的其余候选残留
            for j in range(i + 1, len(video_cands)):
                p = f"{out}/video_{j}.mp4"
                if os.path.exists(p):
                    os.remove(p)
            break
        else:
            print(f"候选 {i} 不含视频轨，尝试下一条")
            if i == len(video_cands) - 1:
                sys.exit("ERROR: 所有候选流都不含视频轨，请检查 captured_urls.json")

    if os.path.exists(final):
        print("final size", os.path.getsize(final), final)
    else:
        sys.exit("合成失败：未产出成片")


if __name__ == "__main__":
    main()
