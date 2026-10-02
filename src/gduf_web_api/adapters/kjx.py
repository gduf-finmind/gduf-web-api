"""Adapter for the School of Accounting site (kjx.gduf.edu.cn)."""

from __future__ import annotations

import re
from datetime import date
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from gduf_web_api.adapters.vsb import (
    VsbAdapter,
    _absolute,
    _clean_text,
    _parse_date,
    people_kjx_card,
    row_kjx,
)

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://kjx.gduf.edu.cn/"
HOST = "kjx.gduf.edu.cn"

_TIME_RE = re.compile(r"时间[\uFF1A:]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})")
_SOURCE_RE = re.compile(r"来源[\uFF1A:]\s*(\S.*)$")


class KjxAdapter(VsbAdapter):
    """Parse the accounting school templates."""

    code = "kjx"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={
                "xxgg": "index/xxgg.htm",
                "dthd": "dtjs/dthd.htm",
                "jxgl": "zyjx/jxgl.htm",
                "kydt": "kxyj/kydt.htm",
            },
            article_row_parser=row_kjx,
            people_paths={
                "js": "szdw/js.htm",
                "fjs": "szdw/fjs.htm",
                "xzry": "szdw/xzry.htm",
            },
            people_row_parser=people_kjx_card,
            content_paths={
                "xyjj": "yxgk/xyjj.htm",
                "szgk": "szdw/szgk.htm",
                "xrld": "yxgk/xrld.htm",
            },
        )

    # -- content title / meta ------------------------------------------------

    def _resolve_title(self, soup: BeautifulSoup, body: Tag) -> str | None:
        node = soup.select_one(".main_contit h2")
        if isinstance(node, Tag):
            text = _clean_text(node.get_text(" ", strip=True))
            if text:
                return text
        return super()._resolve_title(soup, body)

    def _parse_meta(
        self, soup: BeautifulSoup, page_url: str
    ) -> tuple[date | None, str | None, int | None, str | None, str | None]:
        published_at: date | None = None
        attribution: str | None = None
        meta = soup.select_one(".main_contit p")
        if meta is not None:
            fragment = BeautifulSoup(str(meta), "html.parser")
            for junk in fragment.select("script, style, noscript"):
                junk.decompose()
            text = _clean_text(fragment.get_text(" ", strip=True)) or ""
            time_match = _TIME_RE.search(text)
            if time_match:
                published_at = _parse_date(time_match.group(1))
            source_match = _SOURCE_RE.search(text)
            if source_match:
                attribution = _clean_text(source_match.group(1))
        previous_url: str | None = None
        next_url: str | None = None
        nav = soup.select_one(".main_art")
        if nav is not None:
            for entry in nav.find_all("li"):
                label = _clean_text(entry.get_text(" ", strip=True)) or ""
                anchor = entry.find("a", href=True)
                if not isinstance(anchor, Tag):
                    continue
                link = _absolute(page_url, str(anchor.get("href")))
                if not link:
                    continue
                if label.startswith("上一篇"):
                    previous_url = link
                elif label.startswith("下一篇"):
                    next_url = link
        return published_at, attribution, None, previous_url, next_url
