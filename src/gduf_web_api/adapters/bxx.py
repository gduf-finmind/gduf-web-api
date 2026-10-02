"""Adapter for the School of Insurance site (bxx.gduf.edu.cn)."""

from __future__ import annotations

import re
from datetime import date
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from gduf_web_api.adapters.vsb import (
    VsbAdapter,
    _clean_text,
    _parse_date,
    people_bxx_name,
    row_title_only,
)

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://bxx.gduf.edu.cn/"
HOST = "bxx.gduf.edu.cn"

_TIME_RE = re.compile(r"时间[\uFF1A:]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})")
_SOURCE_RE = re.compile(r"来源[\uFF1A:]\s*(.*?)(?=\s*(?:时间|作者|点击|发布日期)[\uFF1A:]|$)")


class BxxAdapter(VsbAdapter):
    """Parse the insurance school templates (title-only list rows)."""

    code = "bxx"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={
                "xwgg": "xwgg.htm",
                "kydt": "kxyj/kydt.htm",
                "xsjl": "kxyj/xsjl.htm",
            },
            article_row_parser=row_title_only,
            people_paths={
                "xrld": "xygk1/xrld.htm",
                "js": "szdw/jsml/js.htm",
                "fjs": "szdw/jsml/fjs.htm",
            },
            people_row_parser=people_bxx_name,
            content_paths={
                "xyjj": "xygk1/xyjj.htm",
                "szgk": "szdw/szgk.htm",
            },
        )

    # -- content title / meta ------------------------------------------------

    def _resolve_title(self, soup: BeautifulSoup, body: Tag) -> str | None:
        # Detail pages carry the article title as the first h2 inside .main_info;
        # static column pages fall back to the default nearest-heading lookup.
        info = soup.select_one(".main_info")
        if info is not None:
            h2 = info.find("h2")
            if isinstance(h2, Tag):
                text = _clean_text(h2.get_text(" ", strip=True))
                if text:
                    return text
        return super()._resolve_title(soup, body)

    def _parse_meta(
        self, soup: BeautifulSoup, page_url: str
    ) -> tuple[date | None, str | None, int | None, str | None, str | None]:
        published_at: date | None = None
        attribution: str | None = None
        meta = soup.select_one(".text_time")
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
        return published_at, attribution, None, None, None
