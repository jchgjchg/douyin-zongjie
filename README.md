# douyin-zongjie · 抖音视频转写与分析流水线

把抖音视频变成**可检索的结构化分析仓库**：下载视频 → 抽音频 → 语音转写 → 术语清洗 → LLM 写分析报告。

本仓库既是一份**成品库**（已沉淀 86 份抖音视频的结构化分析报告），也是一套**可复用的开源流水线**（`scripts/`）——任何人 clone 后都能把自己的抖音视频跑成同样的格式。

---

## 目录结构

```
douyin-zongjie/
├── scripts/              # 流水线脚本（核心，自包含）
│   ├── capture.py        # ① 抓流：Playwright 打开视频页，拦截 douyinvod 视频/音频直链
│   ├── mux.py            # ② 合成：下载两流并用 ffmpeg 合成完整视频
│   ├── transcribe.py     # ③ 转写：whisper（mlx/faster）生成 SRT + 文本稿
│   ├── clean.py          # ④ 清洗：修正专名/口音误写
│   └── analyze.py        # ⑤ 分析：OpenAI 兼容接口写结构化报告
├── run.sh               # 一条命令跑完 ①~⑤
├── requirements.txt     # Python 依赖
├── analysis/            # 86 份分析报告（样例产出，按主题分组见下）
└── downloads/           # 各视频的字幕稿（transcript.txt / .srt / transcript_clean.txt）
```

> 说明：`downloads/` 下只入库了**字幕文本**（约 5MB），原始视频/音频（共 ~5.1GB）因 GitHub 单文件 100MB 限制未入库，请用 `scripts/` 在自己机器上重新生成。

---

## 前置依赖

| 依赖 | 用途 | 安装 |
|---|---|---|
| Python 3.11+ | 运行脚本 | 系统自带 / pyenv |
| ffmpeg | 抽音频、合成视频 | `brew install ffmpeg`（macOS）/ `apt install ffmpeg`（Linux） |
| Google Chrome **或** playwright chromium | 抓流需要真实浏览器 | 已装 Chrome 即可；否则 `playwright install chromium` |
| 抖音登录 cookie（Netscape 格式） | 绕过未登录限制 | 见下方「导出 cookie」 |
| OpenAI 兼容 API key | 第 ⑤ 步写报告 | 任意 OpenAI / 兼容网关；或本地 FreeLLMAPI |

### 导出抖音 cookie

```bash
pip install browser-cookie3
python -c "import browser_cookie3, http.cookiejar; \
cj=browser_cookie3.load_domain('douyin.com'); \
j=http.cookiejar.MozillaCookieJar('~/.douyin_cookies.txt'); \
[add and save cookies...]"
```

更稳妥的方式：在**已登录抖音**的 Chrome 里打开开发者工具 → Application → Cookies，把 `sessionid` 等字段手动整理成 Netscape 格式（每行 7 个 tab 分隔字段）保存到 `~/.douyin_cookies.txt`。cookie 默认读取路径可用环境变量 `DOUYIN_COOKIES` 覆盖。

---

## 快速开始

```bash
git clone https://github.com/jchgjchg/douyin-zongjie.git
cd douyin-zongjie
pip install -r requirements.txt
playwright install chromium        # 若用自带 chromium（否则用系统 Chrome）

# 配置分析用的模型（OpenAI 兼容）
export OPENAI_API_KEY=sk-xxxx
export OPENAI_BASE_URL=https://api.openai.com/v1   # 或本地网关 http://127.0.0.1:3001/v1
export OPENAI_MODEL=gpt-4o-mini

# 一条命令跑完整条流水线
bash run.sh "https://v.douyin.com/XXXX/" downloads/01_示例 示例
```

跑完会在 `downloads/01_示例/` 生成视频与字幕，并在 `analysis/分析报告_示例.md` 生成报告。

---

## 分步执行（想看清每一步时）

```bash
# ① 抓流（输出 captured_urls.json）
python scripts/capture.py --url "https://v.douyin.com/XXXX/" \
    --out downloads/01_示例 --name 示例

# ② 合成视频
python scripts/mux.py --out downloads/01_示例 --name 示例

# ③ 转写（Apple Silicon 走 mlx-whisper；其他平台自动回退 faster-whisper）
python scripts/transcribe.py downloads/01_示例/示例.mp4 downloads/01_示例

# ④ 清洗专名误写
python scripts/clean.py downloads/01_示例/transcript.txt \
    downloads/01_示例/transcript_clean.txt

# ⑤ 调 LLM 写报告
python scripts/analyze.py downloads/01_示例/transcript_clean.txt \
    analysis/分析报告_示例.md
```

### 关于第 ③ 步的转写后端
- **Apple Silicon（M 系列）**：自动用 `mlx-whisper`，GPU 加速、默认离线（吃本地 HF 缓存）。
- **其他平台**：自动回退 `faster-whisper`（首次需联网下载模型；如遇离线限制先 `export HF_HUB_OFFLINE=0`）。

### 关于第 ⑤ 步的模型
`analyze.py` 走标准 OpenAI Chat Completions 协议，读三个环境变量：
- `OPENAI_API_KEY`（必填）
- `OPENAI_BASE_URL`（默认 `https://api.openai.com/v1`，可指向任意兼容网关）
- `OPENAI_MODEL`（默认 `gpt-4o-mini`）

接本地网关（如 FreeLLMAPI）示例：
```bash
export OPENAI_BASE_URL=http://127.0.0.1:3001/v1
export OPENAI_API_KEY=<本地key>
export OPENAI_MODEL=auto
```

---

## 报告长什么样

`analyze.py` 固定输出 5 段结构（见 `scripts/analyze.py` 的 SYSTEM_PROMPT）：
1. 一句话核心
2. 内容结构与要点
3. 关键概念/模型解析
4. 观点与可信度评估（区分技术实质与营销话术）
5. 实战建议

已沉淀的 86 份报告主题分布（详见 `analysis/`）：
- 电商 / 带货 / 短视频运营
- AI / 技术实操（Vibe Coding、MCP、量化数据源…）
- 搞钱 / 副业 / 思维（姜胡说方法、AI 博主变现…）
- 人文 / 认知 / 社会
- 知识管理 / 学习法

---

## 免责声明

本工具仅用于**个人学习、内容归档与本地分析**。下载他人视频请遵守抖音用户协议与当地版权法规，勿用于商业分发或侵权用途。cookie 与 API key 属个人凭证，请勿提交进仓库。
