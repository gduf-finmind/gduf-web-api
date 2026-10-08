"""Dump special regions from saved pages: meta blocks, leader pages, teacher cards, search."""

from __future__ import annotations

import re
import sys
from pathlib import Path

html = Path(sys.argv[1]).read_text(encoding="utf-8")
mode = sys.argv[2] if len(sys.argv) > 2 else "meta"

if mode == "meta":
    # print the article detail region: h1/title + meta line + prev/next
    for marker in ("发布日期", "发布时间", "上一篇", "下一篇", "附件", "点击数", "浏览次数", "来源"):
        i = html.find(marker)
        if i != -1:
            snippet = html[max(0, i - 300) : i + 300]
            snippet = re.sub(r'\s+', " ", snippet)
            print(f"--- {marker} @{i}")
            print(snippet[:700])
            print()
    m = re.search(r"<h1[^>]*>.*?</h1>", html, re.S)
    if m:
        print("--- h1:", re.sub(r"\s+", " ", m.group(0))[:300])
    t = re.search(r"<title>.*?</title>", html, re.S)
    if t:
        print("--- title:", t.group(0)[:300])
elif mode == "body":
    # print everything between <body> and the main content container start
    i = html.find("尾页")
    print(html[:6000])
elif mode == "card":
    i = html.find("main_rpicR")
    print(re.sub(r"\s+", " ", html[i - 500 : i + 1500])[:2200])
