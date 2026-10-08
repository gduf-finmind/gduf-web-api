"""Fetch page-2 fixtures and search page 2 for the five new sites."""

from __future__ import annotations

import base64
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

OUT = Path("tests/fixtures")
UA = "gduf-web-api/0.3.0 (+https://pypi.org/project/gduf-web-api/)"

PAGES: dict[str, list[tuple[str, str]]] = {
    "gjjrx": [
        ("https://gjjrx.gduf.edu.cn/xwzx/xyxw/10.htm", "gjjrx_xyxw_p2.html"),
        ("https://gjjrx.gduf.edu.cn/szdw/zrjs/1.htm", "gjjrx_zrjs_p2.html"),
    ],
    "jmx": [("https://jmx.gduf.edu.cn/index/xwgg/14.htm", "jmx_xwgg_p2.html")],
    "gsgl": [("https://gsgl.gduf.edu.cn/jxky1/jyhd/3.htm", "gsgl_jyhd_p2.html")],
    "xxgc": [("https://xxgc.gduf.edu.cn/index/xyxw/21.htm", "xxgc_xyxw_p2.html")],
    "jrsx": [("https://jrsx.gduf.edu.cn/index/xwxx/25.htm", "jrsx_xwxx_p2.html")],
}

client = httpx.Client(
    timeout=20.0,
    follow_redirects=True,
    headers={"User-Agent": UA},
)
for _code, entries in PAGES.items():
    for url, name in entries:
        response = client.get(url)
        html = response.text
        (OUT / name).write_text(html, encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("li[id^='line_']")
        marker = re.search(r"共\s*\d+\s*条\s*\d+\s*/\s*\d+", soup.get_text(" ", strip=True))
        first = None
        if rows:
            anchor = rows[0].find("a", href=True)
            if anchor is not None:
                first = re.sub(r"\s+", " ", anchor.get_text(" ", strip=True))[:40]
        print(
            f"{name}: status={response.status_code} rows={len(rows)} "
            f"marker={marker.group(0) if marker else None} first={first}"
        )

# gjjrx search page 2
encoded = base64.b64encode("研究生".encode()).decode("ascii")
response = client.get(
    "https://gjjrx.gduf.edu.cn/search.jsp",
    params={
        "wbtreeid": "1001",
        "searchScope": "0",
        "currentnum": 2,
        "newskeycode2": encoded,
    },
)
(OUT / "gjjrx_search_p2.html").write_text(response.text, encoding="utf-8")
soup = BeautifulSoup(response.text, "html.parser")
print(
    "gjjrx_search_p2.html: status=",
    response.status_code,
    "rows=",
    len(soup.select("li:has(b.fr)")),
)
client.close()
