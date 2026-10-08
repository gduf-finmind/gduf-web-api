"""Dry-run the gjjrx adapter against fixtures to capture assertion values."""

from __future__ import annotations

import httpx
from pathlib import Path

from gduf_web_api import GdufClient
from gduf_web_api.errors import InvalidPageError

FIXTURES = Path("tests/fixtures")


def handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/search.jsp":
        if request.method == "POST":
            name = "gjjrx_search_p1.html"
        else:
            current = request.url.params.get("currentnum")
            name = "gjjrx_search_p2.html" if current == "2" else "gjjrx_search_p1.html"
    elif path.startswith("/info/"):
        name = "gjjrx_detail.html"
    else:
        pages = {
            "/xwzx/xyxw.htm": "gjjrx_xyxw.html",
            "/xwzx/xyxw/10.htm": "gjjrx_xyxw_p2.html",
            "/xwzx/tzgg.htm": "gjjrx_tzgg.html",
            "/xwzx/jxky.htm": "gjjrx_jxky.html",
            "/xwzx/dtxg.htm": "gjjrx_dtxg.html",
            "/xwzx/gjzk.htm": "gjjrx_gjzk.html",
            "/szdw/zrjs.htm": "gjjrx_zrjs.html",
            "/szdw/zrjs/2.htm": "gjjrx_zrjs_p2.html",
            "/szdw/jfry.htm": "gjjrx_jfry.html",
            "/szdw/bsfc.htm": "gjjrx_bsfc.html",
            "/szdw/jsfc.htm": "gjjrx_jsfc.html",
            "/xygk/xyld.htm": "gjjrx_xrld.html",
            "/xygk/xyjj.htm": "gjjrx_xyjj.html",
            "/xygk/jgsz.htm": "gjjrx_jgsz.html",
            "/szdw/szgk.htm": "gjjrx_szgk.html",
        }
        if path not in pages:
            return httpx.Response(404, request=request)
        name = pages[path]
    return httpx.Response(
        200,
        text=(FIXTURES / name).read_text(encoding="utf-8"),
        headers={"content-type": "text/html; charset=utf-8"},
        request=request,
    )


client = GdufClient(transport=httpx.MockTransport(handler), retries=0)

articles = ("xyxw", "tzgg", "jxky", "dtxg", "gjzk")
for cat in articles:
    try:
        result = client.get_articles(cat, 1, source="gjjrx")
        first = result.items[0]
        print(
            f"ART {cat}: n={len(result.items)} total={result.total_items} pages={result.total_pages} "
            f"first_url={first.url} first_title={first.title!r} first_date={first.published_at}"
        )
    except Exception as exc:
        print(f"ART {cat}: ERROR {type(exc).__name__}: {exc}")

for cat in ("xrld", "zrjs", "jfry", "bsfc", "jsfc"):
    try:
        result = client.get_people(cat, 1, source="gjjrx")
        first = result.items[0]
        print(
            f"PEO {cat}: n={len(result.items)} total={result.total_items} pages={result.total_pages} "
            f"first_name={first.name!r} first_role={first.role!r} first_url={first.url} img={first.image_url is not None}"
        )
    except Exception as exc:
        print(f"PEO {cat}: ERROR {type(exc).__name__}: {exc}")

for cat in ("xyjj", "jgsz", "szgk"):
    try:
        result = client.get_content(cat, source="gjjrx")
        print(f"CON {cat}: title={result.title!r} kind={result.kind} len={len(result.content_text)}")
    except Exception as exc:
        print(f"CON {cat}: ERROR {type(exc).__name__}: {exc}")

try:
    result = client.get_detail("https://gjjrx.gduf.edu.cn/info/1056/2284.htm", source="gjjrx")
    print(
        "DET:",
        "title=", result.title,
        "| pub=", result.published_at,
        "| attr=", result.attr if hasattr(result, "attr") else result.attribution,
        "| prev=", result.previous_url,
        "| next=", result.next_url,
        "| atts=", len(result.attachments),
        "| imgs=", len(result.images),
    )
except Exception as exc:
    print("DET ERROR:", type(exc).__name__, exc)

try:
    result = client.search("研究生", 1, source="gjjrx")
    first = result.items[0]
    print(
        "SRCH: n=", len(result.items), "total=", result.total_items, "pages=", result.total_pages,
        "first_url=", first.url, "first_title=", first.title[:30], "first_date=", first.published_at,
    )
except Exception as exc:
    print("SRCH ERROR:", type(exc).__name__, exc)

try:
    result = client.search("研究生", 2, source="gjjrx")
    print("SRCH2: n=", len(result.items), "total=", result.total_items, "pages=", result.total_pages, "first_url=", result.items[0].url)
except Exception as exc:
    print("SRCH2 ERROR:", type(exc).__name__, exc)

# second pages
for cat, page in (("xyxw", 2), ("zrjs", 2)):
    try:
        client.get_articles(cat, 1, source="gjjrx") if cat == "xyxw" else client.get_people(cat, 1, source="gjjrx")
        if cat == "xyxw":
            result = client.get_articles(cat, page, source="gjjrx")
        else:
            result = client.get_people(cat, page, source="gjjrx")
        first = result.items[0]
        print(f"P2 {cat}: n={len(result.items)} first={first.title if hasattr(first, 'title') else first.name!r} url={first.url}")
    except Exception as exc:
        print(f"P2 {cat}: ERROR {type(exc).__name__}: {exc}")

try:
    client.get_articles("xyxw", 12, source="gjjrx")
except InvalidPageError as exc:
    print("InvalidPage OK:", exc)
