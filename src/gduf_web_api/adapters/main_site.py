"""Adapter for the GDUF main university website (www.gduf.edu.cn)."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from gduf_web_api.adapters.vsb import (
    VsbAdapter,
    _absolute,
    _clean_text,
    _parse_date,
    row_date_first,
)
from gduf_web_api.errors import ParseError
from gduf_web_api.models import ArticleSummary, HomeSection, PersonSummary, SiteHome

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://www.gduf.edu.cn/"
HOST = "www.gduf.edu.cn"

#: the three k-ib boxes on the home page, in document order
HOME_BOX_CATEGORIES = ("xshd", "mtgj", "ybxw")

_BREADCRUMB_SPLIT_RE = re.compile(r">\s*|\s*&gt;\s*")
#: spacing used purely for layout inside names/role labels (e.g. 黄　琼, 院　　长)
_LAYOUT_SPACE_RE = re.compile(r"[\u3000\u00a0\u200b]+")


def _home_k_ili(row: Tag, page_url: str, category: str | None) -> ArticleSummary | None:
    """``div.k-ili`` home cards: ``.wz h1 a`` title + ``.wz h2`` date."""

    wz = row.select_one(".wz")
    if wz is None:
        return None
    anchor = wz.select_one("h1 a[href]")
    if not isinstance(anchor, Tag):
        return None
    item_url = _absolute(page_url, str(anchor.get("href")))
    title = _clean_text(str(anchor.get("title") or anchor.get_text(" ", strip=True)))
    if not item_url or not title:
        return None
    date_node = wz.find("h2")
    return ArticleSummary(
        title=title,
        url=item_url,
        published_at=_parse_date(date_node.get_text(" ", strip=True) if date_node else None),
        category=category,
    )


def _home_k_igg(row: Tag, page_url: str, category: str | None) -> ArticleSummary | None:
    """k-igg home rows: ``<li><a title>title</a><b>date</b></li>``."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag) or not str(anchor.get("href", "")).strip():
        return None
    if str(anchor.get("href")).startswith("javascript:"):
        return None
    item_url = _absolute(page_url, str(anchor.get("href")))
    title = _clean_text(str(anchor.get("title") or anchor.get_text(" ", strip=True)))
    if not item_url or not title:
        return None
    date_node = row.find("b")
    return ArticleSummary(
        title=title,
        url=item_url,
        published_at=_parse_date(date_node.get_text(" ", strip=True) if date_node else None),
        category=category,
    )


def _leader_row(row: Tag, page_url: str) -> PersonSummary | None:
    """Leaders page rows inside ``ul.list1``; the role label sits on the
    wrapping list item of the group."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    url = _absolute(page_url, str(anchor.get("href")))
    raw_name = str(anchor.get("title") or anchor.get_text(" ", strip=True))
    name = _clean_text(_LAYOUT_SPACE_RE.sub("", raw_name))
    if not url or not name:
        return None
    role = None
    group = row.find_parent("ul")
    if group is not None:
        parent_item = group.find_parent("li")
        if parent_item is not None:
            label = parent_item.find("span")
            label_text = (
                _clean_text(_LAYOUT_SPACE_RE.sub("", label.get_text(" ", strip=True)))
                if label
                else None
            )
            if label_text:
                role = label_text.rstrip("\uff1a:").strip()
    return PersonSummary(name=name, url=url, role=role)


class MainSiteAdapter(VsbAdapter):
    """Parse the main university website templates."""

    code = "main"
    people_row_selector = ".k-xrld ul.list1 > li"
    search_row_selector = "ul.uslist li"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={
                "gjyw": "index/gjyw.htm",
                "tzgg": "index/gjgg1.htm",
                "xshd": "index/xshd.htm",
                "mtgj": "index/mtgj.htm",
                "ybxw": "index/ybxw.htm",
            },
            article_row_parser=row_date_first,
            people_paths={"xrld": "xygk/xrld.htm"},
            people_row_parser=_leader_row,
            content_paths={
                "gjjj": "xygk/gjjj.htm",
                "gjyg": "xygk/gjyg.htm",
                "gjbs": "xygk/gjbs.htm",
                "gjjs": "xygk/gjjs.htm",
                "bxln": "xygk/bxln.htm",
                "jgsz": "xygk/jgsz.htm",
            },
        )

    # -- content title / meta ------------------------------------------------

    def _find_body(self, soup: BeautifulSoup) -> Tag | None:
        """从学校官网页面定位正文。返回文章容器或机构设置专用列表。

        机构设置不是 VSB 文章页。没有 vsb_content 标记。仅接受主内容区内的
        k-jgsz 列表。避免把侧栏导航、页脚或未知模板当作正文。
        """
        body = super()._find_body(soup)
        if body is not None:
            return body
        return soup.select_one(".k-main-r .k-main-nr .k-jgsz")

    @staticmethod
    def _detail_title(soup: BeautifulSoup) -> str | None:
        node = soup.select_one("div.title")
        if node is None:
            return None
        clone = BeautifulSoup(str(node), "html.parser")
        # The title text lives inside a <form> wrapper, so only drop
        # script/style/noscript here - never the form itself.
        for tag in clone.select("script, style, noscript"):
            tag.decompose()
        return _clean_text(clone.get_text(" ", strip=True))

    @staticmethod
    def _breadcrumb_title(soup: BeautifulSoup) -> str | None:
        block = soup.select_one(".k-main-bt")
        if block is None:
            return None
        # Static pages render the column name in .k-main-bt > h1.
        heading = block.find("h1")
        if isinstance(heading, Tag):
            text = _clean_text(heading.get_text(" ", strip=True))
            if text:
                return text
        node = block.find("h2")
        if node is None:
            return None
        parts = [
            part.strip()
            for part in _BREADCRUMB_SPLIT_RE.split(node.get_text(" ", strip=True))
            if part.strip()
        ]
        if parts and parts[-1] == "正文":
            parts = parts[:-1]
        return parts[-1] if parts else None

    def _resolve_title(self, soup: BeautifulSoup, body: Tag) -> str | None:
        detail_title = self._detail_title(soup)
        if detail_title:
            return detail_title
        return self._breadcrumb_title(soup) or super()._resolve_title(soup, body)

    # -- home ----------------------------------------------------------------

    def get_home(self) -> SiteHome:
        soup, page_url = self._fetch(self._base_url)
        sections: list[HomeSection] = []
        iyw = soup.select_one("div.k-iyw")
        if iyw is not None:
            section = self._home_section(
                iyw,
                page_url,
                category="gjyw",
                title="广金要闻",
                row_parser=_home_k_ili,
                selector="div.k-ili",
            )
            if section is not None:
                sections.append(section)
        igg = soup.select_one("div.k-igg")
        if igg is not None:
            section = self._home_section(
                igg,
                page_url,
                category="tzgg",
                title="广金公告",
                row_parser=_home_k_igg,
                selector="ul > li",
            )
            if section is not None:
                sections.append(section)
        for category, box in zip(HOME_BOX_CATEGORIES, soup.select("div.k-ib-li"), strict=False):
            heading = box.select_one(".k-ibt h1")
            title = _clean_text(heading.get_text(" ", strip=True)) if heading else category
            section = self._home_section(
                box,
                page_url,
                category=category,
                title=title or category,
                row_parser=_home_k_ili,
                selector="div.k-ili",
            )
            if section is not None:
                sections.append(section)
        if not sections:
            raise ParseError("no home sections found on the main site home page")
        return SiteHome(tuple(sections), page_url, source=self.code)

    # search: the result rows share the ul.uslist li template of the list
    # pages, so the base VsbAdapter.search() applies row_date_first directly.
