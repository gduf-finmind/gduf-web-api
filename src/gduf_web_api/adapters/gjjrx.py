"""Adapter for the National Finance school site (gjjrx.gduf.edu.cn)."""

from __future__ import annotations

import re
from datetime import date
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from gduf_web_api.adapters.vsb import (
    VsbAdapter,
    _absolute,
    _clean_text,
    _download_attachments,
    _parse_date,
    people_dept_name,
    people_gjjrx_leader,
    people_jrx_img,
    row_gjjrx,
)

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://gjjrx.gduf.edu.cn/"
HOST = "gjjrx.gduf.edu.cn"

_SOURCE_TIME_RE = re.compile(r"文章来源[\uFF1A:]\s*(.*?)\s*发布时间[\uFF1A:]\s*(\d{4}-\d{2}-\d{2})")


class GjjrxAdapter(VsbAdapter):
    """Parse the national finance school templates."""

    code = "gjjrx"
    #: search results reuse the list row markup inside plain list items
    search_row_selector = "li:has(b.fr)"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={
                "xyxw": "xwzx/xyxw.htm",
                "tzgg": "xwzx/tzgg.htm",
                "jxky": "xwzx/jxky.htm",
                "dtxg": "xwzx/dtxg.htm",
                "gjzk": "xwzx/gjzk.htm",
            },
            article_row_parser=row_gjjrx,
            people_paths={
                "xrld": "xygk/xyld.htm",
                "zrjs": "szdw/zrjs.htm",
                "jfry": "szdw/jfry.htm",
                "bsfc": "szdw/bsfc.htm",
                "jsfc": "szdw/jsfc.htm",
            },
            people_row_selector={
                "xrld": "ul.leader_group li",
                "zrjs": "li[id^='line_']",
                "jfry": "li[id^='line_']",
                "bsfc": "li[id^='line_']",
                "jsfc": "li[id^='line_']",
            },
            people_row_parser={
                "xrld": people_gjjrx_leader,
                "zrjs": people_jrx_img,
                "jfry": people_dept_name,
                "bsfc": people_jrx_img,
                "jsfc": people_jrx_img,
            },
            content_paths={
                "xyjj": "xygk/xyjj.htm",
                "jgsz": "xygk/jgsz.htm",
                "szgk": "szdw/szgk.htm",
            },
        )

    # -- content title / meta ------------------------------------------------

    def _resolve_title(self, soup: BeautifulSoup, body: Tag) -> str | None:
        # article detail pages carry the title in the xqnr_tit heading; static
        # column pages carry only the breadcrumb column name
        node = soup.select_one(".xqnr_tit h2")
        if isinstance(node, Tag):
            text = _clean_text(node.get_text(" ", strip=True))
            if text:
                return text
        node = soup.select_one("span.lm.fl")
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
        meta = soup.select_one(".xqnr_tit")
        if meta is not None:
            match = _SOURCE_TIME_RE.search(meta.get_text(" ", strip=True))
            if match:
                attribution = _clean_text(match.group(1))
                published_at = _parse_date(match.group(2))
        previous_url: str | None = None
        next_url: str | None = None
        nav = soup.select_one(".sxfy")
        if nav is not None:
            for item in nav.select("li"):
                label = _clean_text(item.get_text(" ", strip=True)) or ""
                anchor = item.find("a", href=True)
                if not isinstance(anchor, Tag) or not label:
                    continue
                link = _absolute(page_url, str(anchor.get("href")))
                if not link:
                    continue
                if label.startswith("上一条"):
                    previous_url = link
                elif label.startswith("下一条"):
                    next_url = link
        return published_at, attribution, None, previous_url, next_url

    def _extra_attachments(self, soup: BeautifulSoup, page_url: str) -> tuple[str, ...]:
        return _download_attachments(soup, page_url)
