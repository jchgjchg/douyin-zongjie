#!/usr/bin/env python3
"""web/app.py — 抖音转写分析平台的本地 Web 界面。

把 scripts/ 下的流水线（抓流 → 合成 → 转写 → 清洗 → 分析）包成一个网页：
  贴抖音链接 → 点运行 → 实时看日志 → 自动渲染分析报告。
侧栏还能浏览本地已有的全部分析报告。

启动:
  bash web/run_web.sh
  # 或
  python web/app.py            # 默认 http://127.0.0.1:8000
  PORT=9000 python web/app.py  # 自定义端口

前置（与 scripts/ 一致）:
  - ffmpeg 在 PATH（或设 FFMPEG_BIN）
  - 本机 Google Chrome 或 playwright chromium
  - 抖音登录 cookie：~/.douyin_cookies.txt（见 scripts/capture.py 头部说明）
  - LLM：export OPENAI_API_KEY=... （可选 OPENAI_BASE_URL / OPENAI_MODEL 指向本地网关）
"""
import os
import sys
import re
import json
import time
import threading
import subprocess
import mimetypes
from pathlib import Path

from flask import Flask, request, Response, jsonify, send_from_directory
import markdown

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DOWNLOADS = ROOT / "downloads"
ANALYSIS = ROOT / "analysis"
PY = sys.executable

app = Flask(__name__)
app.json.ensure_ascii = False

jobs = {}
jobs_lock = threading.Lock()
job_counter = 0


def load_dotenv():
    """读取仓库根 .env（若存在），仅补充缺失的 OPENAI_* 变量。"""
    p = ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


def next_number():
    nums = []
    if DOWNLOADS.exists():
        for d in os.listdir(DOWNLOADS):
            m = re.match(r"^(\d+)_", d)
            if m:
                nums.append(int(m.group(1)))
    return (max(nums) if nums else 0) + 1


def which(bin_name):
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = Path(d) / bin_name
        if p.exists():
            return str(p)
    return bin_name


def run_step(job, label, cmd, env):
    """运行单个流水线步骤，实时把输出写进 job['log']。返回 returncode。"""
    job["log"].append(f"\n==[{label}]==")
    try:
        proc = subprocess.Popen(
            cmd, cwd=str(ROOT), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
        )
        for line in proc.stdout:
            job["log"].append(line.rstrip("\n"))
        return proc.wait()
    except Exception as e:
        job["log"].append(f"!! 启动步骤失败: {e}")
        return -1


def run_pipeline(job, url, name):
    try:
        job["state"] = "running"
        num = next_number()
        outdir = DOWNLOADS / f"{num}_{name or '未命名'}"
        outdir.mkdir(parents=True, exist_ok=True)
        job["outdir"] = str(outdir)
        name = name or outdir.name
        ANALYSIS.mkdir(parents=True, exist_ok=True)
        report_path = ANALYSIS / f"分析报告_{name}.md"

        env = dict(os.environ)
        env["PATH"] = "/opt/homebrew/bin:" + env.get("PATH", "")
        ffmpeg = env.get("FFMPEG_BIN") or which("ffmpeg")

        steps = [
            ("1/5 抓流", [PY, str(SCRIPTS / "capture.py"),
                          "--url", url, "--out", str(outdir), "--name", name]),
            ("2/5 合成视频", [PY, str(SCRIPTS / "mux.py"),
                              "--out", str(outdir), "--name", name]),
            ("3/5 抽音频", [ffmpeg, "-y", "-i", str(outdir / f"{name}.mp4"),
                            "-vn", "-ac", "1", "-ar", "16000",
                            "-c:a", "pcm_s16le", str(outdir / "audio.wav")]),
            ("4/5 转写", [PY, str(SCRIPTS / "transcribe.py"),
                          str(outdir / "audio.wav"), str(outdir)]),
            ("5/5 清洗", [PY, str(SCRIPTS / "clean.py"),
                          str(outdir / "transcript.txt"),
                          str(outdir / "transcript_clean.txt")]),
            ("生成报告", [PY, str(SCRIPTS / "analyze.py"),
                          str(outdir / "transcript_clean.txt"), str(report_path)]),
        ]

        for label, cmd in steps:
            rc = run_step(job, label, cmd, env)
            if rc != 0:
                job["state"] = "error"
                job["log"].append(f"!! {label} 失败（rc={rc}），流水线中止")
                return

        if report_path.exists():
            md = report_path.read_text(encoding="utf-8")
            job["report_md"] = md
            job["report_html"] = markdown.markdown(
                md, extensions=["tables", "fenced_code"])
            job["report_name"] = report_path.name
            job["state"] = "done"
        else:
            job["state"] = "error"
            job["log"].append("!! 报告未生成")
    except Exception as e:
        job["state"] = "error"
        job["log"].append(f"!! 异常: {e}")
    finally:
        job["done"] = True


@app.route("/")
def index():
    return (ROOT / "web" / "index.html").read_text(encoding="utf-8")


@app.route("/api/status")
def status():
    return jsonify({
        "has_key": bool(os.environ.get("OPENAI_API_KEY")),
        "base": os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "has_cookies": os.path.exists(
            os.path.expanduser("~/.douyin_cookies.txt")),
        "ffmpeg": which("ffmpeg"),
    })


@app.route("/api/run", methods=["POST"])
def run():
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    name = (data.get("name") or "").strip() or None
    if not url:
        return jsonify(error="缺少抖音链接 url"), 400
    global job_counter
    with jobs_lock:
        job_counter += 1
        jid = str(job_counter)
        jobs[jid] = {"state": "starting", "log": [], "done": False}
    threading.Thread(target=run_pipeline, args=(jobs[jid], url, name),
                     daemon=True).start()
    return jsonify(job_id=jid)


@app.route("/api/stream/<job_id>")
def stream(job_id):
    job = jobs.get(job_id)
    if not job:
        return Response("data: " + json.dumps({"type": "error", "msg": "任务不存在"}) + "\n\n",
                        mimetype="text/event-stream")

    def gen():
        sent = 0
        while True:
            if len(job["log"]) > sent:
                for line in job["log"][sent:]:
                    yield "data: " + json.dumps({"type": "log", "line": line},
                                                 ensure_ascii=False) + "\n\n"
                sent = len(job["log"])
            if job.get("done"):
                if job["state"] == "done":
                    yield "data: " + json.dumps({
                        "type": "report",
                        "name": job.get("report_name"),
                        "html": job.get("report_html"),
                    }, ensure_ascii=False) + "\n\n"
                else:
                    yield "data: " + json.dumps({
                        "type": "error",
                        "msg": "流水线执行出错，请查看日志",
                    }, ensure_ascii=False) + "\n\n"
                yield "data: " + json.dumps({"type": "end"}, ensure_ascii=False) + "\n\n"
                break
            time.sleep(0.4)

    return Response(gen(), mimetype="text/event-stream")


@app.route("/api/reports")
def reports():
    items = []
    if ANALYSIS.exists():
        for f in os.listdir(ANALYSIS):
            if f.startswith("分析报告_") and f.endswith(".md"):
                p = ANALYSIS / f
                items.append({
                    "file": f,
                    "title": f[len("分析报告_"):-3],
                    "mtime": p.stat().st_mtime,
                    "size": p.stat().st_size,
                })
    items.sort(key=lambda x: -x["mtime"])
    return jsonify(items)


@app.route("/api/report/<path:file>")
def report(file):
    p = ANALYSIS / os.path.basename(file)
    if not p.exists():
        return jsonify(error="not found"), 404
    md = p.read_text(encoding="utf-8")
    return jsonify(
        title=p.name[len("分析报告_"):-3],
        html=markdown.markdown(md, extensions=["tables", "fenced_code"]),
    )


if __name__ == "__main__":
    load_dotenv()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    print(f"抖音转写分析平台: http://{host}:{port}")
    app.run(host=host, port=port, threaded=True)
