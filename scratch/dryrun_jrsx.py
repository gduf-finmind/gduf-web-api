"""Dry-run the jrsx adapter against fixtures to capture assertion values."""

from __future__ import annotations

from pathlib import Path

import httpx

from gduf_web_api import GdufClient
from gduf_web_api.errors import InvalidPageError

FIXTURES = Path("tests/fixtures")

PAGES = {
    "/index/xwxx.htm": "jrsx_xwxx.html",
    "/index/xwxx/25.htm": "jrsx_xwxx_p2.html",
    "/index/tzgg.htm": "jrsx_tzgg.html",
    "/szdw/msfc.htm": "jrsx_msfc.html",
    "/szdw/szgk.htm": "jrsx_szgk.html",
    "/szdw/jsml.htm": "jrsx_jsml.html",
    "/szdw/ssds.htm": "jrsx_ssds.html",
    "/xygk1/xyjj.htm": "jrsx_xyjj.html",
    "/xygk1/xyld.htm": "jrsx_xyld.html",
}


def handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path.startswith("/info/"):
        name = "jrsx_detail.html"
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

for cat in ("xwxx", "tzgg", "msfc", "szgk"):
    try:
        result = client.get_articles(cat, 1, source="jrsx")
        first = result.items[0]
        print(
            f"ART {cat}: n={len(result.items)} total={result.total_items} "
            f"pages={result.total_pages} first_url={first.url} "
            f"first_title={first.title[:40]!r} first_date={first.published_at}"
        )
    except Exception as exc:
        print(f"ART {cat}: ERROR {type(exc).__name__}: {exc}")

for cat in ("jsml", "ssds"):
    try:
        result = client.get_people(cat, 1, source="jrsx")
        first = result.items[0]
        print(
            f"PEO {cat}: n={len(result.items)} total={result.total_items} "
            f"pages={result.total_pages} first={first.name!r} {first.url}"
        )
    except Exception as exc:
        print(f"PEO {cat}: ERROR {type(exc).__name__}: {exc}")

for cat in ("xyjj", "xyld"):
    try:
        result = client.get_content(cat, source="jrsx")
        print(
            f"CON {cat}: title={result.title!r} kind={result.kind} "
            f"len={len(result.content_text)}"
        )
    except Exception as exc:
        print(f"CON {cat}: ERROR {type(exc).__name__}: {exc}")

try:
    result = client.get_detail("https://jrsx.gduf.edu.cn/info/1055/3611.htm", source="jrsx")
    print(
        "DET: title=", result.title[:40],
        "| pub=", result.published_at,
        "| attr=", result.attribution,
        "| prev=", result.previous_url,
        "| next=", result.next_url,
        "| atts=", len(result.attachments),
        "| textlen=", len(result.content_text),
    )
except Exception as exc:
    print("DET ERROR:", type(exc).__name__, exc)

try:
    page2 = client.get_articles("xwxx", 2, source="jrsx")
    print(
        "P2 xwxx: n=", len(page2.items),
        "first=", page2.items[0].title[:30],
        page2.items[0].url,
        page2.items[0].published_at,
    )
except Exception as exc:
    print("P2 ERROR:", type(exc).__name__, exc)

try:
    client.get_articles("xwxx", 27, source="jrsx")
except InvalidPageError as exc:
    print("InvalidPage OK:", exc)
