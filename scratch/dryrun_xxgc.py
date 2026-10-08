"""Dry-run the xxgc adapter against fixtures to capture assertion values."""

from __future__ import annotations

import httpx
from pathlib import Path

from gduf_web_api import GdufClient
from gduf_web_api.errors import InvalidPageError

FIXTURES = Path("tests/fixtures")

PAGES = {
    "/index/xyxw.htm": "xxgc_xyxw.html",
    "/index/xyxw/21.htm": "xxgc_xyxw_p2.html",
    "/tzgg.htm": "xxgc_tzgg.html",
    "/index/jxhd.htm": "xxgc_jxhd.html",
    "/szdw/jsml.htm": "xxgc_jsml.html",
    "/szdw/jfry.htm": "xxgc_jfry.html",
    "/szdw/szgk.htm": "xxgc_szgk.html",
    "/xygk/xyjj.htm": "xxgc_xyjj.html",
    "/xygk/ldjs.htm": "xxgc_ldjs.html",
}


def handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path.startswith("/info/"):
        name = "xxgc_detail.html"
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

for cat in ("xyxw", "tzgg", "jxhd"):
    try:
        result = client.get_articles(cat, 1, source="xxgc")
        first = result.items[0]
        print(
            f"ART {cat}: n={len(result.items)} total={result.total_items} pages={result.total_pages} "
            f"first_url={first.url} first_title={first.title[:40]!r} first_date={first.published_at}"
        )
    except Exception as exc:
        print(f"ART {cat}: ERROR {type(exc).__name__}: {exc}")

for cat in ("jsml", "jfry"):
    try:
        result = client.get_people(cat, 1, source="xxgc")
        first = result.items[0]
        print(
            f"PEO {cat}: n={len(result.items)} total={result.total_items} pages={result.total_pages} "
            f"first_name={first.name!r} first_url={first.url}"
        )
        print(f"      bio={first.responsibility!r}"[:160])
        print(f"      img={first.image_url!r}")
    except Exception as exc:
        print(f"PEO {cat}: ERROR {type(exc).__name__}: {exc}")

for cat in ("xyjj", "ldjs", "szgk"):
    try:
        result = client.get_content(cat, source="xxgc")
        print(f"CON {cat}: title={result.title!r} kind={result.kind} len={len(result.content_text)}")
    except Exception as exc:
        print(f"CON {cat}: ERROR {type(exc).__name__}: {exc}")

try:
    result = client.get_detail("https://xxgc.gduf.edu.cn/info/1055/3902.htm", source="xxgc")
    print(
        "DET: title=", result.title[:40],
        "| pub=", result.published_at,
        "| attr=", result.attribution,
        "| prev=", result.previous_url,
        "| next=", result.next_url,
        "| atts=", len(result.attachments),
        "| imgs=", len(result.images),
        "| textlen=", len(result.content_text),
    )
except Exception as exc:
    print("DET ERROR:", type(exc).__name__, exc)

try:
    page2 = client.get_articles("xyxw", 2, source="xxgc")
    print(
        "P2 xyxw: n=", len(page2.items),
        "first=", page2.items[0].title[:30],
        page2.items[0].url,
        page2.items[0].published_at,
    )
except Exception as exc:
    print("P2 ERROR:", type(exc).__name__, exc)

try:
    client.get_articles("xyxw", 23, source="xxgc")
except InvalidPageError as exc:
    print("InvalidPage OK:", exc)
