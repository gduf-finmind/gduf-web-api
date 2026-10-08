"""Live smoke test for the gsgl adapter against https://gsgl.gduf.edu.cn/."""

from __future__ import annotations

from gduf_web_api import GdufClient

client = GdufClient(retries=1)

for cat in ("xwxx", "jyhd", "djhd", "xshd"):
    result = client.get_articles(cat, 1, source="gsgl")
    first = result.items[0]
    print(
        f"ART {cat}: n={len(result.items)} total={result.total_items} pages={result.total_pages} "
        f"first={first.title[:28]!r} {first.published_at}"
    )

for cat in ("js", "fjs", "bs"):
    result = client.get_people(cat, 1, source="gsgl")
    print(f"PEO {cat}: total={result.total_items} pages={result.total_pages} first={result.items[0].name}")

for cat in ("ykjj", "ldjs", "szgk", "glry"):
    result = client.get_content(cat, source="gsgl")
    print(f"CON {cat}: title={result.title!r}")

summary = client.get_articles("jyhd", 1, source="gsgl").items[0]
detail = client.get_detail(summary, source="gsgl")
print(f"DET: title={detail.title[:30]!r} pub={detail.published_at} next={detail.next_url}")
