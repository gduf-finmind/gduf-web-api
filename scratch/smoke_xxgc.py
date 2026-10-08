"""Live smoke test for the xxgc adapter against https://xxgc.gduf.edu.cn/."""

from __future__ import annotations

from gduf_web_api import GdufClient

client = GdufClient(retries=1)

for cat in ("xyxw", "tzgg", "jxhd"):
    result = client.get_articles(cat, 1, source="xxgc")
    first = result.items[0]
    print(
        f"ART {cat}: n={len(result.items)} total={result.total_items} pages={result.total_pages} "
        f"first={first.title[:26]!r} {first.published_at}"
    )

for cat in ("jsml", "jfry"):
    result = client.get_people(cat, 1, source="xxgc")
    first = result.items[0]
    print(
        f"PEO {cat}: total={result.total_items} pages={result.total_pages} "
        f"first={first.name} bio_ok={bool(first.responsibility)}"
    )

for cat in ("xyjj", "ldjs", "szgk"):
    result = client.get_content(cat, source="xxgc")
    print(f"CON {cat}: title={result.title!r}")

summary = client.get_articles("xyxw", 1, source="xxgc").items[0]
detail = client.get_detail(summary, source="xxgc")
print(
    f"DET: title={detail.title[:26]!r} pub={detail.published_at} "
    f"attr={detail.attribution} next={detail.next_url}"
)
