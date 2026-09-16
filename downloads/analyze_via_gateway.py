#!/usr/bin/env python3
"""调用本地 FreeLLMAPI 网关分析字幕稿件，输出结构化分析报告。
用法: python analyze_via_gateway.py <transcript_clean.txt> <output.md>
模型: auto（网关自动路由选最佳模型）
兜底: 网关不可用时（429/超时/网络错误），助手会直接分析。
"""
import json, sys, time, urllib.request, urllib.error

API_URL = "http://127.0.0.1:3001/v1/chat/completions"
API_KEY = "freellmapi-7d93637e459ce5ea40fc98870a0af6821c3b06b3d5c4d377"
MODEL = "auto"
MAX_RETRIES = 3
RETRY_DELAY = 5

SYSTEM_PROMPT = (
    "你是短视频内容分析师。用户会给你一段抖音视频的字幕稿件（逐段文本）。"
    "请输出一份完整的结构化分析报告（Markdown），必须包含以下 5 个部分，每个部分不少于 2-3 句：\n"
    "1. 一句话核心（25 字以内）\n"
    "2. 内容结构与要点（按逻辑段落拆解，每部分 1-2 句）\n"
    "3. 关键概念/模型解析（如有专业概念，用通俗语言解释；无则跳过）\n"
    "4. 观点与可信度评估（区分技术实质与营销话术，直接、客观、不吹捧）\n"
    "5. 实战建议（可执行的具体动作，2-3 条）\n"
    "报告用简体中文，控制在 600-800 字，要点化，不要空话。"
)

def main():
    transcript = open(sys.argv[1], encoding="utf-8").read()
    out_path = sys.argv[2]
    content = None
    for attempt in range(1, MAX_RETRIES + 1):
        body = json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"以下是视频字幕稿件：\n\n{transcript}"},
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
        }).encode("utf-8")
        req = urllib.request.Request(API_URL, data=body, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        })
        try:
            print(f"调用网关中（第 {attempt} 次）...", flush=True)
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.load(resp)
            content = data["choices"][0]["message"]["content"]
            # 内容有效性检查：如果返回的是原文（没分析），重新请求
            if len(content) > len(transcript) * 0.8 and "一句话" not in content[:100]:
                print(f"  返回内容疑似原文（{len(content)} 字符），重新请求...", flush=True)
                if attempt < MAX_RETRIES:
                    continue
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"分析完成 -> {out_path}", flush=True)
            return
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES:
                print(f"429 限流，{RETRY_DELAY}s 后重试...", flush=True)
                time.sleep(RETRY_DELAY)
            else:
                print(f"HTTP 错误 {e.code}，放弃重试", flush=True)
                raise
        except Exception as e:
            print(f"网络错误: {e}，放弃重试", flush=True)
            raise

if __name__ == "__main__":
    main()