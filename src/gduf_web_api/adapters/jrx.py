"""Adapter for the School of Finance and Investment site (jrx.gduf.edu.cn)."""

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
    people_jrx_img,
    row_jrx,
)

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://jrx.gduf.edu.cn/"
HOST = "jrx.gduf.edu.cn"

_SOURCE_LABEL_RE = re.compile(r"^信息来源[\uFF1A:]\s*")


class JrxAdapter(VsbAdapter):
    """Parse the finance and investment college templates."""

    code = "jrx"
    #: search hits reuse the list row markup inside a plain text list
    search_row_selector = "div.text-list li"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={"xwgg": "xwgg.htm"},
            article_row_parser=row_jrx,
            people_paths={"zrjs": "szdw/zrjs.htm", "jfry": "szdw/jfry.htm"},
            people_row_parser=people_jrx_img,
            content_paths={
                "xyjj": "xygk/xyjj.htm",
                "jgsz": "xygk/jgsz.htm",
                "kydt": "kydt/kydt.htm",
                "bsfc": "szdw/bsfc.htm",
                "xyld": "xygk/xyld.htm",
            },
        )

    # -- content title / meta ------------------------------------------------

    def _resolve_title(self, soup: BeautifulSoup, body: Tag) -> str | None:
        # Article and most static pages carry the page title in .art-tit h3;
        # a few column pages (e.g. szgk) only render it beside the breadcrumb.
        for selector in (".art-tit h3", ".position h2"):
            node = soup.select_one(selector)
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
        meta = soup.select_one(".art-tit p")
        if meta is not None:
            for span in meta.find_all("span"):
                text = _clean_text(span.get_text(" ", strip=True)) or ""
                if text.startswith("发布日期"):
                    published_at = _parse_date(text)
                elif text.startswith("信息来源"):
                    attribution = _clean_text(_SOURCE_LABEL_RE.sub("", text))
        previous_url: str | None = None
        next_url: str | None = None
        nav = soup.select_one(".pnext")
        if nav is not None:
            for para in nav.find_all("p"):
                label = _clean_text(para.get_text(" ", strip=True)) or ""
                anchor = para.find("a", href=True)
                if not isinstance(anchor, Tag):
                    continue
                link = _absolute(page_url, str(anchor.get("href")))
                if not link:
                    continue
                if label.startswith("上一条"):
                    previous_url = link
                elif label.startswith("下一条"):
                    next_url = link
        return published_at, attribution, None, previous_url, next_url
