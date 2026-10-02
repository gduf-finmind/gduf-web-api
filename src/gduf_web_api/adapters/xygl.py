"""Adapter for the School of Credit Management site (xygl.gduf.edu.cn)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from gduf_web_api.adapters.vsb import (
    VsbAdapter,
    _clean_text,
    _parse_date,
    people_xygl_card,
    row_xygl,
)

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://xygl.gduf.edu.cn/"
HOST = "xygl.gduf.edu.cn"


class XyglAdapter(VsbAdapter):
    """Parse the credit management school templates."""

    code = "xygl"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={
                "zxzx": "index/zxzx.htm",
                "kydt": "xsky/kydt.htm",
                "msfc": "index/msfc.htm",
            },
            article_row_parser=row_xygl,
            people_paths={"zrjs": "szdw/zrjs.htm"},
            people_row_parser=people_xygl_card,
            content_paths={
                "xyjj": "xygk/xyjj.htm",
                "szgk": "szdw/szgk.htm",
                "xrld": "xygk/xrld.htm",
            },
        )

    # -- content title / meta ------------------------------------------------

    def _resolve_title(self, soup: BeautifulSoup, body: Tag) -> str | None:
        # Detail pages (.con_con) put the article title in the first h2; the
        # following h3 renders the date and must not win the heading lookup.
        if soup.select_one(".con_con") is not None:
            node = soup.find("h2")
            if isinstance(node, Tag):
                text = _clean_text(node.get_text(" ", strip=True))
                if text:
                    return text
        return super()._resolve_title(soup, body)

    def _parse_meta(
        self, soup: BeautifulSoup, page_url: str
    ) -> tuple[date | None, str | None, int | None, str | None, str | None]:
        published_at: date | None = None
        if soup.select_one(".con_con") is not None:
            for heading in soup.find_all("h3"):
                published_at = _parse_date(heading.get_text(" ", strip=True))
                if published_at is not None:
                    break
        return published_at, None, None, None, None
