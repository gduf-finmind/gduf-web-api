"""Probe the five new college sites: reachability, title, nav columns, templates."""

from __future__ import annotations

import json
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

SITES = {
    "gjjrx": "https://gjjrx.gduf.edu.cn/",
    "jmx": "https://jmx.gduf.edu.cn/",
    "gsgl": "https://gsgl.gduf.edu.cn/",
    "xxgc": "https://xxgc.gduf.edu.cn/",
    "jrsx": "https://jrsx.gduf.edu.cn/",
}

OUT = Path(__file__).parent / "probed"
OUT.mkdir(exist_ok=True)


def probe(name: str, base: str) -> dict:
    client = httpx.Client(
        timeout=20.0,
        follow_redirects=True,
        headers={"User-Agent": "gduf-web-api/0.3.0 (+https://pypi.org/project/gduf-web-api/)"},
    )
    report: dict = {"name": name, "base": base, "errors": []}
    try:
        response = client.get(base)
        report["status"] = response.status_code
        report["final_url"] = str(response.url)
        if "charset=" not in response.headers.get("content-type", "").lower():
            response.encoding = "utf-8"
        html = response.text
    except Exception as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
        return report
    (OUT / f"{name}_home.html").write_text(html, encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    report["title"] = soup.title.get_text(strip=True) if soup.title else None
    report["has_vsb_list_rows"] = len(soup.select("li[id^='line_']"))
    report["has_vsb_content"] = len(soup.select("[id^='vsb_content']"))
    report["has_search_jsp"] = bool(re.search(r"search\.jsp", html))
    report["page_marker"] = re.search(r"共\s*\d+\s*条\s*\d+\s*/\s*\d+", html)
    # collect internal nav links to discover column paths
    from urllib.parse import urljoin, urlparse

    host = urlparse(base).netloc
    seen: set[str] = set()
    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href"))
        absolute = urljoin(base, href)
        if urlparse(absolute).netloc != host:
            continue
        path = urlparse(absolute).path
        if path in seen:
            continue
        seen.add(path)
        links.append(f"{path}  {anchor.get_text(' ', strip=True)[:30]}")
    report["links"] = links
    return report


def main() -> None:
    for name, base in SITES.items():
        report = probe(name, base)
        print(json.dumps(report, ensure_ascii=False, indent=1))
        print("=" * 70)


if __name__ == "__main__":
    main()
