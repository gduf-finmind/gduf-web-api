"""Adapter for the School of Finance and New Media site (cjcm.gduf.edu.cn)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from gduf_web_api.adapters.vsb import (
    VsbAdapter,
    _absolute,
    _clean_text,
    people_cjcm_photo,
    row_trailing_date,
)

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://cjcm.gduf.edu.cn/"
HOST = "cjcm.gduf.edu.cn"


class CjcmAdapter(VsbAdapter):
    """Parse the finance and new media school templates."""

    code = "cjcm"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={
                "xyxw": "xyxw.htm",
                "tzgg": "tzgg.htm",
                "jxdt": "jxgz/jxdt.htm",
                "kydt": "xsky/kydt.htm",
                "xykj": "xykj.htm",
            },
            article_row_parser=row_trailing_date,
            people_paths={"wlyxmtx": "szdw/wlyxmtx.htm"},
            people_row_parser=people_cjcm_photo,
            content_paths={
                "xyjj": "xygk/xyjj.htm",
                "szgk": "szdw/szgk.htm",
                "xrld": "xygk/xrld.htm",
            },
        )

    # -- content title / meta / attachments ----------------------------------

    def _resolve_title(self, soup: BeautifulSoup, body: Tag) -> str | None:
        node = soup.select_one("h1.c-title")
        if isinstance(node, Tag):
            text = _clean_text(node.get_text(" ", strip=True))
            if text:
                return text
        return super()._resolve_title(soup, body)

    def _parse_meta(
        self, soup: BeautifulSoup, page_url: str
    ) -> tuple[date | None, str | None, int | None, str | None, str | None]:
        previous_url: str | None = None
        next_url: str | None = None
        nav = soup.select_one(".i-sxt")
        if nav is not None:
            for para in nav.find_all("p"):
                label = _clean_text(para.get_text(" ", strip=True)) or ""
                anchor = para.find("a", href=True)
                if not isinstance(anchor, Tag):
                    continue
                link = _absolute(page_url, str(anchor.get("href")))
                if not link:
                    continue
                if label.startswith("上一篇"):
                    previous_url = link
                elif label.startswith("下一篇"):
                    next_url = link
        return None, None, None, previous_url, next_url

    def _extra_attachments(self, soup: BeautifulSoup, page_url: str) -> tuple[str, ...]:
        # the attachment block links through a download.jsp endpoint without a
        # file extension, so generic link scanning cannot recognize it
        found: list[str] = []
        for anchor in soup.select(".wz_fj a[href]"):
            link = _absolute(page_url, str(anchor.get("href")))
            if link and link not in found:
                found.append(link)
        return tuple(found)
