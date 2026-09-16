#!/usr/bin/env python3
"""clean.py — 清洗 whisper 转写文本（修正专名/口音误写），输出字幕稿件。

用法:
  python scripts/clean.py <raw_txt> [out_txt]
  out_txt 缺省时写回 <raw_txt 去扩展名>_clean.txt

REPLACEMENTS 是基于抖音技术口播常见 whisper 误写整理的起步词表，
遇到没覆盖到的错别字，直接往下面列表追加 (误写, 正写) 即可。
"""
import sys

REPLACEMENTS = [
    # 工具/平台专名（whisper 高频误写）
    ("workbody", "WorkBuddy"), ("做包", "Cursor"),
    ("TASIE", "Tushare"), ("Bailstock", "BaoStock"),
    ("郭友才", "郭有才"), ("真点", "争点"),
    ("三合大神", "三和大神"), ("木旦", "穆旦"),
    # 口语/口音常见错字
    ("横平", "横屏"),
    # 会话/神经类（视具体视频保留，下同源内容可复用）
    ("绘画状态", "会话状态"), ("绘画内", "会话内"),
    ("同一个绘画", "同一个会话"), ("绘画", "会话"),
    ("鲜鹅叶", "前额叶"), ("前额页", "前额叶"),
    ("神经地质", "神经递质"), ("神经突出", "神经突触"),
]


def main():
    if len(sys.argv) < 2:
        print("用法: python clean.py <raw_txt> [out_txt]")
        sys.exit(1)
    raw, out = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2
                             else sys.argv[1].replace(".txt", "_clean.txt"))
    txt = open(raw, encoding="utf-8").read()
    for a, b in REPLACEMENTS:
        txt = txt.replace(a, b)
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"清洗完成：{len(lines)} 段 -> {out}")


if __name__ == "__main__":
    main()
