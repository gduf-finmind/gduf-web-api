"""Dry-run the jmx adapter against fixtures to capture assertion values."""

from __future__ import annotations

from pathlib import Path

import httpx

from gduf_web_api import GdufClient
from gduf_web_api.errors import InvalidPageError

FIXTURES = Path("tests/fixtures")

PAGES = {
    "/index/xwgg.htm": "jmx_xwgg.html",
    "/index/xwgg/14.htm": "jmx_xwgg_p2.html",
    "/index/djhd.htm": "jmx_djhd.html",
    "/index/jxhd.htm": "jmx_jxhd.html",
    "/index/kyhd.htm": "jmx_kyhd.html",
    "/index/ssfc.htm": "jmx_ssfc.html",
    "/xygk/xyjj.htm": "jmx_xyjj.html",
    "/xygk/szdw.htm": "jmx_szdw.html",
    "/xygk/jgsz.htm": "jmx_jgsz.html",
    "/xygk/xrld.htm": "jmx_xrld.html",
}


def handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path.startswith("/info/"):
        name = "jmx_detail.html"
    elif path in PAGES:
        name = PAGES[path]
    else:
        return httpx.Response(404, request=request)
    return httpx.Response(
        200,
        text=(FIXTURES / name).read_text(encoding="utf-8"),
        headers={"content-type": "text/html; charset=utf-8"},
        request=request,
    )


client = GdufClient(transport=httpx.MockTransport(handler), retries=0)

for cat in ("xwgg", "djhd", "jxhd", "kyhd", "ssfc", "xyjj", "szdw"):
    try:
        result = client.get_articles(cat, 1, source="jmx")
        first = result.items[0]
        print(
            f"ART {cat}: n={len(result.items)} total={result.total_items} "
            f"pages={result.total_pages} first_url={first.url} "
            f"first_title={first.title[:36]!r} first_date={first.published_at}"
        )
    except Exception as exc:
        print(f"ART {cat}: ERROR {type(exc).__name__}: {exc}")

for cat in ("jgsz", "xrld"):
    try:
        result = client.get_content(cat, source="jmx")
        print(
            f"CON {cat}: title={result.title!r} kind={result.kind} "
            f"len={len(result.content_text)}"
        )
    except Exception as exc:
        print(f"CON {cat}: ERROR {type(exc).__name__}: {exc}")

try:
    result = client.get_detail("https://jmx.gduf.edu.cn/info/1093/3725.htm", source="jmx")
    print(
        "DET: title=", result.title[:40],
        "| pub=", result.published_at,
        "| attr=", result.attribution,
        "| prev=", result.previous_url,
        "| next=", result.next_url,
        "| atts=", result.attachments,
        "| imgs=", len(result.images),
    )
except Exception as exc:
    print("DET ERROR:", type(exc).__name__, exc)

try:
    client.get_articles("xwgg", 1, source="jmx")
    page2 = client.get_articles("xwgg", 2, source="jmx")
    print(
        "P2 xwgg: n=", len(page2.items), "first=", page2.items[0].title[:40],
        page2.items[0].url, page2.items[0].published_at,
    )
except Exception as exc:
    print("P2 ERROR:", type(exc).__name__, exc)

try:
    client.get_articles("xwgg", 16, source="jmx")
except InvalidPageError as exc:
    print("InvalidPage OK:", exc)
