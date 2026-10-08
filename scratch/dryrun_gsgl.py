"""Dry-run the gsgl adapter against fixtures to capture assertion values."""

from __future__ import annotations

from pathlib import Path

import httpx

from gduf_web_api import GdufClient
from gduf_web_api.errors import InvalidPageError

FIXTURES = Path("tests/fixtures")

PAGES = {
    "/xwxx.htm": "gsgl_xwxx.html",
    "/jxky1/jyhd.htm": "gsgl_jyhd.html",
    "/jxky1/jyhd/3.htm": "gsgl_jyhd_p2.html",
    "/djgz/djhd.htm": "gsgl_djhd.html",
    "/xsgz/xshd.htm": "gsgl_xshd.html",
    "/szdw/js.htm": "gsgl_js.html",
    "/szdw/fjs.htm": "gsgl_fjs.html",
    "/szdw/bs.htm": "gsgl_bs.html",
    "/szdw/glry.htm": "gsgl_glry.html",
    "/szdw/szgk.htm": "gsgl_szgk.html",
    "/xygk/ykjj.htm": "gsgl_ykjj.html",
    "/xygk/ldjs.htm": "gsgl_ldjs.html",
}


def handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path.startswith("/info/"):
        name = "gsgl_detail.html"
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

for cat in ("xwxx", "jyhd", "djhd", "xshd"):
    try:
        result = client.get_articles(cat, 1, source="gsgl")
        first = result.items[0]
        print(
            f"ART {cat}: n={len(result.items)} total={result.total_items} "
            f"pages={result.total_pages} first_url={first.url} "
            f"first_title={first.title[:34]!r} first_date={first.published_at}"
        )
    except Exception as exc:
        print(f"ART {cat}: ERROR {type(exc).__name__}: {exc}")

for cat in ("js", "fjs", "bs"):
    try:
        result = client.get_people(cat, 1, source="gsgl")
        first = result.items[0]
        print(
            f"PEO {cat}: n={len(result.items)} total={result.total_items} "
            f"pages={result.total_pages} first_name={first.name!r} first_url={first.url}"
        )
    except Exception as exc:
        print(f"PEO {cat}: ERROR {type(exc).__name__}: {exc}")

for cat in ("ykjj", "ldjs", "szgk", "glry"):
    try:
        result = client.get_content(cat, source="gsgl")
        print(
            f"CON {cat}: title={result.title!r} kind={result.kind} "
            f"len={len(result.content_text)}"
        )
    except Exception as exc:
        print(f"CON {cat}: ERROR {type(exc).__name__}: {exc}")

try:
    result = client.get_detail("https://gsgl.gduf.edu.cn/info/1137/3494.htm", source="gsgl")
    print(
        "DET: title=", result.title[:36],
        "| pub=", result.published_at,
        "| attr=", result.attribution,
        "| prev=", result.previous_url,
        "| next=", result.next_url,
        "| atts=", len(result.attachments),
        "| imgs=", len(result.images),
    )
except Exception as exc:
    print("DET ERROR:", type(exc).__name__, exc)

try:
    client.get_articles("jyhd", 1, source="gsgl")
    page2 = client.get_articles("jyhd", 2, source="gsgl")
    print(
        "P2 jyhd: n=", len(page2.items),
        "first=", page2.items[0].title[:34],
        page2.items[0].url,
        page2.items[0].published_at,
    )
except Exception as exc:
    print("P2 ERROR:", type(exc).__name__, exc)

try:
    client.get_articles("jyhd", 5, source="gsgl")
except InvalidPageError as exc:
    print("InvalidPage OK:", exc)
