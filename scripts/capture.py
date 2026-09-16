#!/usr/bin/env python3
"""capture.py — 用 Playwright 打开抖音视频页，拦截 douyinvod 视频/音频流直链。

前置依赖:
  - pip install playwright && playwright install chromium   （或本机已装 Google Chrome）
  - 导出抖音登录 cookie 为 Netscape 格式文件（默认 ~/.douyin_cookies.txt）
    方式 A（推荐，需先 pip install browser-cookie3）:
        python -c "import browser_cookie3, http.cookiejar; \
        cj=browser_cookie3.load_domain('douyin.com'); \
        j=http.cookiejar.MozillaCookieJar('~/.douyin_cookies.txt'); \
        for c in cj: j.set_cookie(c); j.save()"
    方式 B: Chrome 开发者工具 → Application → Cookies → 手动复制为 Netscape 格式

用法:
  python scripts/capture.py --url "https://v.douyin.com/XXXX/" --out downloads/NN_主题 [--name 主题]
                            [--cookies ~/.douyin_cookies.txt] [--use-chromium]

输出: <out>/captured_urls.json  +  <out>/video_srcs.txt
注意: 直链带签名、限时有效，抓到后请尽快跑 mux.py 下载。
"""
import os, sys, json, re, argparse, urllib.request

# 清掉沙箱/系统代理，避免连不上抖音
for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"]:
    os.environ.pop(k, None)
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36")


def resolve_video_id(url):
    """从短链/长链/视频页里提取 15+ 位数字 video id。"""
    m = re.search(r"(?:/video/|vid=)(\d{15,})", url)
    if m:
        return m.group(1)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            final = r.geturl()
        m = re.search(r"/video/(\d{15,})", final)
        if m:
            return m.group(1)
    except Exception as e:
        print("短链解析失败:", e)
    return None


def load_cookies(path):
    cookies = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            domain, _, path_, secure, _, name, value = parts[:7]
            cookies.append({
                "name": name, "value": value,
                "domain": domain.lstrip("."), "path": path_,
                "secure": secure.upper() == "TRUE", "httpOnly": False,
            })
    return cookies


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="抖音视频链接（短链/长链/视频页均可）")
    ap.add_argument("--out", required=True, help="输出目录")
    ap.add_argument("--name", default=None, help="视频文件名（不含扩展名），默认取 out 目录名")
    ap.add_argument("--cookies", default=os.environ.get("DOUYIN_COOKIES",
                        os.path.expanduser("~/.douyin_cookies.txt")),
                    help="Netscape cookie 文件")
    ap.add_argument("--use-chromium", action="store_true",
                    help="用 playwright 自带 chromium（默认用系统 Chrome channel）")
    args = ap.parse_args()

    vid = resolve_video_id(args.url)
    if not vid:
        sys.exit("ERROR: 无法从链接解析出 video id")
    os.makedirs(args.out, exist_ok=True)
    name = args.name or os.path.basename(args.out.rstrip("/"))
    cookies = load_cookies(args.cookies)

    captured = []

    def on_response(resp):
        u = resp.url
        ct = resp.headers.get("content-type", "")
        if any(x in u for x in ["douyinvod", ".m3u8", "playwm", "playApi",
                                 "aweme/detail", "v3-web", "playurl"]) \
           or "video" in ct or "application/vnd.apple.mpegurl" in ct:
            captured.append({"url": u, "ct": ct, "status": resp.status})

    with sync_playwright() as p:
        if args.use_chromium:
            browser = p.chromium.launch(headless=True,
                                        args=["--disable-blink-features=AutomationControlled"])
        else:
            browser = p.chromium.launch(channel="chrome", headless=True,
                                        args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 800})
        ctx.add_cookies(cookies)
        ctx.on("response", on_response)
        page = ctx.new_page()
        print(">> 打开视频页", vid)
        page.goto(f"https://www.douyin.com/video/{vid}",
                  wait_until="domcontentloaded", timeout=40000)
        try:
            page.wait_for_timeout(8000)
            page.wait_for_selector("video", timeout=15000)
        except Exception as e:
            print("wait video warn:", e)
        page.wait_for_timeout(5000)
        vids = page.evaluate("""() => Array.from(document.querySelectorAll('video'))
            .map(v => (v.currentSrc || v.src ||
                (v.querySelector('source') && v.querySelector('source').src) || ''))
            .filter(Boolean)""")
        print("video srcs:", vids)
        print(f"=== 捕获 {len(captured)} 个响应 ===")
        for c in captured:
            print(c["status"], c["ct"], c["url"][:160])
        with open(f"{args.out}/captured_urls.json", "w") as f:
            json.dump(captured, f, ensure_ascii=False, indent=2)
        with open(f"{args.out}/video_srcs.txt", "w") as f:
            f.write("\n".join(vids))
        browser.close()
    print("DONE ->", f"{args.out}/captured_urls.json")


if __name__ == "__main__":
    main()
