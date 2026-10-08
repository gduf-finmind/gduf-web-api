"""Test the gjjrx search.jsp endpoint and dump result structure."""

from __future__ import annotations

import base64
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

keyword = "研究生"
encoded = base64.b64encode(keyword.encode("utf-8")).decode("ascii")
client = httpx.Client(
    timeout=20.0,
    follow_redirects=True,
    headers={"User-Agent": "gduf-web-api/0.3.0 (+https://pypi.org/project/gduf-web-api/)"},
)
try:
    response = client.post(
        "https://gjjrx.gduf.edu.cn/search.jsp",
        params={"wbtreeid": "1001"},
        data={
            "lucenenewssearchkeyword": encoded,
            "_lucenesearchtype": "1",
            "searchScope": "0",
        },
    )
finally:
    client.close()
print("status:", response.status_code, "url:", response.url)
html = response.text
Path("scratch/probed/gjjrx_search_p1.html").write_text(html, encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")
print("title:", soup.title.get_text(strip=True) if soup.title else None)
print("line_ rows:", len(soup.select("li[id^='line_']")))
rows = soup.select("li[id^='line_']")
if rows:
    print("ROW0:", re.sub(r"\s+", " ", str(rows[0]))[:400])
m = re.search(r"共有\s*\d+\s*条.*?共有\s*\d+\s*页.*?当前第\s*\d+\s*页", html, re.S)
print("search page marker:", m.group(0) if m else None)
# any other list-like containers?
for sel in ("ul li", "table tr"):
    print(sel, len(soup.select(sel)))
i = html.find("搜索结果")
print("搜索结果 region:", re.sub(r"\s+", " ", html[i - 100 : i + 500]) if i != -1 else "not found")
