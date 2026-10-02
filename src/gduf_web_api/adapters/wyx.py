"""Adapter for the School of Foreign Languages and Culture site (wyx.gduf.edu.cn)."""

from __future__ import annotations

import re
from datetime import date
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from gduf_web_api.adapters.vsb import (
    VsbAdapter,
    _clean_text,
    _parse_date,
    people_wyx_card,
    row_trailing_date,
)

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://wyx.gduf.edu.cn/"
HOST = "wyx.gduf.edu.cn"

_PUBLISHED_RE = re.compile(r"发布时间[\uFF1A:]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})")
_CRUMB_SEP = re.compile(r"\s*>>\s*")


class WyxAdapter(VsbAdapter):
    """Parse the foreign languages and culture school templates."""

    code = "wyx"
    #: teacher cards sit in plain list-images divs, not numbered list items
    people_row_selector = "div.list-images"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={
                "tzgg": "tzgg.htm",
                "xyxw": "xyxw.htm",
                "djdt": "dqgz/djdt.htm",
                "kydt": "xsky/kydt.htm",
                "xgdt": "xszc/xgdt.htm",
            },
            article_row_parser=row_trailing_date,
            people_paths={"js": "szll/js.htm", "fjs": "szll/fjs.htm"},
            people_row_parser=people_wyx_card,
            content_paths={
                "xyjj": "xygk/xyjj.htm",
                "szgk": "szll/dwgk.htm",
                "xrld": "xygk/xrld.htm",
            },
        )

    # -- content title / meta ------------------------------------------------

    def _resolve_title(self, soup: BeautifulSoup, body: Tag) -> str | None:
        node = soup.select_one(".kuaiXun-con .title h3")
        if isinstance(node, Tag):
            text = _clean_text(node.get_text(" ", strip=True))
            if text:
                return text
        # static column pages carry no heading; the title repeats as the last
        # segment of the breadcrumb block (div.biaoTi)
        crumb = soup.select_one("div.biaoTi")
        if crumb is not None:
            text = _clean_text(crumb.get_text(" ", strip=True)) or ""
            parts = [seg for seg in (_clean_text(p) for p in _CRUMB_SEP.split(text)) if seg]
            if parts:
                title = parts[-1]
                if "当前位置" in title:
                    title = _clean_text(title.split("当前位置", 1)[0]) or title
                return title
        return super()._resolve_title(soup, body)

    def _parse_meta(
        self, soup: BeautifulSoup, page_url: str
    ) -> tuple[date | None, str | None, int | None, str | None, str | None]:
        published_at: date | None = None
        scope = soup.select_one(".kuaiXun-con .title")
        if scope is not None:
            text = _clean_text(scope.get_text(" ", strip=True)) or ""
            match = _PUBLISHED_RE.search(text)
            if match:
                published_at = _parse_date(match.group(1))
        return published_at, None, None, None, None
