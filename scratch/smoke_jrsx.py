"""Live smoke test for the jrsx adapter against https://jrsx.gduf.edu.cn/."""

from __future__ import annotations

from gduf_web_api import GdufClient

client = GdufClient(retries=1)

for cat in ("xwxx", "tzgg", "msfc", "szgk"):
    result = client.get_articles(cat, 1, source="jrsx")
    first = result.items[0]
    print(
        f"ART {cat}: n={len(result.items)} total={result.total_items} pages={result.total_pages} "
        f"first={first.title[:26]!r} {first.published_at}"
    )

for cat in ("jsml", "ssds"):
    result = client.get_people(cat, 1, source="jrsx")
    print(
        f"PEO {cat}: total={result.total_items} pages={result.total_pages} "
        f"first={result.items[0].name}"
    )

for cat in ("xyjj", "xyld"):
    result = client.get_content(cat, source="jrsx")
    print(f"CON {cat}: title={result.title!r}")

summary = client.get_articles("xwxx", 1, source="jrsx").items[0]
detail = client.get_detail(summary, source="jrsx")
print(f"DET: title={detail.title[:26]!r} pub={detail.published_at} attr={detail.attribution}")
