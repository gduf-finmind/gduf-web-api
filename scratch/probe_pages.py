"""Fetch key list/static/detail pages for the five new sites and dump structure hints."""

from __future__ import annotations

import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

SITES: dict[str, tuple[str, list[str]]] = {
    "gjjrx": (
        "https://gjjrx.gduf.edu.cn/",
        [
            "/xwzx/xyxw.htm",
            "/xwzx/tzgg.htm",
            "/xwzx/jxky.htm",
            "/xwzx/dtxg.htm",
            "/xwzx/gjzk.htm",
            "/szdw/zrjs.htm",
            "/szdw/jfry.htm",
            "/szdw/bsfc.htm",
            "/szdw/jsfc.htm",
            "/xygk/xyjj.htm",
            "/xygk/jgsz.htm",
            "/xygk/xyld.htm",
            "/szdw/szgk.htm",
            "/info/1056/2284.htm",
        ],
    ),
    "jmx": (
        "https://jmx.gduf.edu.cn/",
        [
            "/index/xwgg.htm",
            "/index/djhd.htm",
            "/index/jxhd.htm",
            "/index/kyhd.htm",
            "/index/ssfc.htm",
            "/xygk/xyjj.htm",
            "/xygk/jgsz.htm",
            "/xygk/xrld.htm",
            "/xygk/szdw.htm",
            "/info/1093/3725.htm",
        ],
    ),
    "gsgl": (
        "https://gsgl.gduf.edu.cn/",
        [
            "/jxky1/jyhd.htm",
            "/xwxx.htm",
            "/djgz/djhd.htm",
            "/xsgz/xshd.htm",
            "/szdw/js.htm",
            "/szdw/fjs.htm",
            "/szdw/bs.htm",
            "/szdw/glry.htm",
            "/szdw/szgk.htm",
            "/xygk/ykjj.htm",
            "/xygk/ldjs.htm",
            "/info/1137/3494.htm",
        ],
    ),
    "xxgc": (
        "https://xxgc.gduf.edu.cn/",
        [
            "/index/xyxw.htm",
            "/tzgg.htm",
            "/index/jxhd.htm",
            "/szdw/jsml.htm",
            "/szdw/jfry.htm",
            "/szdw/szgk.htm",
            "/xygk/xyjj.htm",
            "/xygk/ldjs.htm",
            "/info/1055/3902.htm",
        ],
    ),
    "jrsx": (
        "https://jrsx.gduf.edu.cn/",
        [
            "/index/tzgg.htm",
            "/index/xwxx.htm",
            "/szdw/jsml.htm",
            "/szdw/ssds.htm",
            "/szdw/msfc.htm",
            "/szdw/szgk.htm",
            "/xygk1/xyjj.htm",
            "/xygk1/xyld.htm",
            "/info/1055/3611.htm",
        ],
    ),
}

OUT = Path(__file__).parent / "probed"


def dump(name: str, base: str, path: str, client: httpx.Client) -> None:
    url = base + path.lstrip("/")
    try:
        response = client.get(url)
    except Exception as exc:
        print(f"--- {name} {path} ERROR {type(exc).__name__}: {exc}")
        return
    safe = path.strip("/").replace("/", "_") or "index"
    (OUT / f"{name}_{safe}.html").write_text(response.text, encoding="utf-8")
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("li[id^='line_']")
    page_marker = re.search(r"共\s*\d+\s*条\s*\d+\s*/\s*\d+", response.text)
    print(
        f"--- {name} {path} status={response.status_code} "
        f"rows={len(rows)} page_marker={page_marker.group(0) if page_marker else None} "
        f"vsb_body={len(soup.select('[id^=vsb_content]'))}"
    )
    if rows:
        snippet = str(rows[0])
        print("    ROW0:", snippet[:600].replace("\n", " "))
    elif soup.select("[id^='vsb_content']"):
        body = soup.select("[id^='vsb_content']")[0]
        print("    BODY:", body.decode_contents()[:400].replace("\n", " "))


def main() -> None:
    client = httpx.Client(
        timeout=20.0,
        follow_redirects=True,
        headers={"User-Agent": "gduf-web-api/0.3.0 (+https://pypi.org/project/gduf-web-api/)"},
    )
    for name, (base, paths) in SITES.items():
        for path in paths:
            dump(name, base, path, client)
    client.close()


if __name__ == "__main__":
    main()
