"""Shared adapter for Visual SiteBuilder (VS Builder) based college sites.

Most GDUF college sub-sites run the same "Visual SiteBuilder" CMS with a
common set of conventions that this base class implements:

- list pages render rows as ``li[id^='line_']`` items (a few people pages
  use a different container, configurable per site);
- pagination shows ``共 N 条&nbsp;&nbsp;P/T`` and page ``k`` is served at
  ``{path}/{T-k+1}.htm``;
- article/profile/static bodies live in ``div[id^='vsb_content']``;
- search (where present) is the lucene ``search.jsp`` endpoint with a
  base64-encoded keyword, page one via POST and later pages via GET with
  ``currentnum``/``newskeycode2``.

Row markup differs per site, so each concrete adapter selects one of the
row parsers below (or supplies its own).
"""

from __future__ import annotations

import base64
import re
from collections.abc import Callable, Mapping
from datetime import date
from typing import TYPE_CHECKING
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from gduf_web_api.errors import InvalidPageError, ParseError
from gduf_web_api.models import (
    ArticleSummary,
    ContentDetail,
    HomeSection,
    PageResult,
    PersonSummary,
    SiteHome,
)

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

RowParser = Callable[[Tag, str, str | None], ArticleSummary | None]
PeopleRowParser = Callable[[Tag, str], PersonSummary | None]

_PAGE_RE = re.compile(r"共\s*(\d+)\s*条\s*(\d+)\s*/\s*(\d+)")
_SEARCH_PAGE_RE = re.compile(r"共有\s*(\d+)\s*条.*?共有\s*(\d+)\s*页.*?当前第\s*(\d+)\s*页")
_DATE_RE = re.compile(r"(20\d{2})[-年/.](\d{1,2})[-月/.](\d{1,2})")
_MD_RE = re.compile(r"^(\d{1,2})[-/.](\d{1,2})$")
_ATTACHMENT_RE = re.compile(
    r"\.(?:pdf|docx?|xlsx?|pptx?|zip|rar|7z|txt|csv)(?:$|[?#])", re.IGNORECASE
)

_EN_MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def _validate_page(page: int) -> None:
    if isinstance(page, bool) or not isinstance(page, int) or page < 1:
        raise InvalidPageError("page must be a positive integer")


_ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\ufeff]")


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(_ZERO_WIDTH_RE.sub("", value).split())
    return cleaned or None


#: spacing used purely for layout inside names (e.g. 黄　琼, 韦　筱)
_LAYOUT_SPACE_RE = re.compile(r"[\u3000\u00a0\u200b]+")


def _clean_name(value: str | None) -> str | None:
    """Clean a person name, dropping spacing that is only used for layout."""

    if value is None:
        return None
    return _clean_text(_LAYOUT_SPACE_RE.sub("", value))


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    match = _DATE_RE.search(value)
    if not match:
        return None
    try:
        return date(*(int(part) for part in match.groups()))
    except ValueError:
        return None


def _parse_day_month(day: str | None, month: str | None) -> date | None:
    """Build a date from a day number and an English month name (no year)."""

    if not day or not month:
        return None
    month_num = _EN_MONTHS.get(month.strip().lower()[:3])
    if month_num is None:
        return None
    try:
        return date(2026, month_num, int(day))  # year is unknown; see _row_xygl
    except ValueError:
        return None


def _absolute(page_url: str, value: str | None) -> str | None:
    if not value or value.lower().startswith(("javascript:", "data:")):
        return None
    return urljoin(page_url, value)


def _dedupe_articles(items: list[ArticleSummary]) -> tuple[ArticleSummary, ...]:
    found: dict[str, ArticleSummary] = {}
    for item in items:
        found.setdefault(item.url, item)
    return tuple(found.values())


def _split_name_role(display_name: str) -> tuple[str, str | None]:
    """Split "职务 姓名" (or "姓名") on the last whitespace run."""

    parts = re.split(r"\s+", display_name.strip())
    if len(parts) <= 1:
        return display_name.strip(), None
    return parts[-1], " ".join(parts[:-1])


def _split_person_title(display_name: str) -> tuple[str, str | None]:
    parenthesized = re.fullmatch(
        r"\s*(.+?)\s*[\uff08(]\s*(.+?)\s*[\uff09)]\s*", display_name
    )
    if parenthesized:
        return parenthesized.group(1).strip(), parenthesized.group(2).strip()
    return _split_name_role(display_name)


# ---------------------------------------------------------------------------
# Article row parsers, one per observed list template.
# ---------------------------------------------------------------------------


def row_date_first(row: Tag, page_url: str, category: str | None) -> ArticleSummary | None:
    """``<li><span>2026.09.30</span><a href title>`` (main site lists)."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    item_url = _absolute(page_url, str(anchor.get("href")))
    title = _clean_text(str(anchor.get("title") or anchor.get_text(" ", strip=True)))
    if not item_url or not title:
        return None
    date_span = row.find("span")
    return ArticleSummary(
        title=title,
        url=item_url,
        published_at=_parse_date(date_span.get_text(" ", strip=True) if date_span else None),
        category=category,
    )


def row_jrx(row: Tag, page_url: str, category: str | None) -> ArticleSummary | None:
    """``<li><a><div.text-ldata><p>MM/DD</p><span>YYYY</span></div><div.text-linfo><h3/><p/></div></a></li>``."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    item_url = _absolute(page_url, str(anchor.get("href")))
    info = anchor.select_one(".text-linfo")
    title_node = info.find("h3") if info else None
    title = _clean_text(
        str(anchor.get("title") or (title_node.get_text(" ", strip=True) if title_node else ""))
    )
    if not item_url or not title:
        return None
    published_at = None
    data = anchor.select_one(".text-ldata")
    if data:
        p = data.find("p")
        year_node = data.find("span")
        day_text = p.get_text(" ", strip=True) if p else ""
        year_text = year_node.get_text(" ", strip=True) if year_node else ""
        day_match = _MD_RE.match(day_text)
        if day_match:
            try:
                published_at = date(
                    int(year_text), int(day_match.group(1)), int(day_match.group(2))
                )
            except (TypeError, ValueError):
                published_at = None
    summary_node = info.find("p") if info else None
    return ArticleSummary(
        title=title,
        url=item_url,
        published_at=published_at,
        summary=_clean_text(summary_node.get_text(" ", strip=True)) if summary_node else None,
        category=category,
    )


def row_kjx(row: Tag, page_url: str, category: str | None) -> ArticleSummary | None:
    """``<li><a><span>2026-06-16</span><em>title</em></a></li>``."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    item_url = _absolute(page_url, str(anchor.get("href")))
    em = anchor.find("em")
    title = _clean_text(em.get_text(" ", strip=True) if em else anchor.get_text(" ", strip=True))
    if not item_url or not title:
        return None
    date_span = anchor.find("span")
    return ArticleSummary(
        title=title,
        url=item_url,
        published_at=_parse_date(date_span.get_text(" ", strip=True) if date_span else None),
        category=category,
    )


def row_title_only(row: Tag, page_url: str, category: str | None) -> ArticleSummary | None:
    """``<li><a href title>title</a></li>`` (no date rendered, bxx lists)."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    item_url = _absolute(page_url, str(anchor.get("href")))
    title = _clean_text(str(anchor.get("title") or anchor.get_text(" ", strip=True)))
    if not item_url or not title:
        return None
    return ArticleSummary(title=title, url=item_url, category=category)


def row_xygl(row: Tag, page_url: str, category: str | None) -> ArticleSummary | None:
    """``<li><div.list_time><p.day/><p.month>|<img></div><div.list_wen><a.tit/><p/></div></li>``."""

    wen = row.select_one(".list_wen")
    if wen is None:
        return None
    anchor = wen.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    item_url = _absolute(page_url, str(anchor.get("href")))
    title = _clean_text(anchor.get_text(" ", strip=True))
    if not item_url or not title:
        return None
    # The template renders "day + English month" without a year (e.g. "26 May");
    # the year is ambiguous, so published_at stays None. _parse_day_month
    # documents and validates the date shape.
    published_at = None
    time_box = row.select_one(".list_time")
    if time_box is not None:
        day = time_box.select_one("p.day")
        month = time_box.select_one("p.month")
        if day is not None and month is not None:
            _parse_day_month(day.get_text(strip=True), month.get_text(strip=True))
    summary_node = wen.find("p")
    summary = _clean_text(summary_node.get_text(" ", strip=True)) if summary_node else None
    if summary:
        summary = re.sub(r"\[\s*详细\s*\]\s*$", "", summary) or None
    return ArticleSummary(
        title=title, url=item_url, published_at=published_at, summary=summary, category=category
    )


def row_trailing_date(row: Tag, page_url: str, category: str | None) -> ArticleSummary | None:
    """``<li><a href [title]>title</a><span>date</span></li>`` (wyx, cjcm lists;
    some cjcm links point at external articles)."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    item_url = _absolute(page_url, str(anchor.get("href")))
    title = _clean_text(str(anchor.get("title") or anchor.get_text(" ", strip=True)))
    if not item_url or not title:
        return None
    date_span = row.find("span")
    return ArticleSummary(
        title=title,
        url=item_url,
        published_at=_parse_date(date_span.get_text(" ", strip=True) if date_span else None),
        category=category,
    )


def row_gjjrx(row: Tag, page_url: str, category: str | None) -> ArticleSummary | None:
    """``<li><b class="fr">date</b><a href [title]>title</a></li>`` (gjjrx lists
    and search results)."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
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


def row_jmx(row: Tag, page_url: str, category: str | None) -> ArticleSummary | None:
    """``<li><span>date</span><a href><em>title</em></a></li>`` (jmx lists)."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    item_url = _absolute(page_url, str(anchor.get("href")))
    em = anchor.find("em")
    title = _clean_text(em.get_text(" ", strip=True) if em else anchor.get_text(" ", strip=True))
    if not item_url or not title:
        return None
    date_span = row.find("span")
    return ArticleSummary(
        title=title,
        url=item_url,
        published_at=_parse_date(date_span.get_text(" ", strip=True) if date_span else None),
        category=category,
    )


# ---------------------------------------------------------------------------
# People row parsers.
# ---------------------------------------------------------------------------


def people_jrx_img(row: Tag, page_url: str) -> PersonSummary | None:
    """``<li><a title=name><div.pic><img/></div><div.info><p>name</p></div></a></li>``."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    url = _absolute(page_url, str(anchor.get("href")))
    info = anchor.select_one(".info")
    name = _clean_name(info.get_text(" ", strip=True) if info else str(anchor.get("title") or ""))
    if not url or not name:
        return None
    image = anchor.select_one(".pic img")
    return PersonSummary(
        name=name,
        url=url,
        image_url=_absolute(page_url, str(image.get("src"))) if isinstance(image, Tag) else None,
    )


def people_kjx_card(row: Tag, page_url: str) -> PersonSummary | None:
    """kjx teacher cards: photo + ``h3`` name + 职位/个人简介 text + 详细 link."""

    right = row.select_one(".main_rpicR")
    if right is None:
        return None
    h3 = right.find("h3")
    name = _clean_name(h3.get_text(" ", strip=True)) if h3 else None
    if not name:
        return None
    detail_link = next(
        (
            a
            for a in right.find_all("a", href=True)
            if _clean_text(a.get_text(" ", strip=True)) == "详细"
        ),
        None,
    )
    if not isinstance(detail_link, Tag):
        return None
    url = _absolute(page_url, str(detail_link.get("href")))
    if not url:
        return None
    info_para = right.find("p")
    text = _clean_text(info_para.get_text(" ", strip=True)) if info_para is not None else ""
    role = None
    summary = None
    role_match = re.search(
        r"(?:职位|职称)[\uFF1A:]\s*(.+?)(?:个人简介[\uFF1A:]|部门[\uFF1A:]|\s*\[|$)", text or ""
    )
    if role_match:
        role = _clean_text(role_match.group(1))
    summary_match = re.search(r"个人简介[\uFF1A:]\s*(.+?)(?:\s*\[|$)", text or "")
    if summary_match:
        summary = _clean_text(summary_match.group(1))
    left = row.select_one(".main_rpicL")
    image = left.find("img") if left else row.find("img")
    return PersonSummary(
        name=name,
        url=url,
        role=role,
        responsibility=summary,
        image_url=_absolute(page_url, str(image.get("src"))) if isinstance(image, Tag) else None,
    )


def people_xxgc_card(row: Tag, page_url: str) -> PersonSummary | None:
    """xxgc teacher cards: photo + ``h3`` name + 教师简介 bio + 详细 link."""

    right = row.select_one(".main_rpicR")
    if right is None:
        return None
    h3 = right.find("h3")
    name = _clean_name(h3.get_text(" ", strip=True)) if h3 else None
    if not name:
        return None
    detail_link = next(
        (
            a
            for a in right.find_all("a", href=True)
            if _clean_text(a.get_text(" ", strip=True)) == "详细"
        ),
        None,
    )
    if not isinstance(detail_link, Tag):
        return None
    url = _absolute(page_url, str(detail_link.get("href")))
    if not url:
        return None
    bio_para = right.find("p")
    summary = _clean_text(bio_para.get_text(" ", strip=True)) if bio_para is not None else None
    if summary:
        summary = re.sub(r"^教师简介", "", summary)
        summary = re.sub(r"\s*\[\s*详细\s*\]\s*$", "", summary) or None
    left = row.select_one(".main_rpicL")
    image = left.find("img") if left else row.find("img")
    return PersonSummary(
        name=name,
        url=url,
        responsibility=summary,
        image_url=_absolute(page_url, str(image.get("src"))) if isinstance(image, Tag) else None,
    )


def people_bxx_name(row: Tag, page_url: str) -> PersonSummary | None:
    """``<li><a title="姓名 职务">姓名 职务</a></li>``; role optional."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    url = _absolute(page_url, str(anchor.get("href")))
    display_name = _clean_text(str(anchor.get("title") or anchor.get_text(" ", strip=True)))
    if not url or not display_name:
        return None
    name, role = _split_name_role(display_name)
    return PersonSummary(name=name, url=url, role=role)


def people_xygl_card(row: Tag, page_url: str) -> PersonSummary | None:
    """xygl teacher cards: photo + name link + bio paragraph."""

    wen = row.select_one(".list_wen")
    if wen is None:
        return None
    anchor = wen.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    url = _absolute(page_url, str(anchor.get("href")))
    name = _clean_text(anchor.get_text(" ", strip=True))
    if not url or not name:
        return None
    summary_node = wen.find("p")
    summary = _clean_text(summary_node.get_text(" ", strip=True)) if summary_node else None
    if summary:
        summary = re.sub(r"\[\s*详细\s*\]\s*$", "", summary) or None
    image = row.select_one(".list_time img")
    return PersonSummary(
        name=name,
        url=url,
        responsibility=summary,
        image_url=_absolute(page_url, str(image.get("src"))) if isinstance(image, Tag) else None,
    )


def people_wyx_card(row: Tag, page_url: str) -> PersonSummary | None:
    """wyx teacher cards (``div.list-images``): photo + name + 职务/称 + interests."""

    left = row.select_one(".list-left")
    content = row.select_one(".list-content")
    if left is None or content is None:
        return None
    anchor = left.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    url = _absolute(page_url, str(anchor.get("href")))
    strong = content.select_one(".list-title strong")
    name = _clean_text(strong.get_text(" ", strip=True)) if strong else None
    if not url or not name:
        return None
    role = None
    for p in content.select(".list-text p"):
        text = p.get_text(" ", strip=True)
        if text.startswith("职务/称") or text.startswith("职务/职称"):
            span = p.find("span")
            role = _clean_text(span.get_text(" ", strip=True) if span else None)
            break
    image = left.find("img")
    return PersonSummary(
        name=name,
        url=url,
        role=role,
        image_url=_absolute(page_url, str(image.get("src"))) if isinstance(image, Tag) else None,
    )


def people_cjcm_photo(row: Tag, page_url: str) -> PersonSummary | None:
    """``<li><a><img alt=name/><span>姓名 职务</span></a></li>`` (cjcm staff rows)."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    url = _absolute(page_url, str(anchor.get("href")))
    if not url:
        return None
    span = anchor.find("span")
    image = anchor.find("img")
    span_text = _clean_text(span.get_text(" ", strip=True)) if span is not None else None
    alt_name = _clean_name(str(image.get("alt") or "")) if isinstance(image, Tag) else None
    name: str | None = None
    role: str | None = None
    if alt_name and span_text and span_text.startswith(alt_name):
        # the span repeats "姓名 职务"; keep only the role tail
        name = alt_name
        role = _clean_text(span_text[len(alt_name) :])
    elif span_text:
        # the span renders "姓名 职务" in that order
        parts = span_text.split(maxsplit=1)
        name = _clean_name(parts[0])
        role = _clean_text(parts[1]) if len(parts) > 1 else None
    elif alt_name:
        name = alt_name
    if not name:
        return None
    return PersonSummary(
        name=name,
        url=url,
        role=role,
        image_url=_absolute(page_url, str(image.get("src"))) if isinstance(image, Tag) else None,
    )


_DEPT_NAME_RE = re.compile(r"^(\S+?)[\u2014\u2013\-]\s*")


def people_dept_name(row: Tag, page_url: str) -> PersonSummary | None:
    """Photo cards whose display text reads "部门—姓名" (gjjrx support staff)."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    url = _absolute(page_url, str(anchor.get("href")))
    info = anchor.select_one(".info")
    display_name = _clean_text(
        info.get_text(" ", strip=True) if info else str(anchor.get("title") or "")
    )
    if not url or not display_name:
        return None
    name = display_name
    role: str | None = None
    split = _DEPT_NAME_RE.match(display_name)
    if split:
        role = split.group(1)
        name = _clean_name(display_name[split.end() :]) or name
    image = anchor.select_one(".pic img")
    return PersonSummary(
        name=name,
        url=url,
        role=role,
        image_url=_absolute(page_url, str(image.get("src"))) if isinstance(image, Tag) else None,
    )


def people_gjjrx_leader(row: Tag, page_url: str) -> PersonSummary | None:
    """gjjrx leader cards: photo link plus a 姓名/职务 two-row table."""

    anchor = row.select_one(".leader_image a[href]")
    if not isinstance(anchor, Tag):
        return None
    url = _absolute(page_url, str(anchor.get("href")))
    if not url:
        return None
    name: str | None = None
    role: str | None = None
    for cell in row.select(".leader_info td"):
        label_node = cell.find("b")
        value_node = cell.find("span")
        label = _clean_text(label_node.get_text(" ", strip=True)) if label_node else ""
        value = (
            _clean_text(value_node.get_text(" ", strip=True))
            if isinstance(value_node, Tag)
            else None
        )
        if not value:
            continue
        if label == "姓名":
            name = _clean_name(value)
        elif label == "职务":
            role = value
    if not name:
        return None
    image = row.select_one(".leader_image img")
    return PersonSummary(
        name=name,
        url=url,
        role=role,
        image_url=_absolute(page_url, str(image.get("src"))) if isinstance(image, Tag) else None,
    )


def _download_attachments(soup: BeautifulSoup, page_url: str) -> tuple[str, ...]:
    """Collect ``download.jsp`` attachment links that carry no file extension."""

    found: list[str] = []
    for anchor in soup.select('a[href*="download.jsp"]'):
        link = _absolute(page_url, str(anchor.get("href")))
        if link and link not in found:
            found.append(link)
    return tuple(found)


def people_em_name(row: Tag, page_url: str) -> PersonSummary | None:
    """``<li><a href><span>date</span><em>姓名</em></a></li>`` (gsgl/jrsx staff lists)."""

    anchor = row.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    url = _absolute(page_url, str(anchor.get("href")))
    em = anchor.find("em")
    name = _clean_name(em.get_text(" ", strip=True) if em else anchor.get_text(" ", strip=True))
    if not url or not name:
        return None
    return PersonSummary(name=name, url=url)


# ---------------------------------------------------------------------------
# Adapter base.
# ---------------------------------------------------------------------------


class VsbAdapter:
    """Base adapter for Visual SiteBuilder college sites."""

    code: str = "vsb"

    #: selector for article list rows
    article_row_selector = "li[id^='line_']"
    #: selector for people list rows (defaults to the article rows); a concrete
    #: adapter may override it per category via the constructor
    people_row_selector = "li[id^='line_']"
    #: search result rows; None disables search
    search_row_selector: str | None = None

    def __init__(
        self,
        client: GdufClient,
        *,
        base_url: str,
        host: str,
        article_paths: dict[str, str],
        article_row_parser: RowParser,
        people_paths: dict[str, str] | None = None,
        people_row_parser: PeopleRowParser | Mapping[str, PeopleRowParser] | None = None,
        people_row_selector: str | Mapping[str, str] | None = None,
        content_paths: dict[str, str] | None = None,
    ) -> None:
        self._client = client
        self._base_url = base_url
        self._host = host
        self._article_paths = article_paths
        self._article_row_parser = article_row_parser
        self._people_paths = people_paths or {}
        self._people_row_parser: PeopleRowParser | Mapping[str, PeopleRowParser] | None = (
            people_row_parser
        )
        self._people_row_selector: str | Mapping[str, str] = (
            people_row_selector if people_row_selector is not None else self.people_row_selector
        )
        self._content_paths = content_paths or {}
        self._page_meta: dict[str, tuple[int, int]] = {}
        self._first_page: dict[str, tuple[BeautifulSoup, str]] = {}

    # -- low-level helpers ---------------------------------------------------

    def _fetch(self, url: str) -> tuple[BeautifulSoup, str]:
        html, response_url = self._client._request_text("GET", url)
        return BeautifulSoup(html, "html.parser"), response_url

    @staticmethod
    def _pagination(soup: BeautifulSoup, item_count: int) -> tuple[int, int, int]:
        match = _PAGE_RE.search(soup.get_text(" ", strip=True))
        if not match:
            return item_count, 1, 1
        total_items, current_page, total_pages = (int(value) for value in match.groups())
        return total_items, current_page, total_pages

    def _paginated_page(
        self, key: str, path: str, page: int
    ) -> tuple[BeautifulSoup, str, int, int]:
        _validate_page(page)
        canonical_url = urljoin(self._base_url, path)
        cached = self._page_meta.get(key)
        if cached is None:
            first_soup, first_url = self._fetch(canonical_url)
            total_items, _, total_pages = self._pagination(first_soup, 0)
            cached = (total_items, total_pages)
            self._page_meta[key] = cached
            self._first_page[key] = (first_soup, first_url)
        total_items, total_pages = cached
        if page > total_pages:
            raise InvalidPageError(
                f"page {page} is outside the available range 1..{total_pages} for {key}"
            )
        if page == 1:
            cached_page = self._first_page.pop(key, None)
            if cached_page is not None:
                return *cached_page, total_items, total_pages
            soup, response_url = self._fetch(canonical_url)
            return soup, response_url, total_items, total_pages
        path_without_suffix = path.removesuffix(".htm")
        suffix = total_pages - page + 1
        page_url = urljoin(self._base_url, f"{path_without_suffix}/{suffix}.htm")
        soup, response_url = self._fetch(page_url)
        return soup, response_url, total_items, total_pages

    # -- list endpoints ------------------------------------------------------

    def get_articles(self, category: str, page: int = 1) -> PageResult[ArticleSummary]:
        try:
            path = self._article_paths[category]
        except KeyError as exc:
            raise ParseError(f"unknown {self.code} article category: {category!r}") from exc
        soup, response_url, cached_total, cached_pages = self._paginated_page(
            f"article:{category}", path, page
        )
        items = [
            item
            for item in (
                self._article_row_parser(row, response_url, category)
                for row in soup.select(self.article_row_selector)
            )
            if item is not None
        ]
        if not items:
            raise ParseError(f"no article items found for {category}")
        total_items, _, total_pages = self._pagination(soup, len(items))
        if total_pages == 1 and cached_pages > 1:
            total_items, total_pages = cached_total, cached_pages
        return PageResult(_dedupe_articles(items), page, total_pages, total_items, response_url)

    def _people_row_config(self, category: str) -> tuple[str, PeopleRowParser | None]:
        """Resolve the row selector and parser for one people category."""

        selector = self._people_row_selector
        parser = self._people_row_parser
        if isinstance(selector, Mapping) and category not in selector:
            raise ParseError(f"unknown {self.code} people category: {category!r}")
        if isinstance(parser, Mapping) and category not in parser:
            raise ParseError(f"unknown {self.code} people category: {category!r}")
        return (
            selector[category] if isinstance(selector, Mapping) else selector,
            parser[category] if isinstance(parser, Mapping) else parser,
        )

    def get_people(self, category: str, page: int = 1) -> PageResult[PersonSummary]:
        selector, row_parser = self._people_row_config(category)
        if row_parser is None:
            raise ParseError(f"{self.code} has no people list support")
        try:
            path = self._people_paths[category]
        except KeyError as exc:
            raise ParseError(f"unknown {self.code} people category: {category!r}") from exc
        soup, response_url, cached_total, cached_pages = self._paginated_page(
            f"people:{category}", path, page
        )
        items = [
            item
            for item in (row_parser(row, response_url) for row in soup.select(selector))
            if item is not None
        ]
        if not items:
            raise ParseError(f"no people items found for {category}")
        total_items, _, total_pages = self._pagination(soup, len(items))
        if total_pages == 1 and cached_pages > 1:
            total_items, total_pages = cached_total, cached_pages
        return PageResult(tuple(items), page, total_pages, total_items, response_url)

    # -- content endpoints ---------------------------------------------------

    def get_content(self, category: str) -> ContentDetail:
        try:
            path = self._content_paths[category]
        except KeyError as exc:
            raise ParseError(f"unknown {self.code} content category: {category!r}") from exc
        soup, response_url = self._fetch(urljoin(self._base_url, path))
        return self._parse_content(soup, response_url, category=category, kind="static")

    def get_detail(self, item_or_url: ArticleSummary | PersonSummary | str) -> ContentDetail:
        url = item_or_url if isinstance(item_or_url, str) else item_or_url.url
        parsed = urlparse(urljoin(self._base_url, url))
        if parsed.scheme not in {"http", "https"} or parsed.hostname != self._host:
            raise ValueError(f"detail URL must belong to {self._host}")
        soup, response_url = self._fetch(parsed.geturl())
        return self._parse_content(soup, response_url, category=None, kind="article")

    def _find_body(self, soup: BeautifulSoup) -> Tag | None:
        nodes = soup.select("[id^='vsb_content']")
        if not nodes:
            return None
        for node in nodes:
            if not node.select("[id^='vsb_content']"):
                return node
        return nodes[-1]

    def _resolve_title(self, soup: BeautifulSoup, body: Tag) -> str | None:
        # Default: the closest heading that precedes the body element.
        for element in body.previous_elements:
            if isinstance(element, Tag) and element.name in ("h1", "h2", "h3", "h4"):
                text = _clean_text(element.get_text(" ", strip=True))
                if text:
                    return text
        raw_title = soup.title.get_text(" ", strip=True) if soup.title else ""
        return _clean_text(raw_title)

    def _parse_meta(
        self, soup: BeautifulSoup, page_url: str
    ) -> tuple[date | None, str | None, int | None, str | None, str | None]:
        """Return (published_at, attribution, view_count, previous_url, next_url)."""

        return None, None, None, None, None

    def _extra_attachments(self, soup: BeautifulSoup, page_url: str) -> tuple[str, ...]:
        """Site-specific attachment links that generic link scanning misses."""

        return ()

    def _parse_content(
        self,
        soup: BeautifulSoup,
        page_url: str,
        *,
        category: str | None,
        kind: str,
    ) -> ContentDetail:
        body = self._find_body(soup)
        if body is None:
            raise ParseError("content body container not found")
        title = self._resolve_title(soup, body)
        if not title:
            raise ParseError("content title not found")
        body_soup = BeautifulSoup(str(body), "html.parser")
        clean_body = body_soup.find()
        if not isinstance(clean_body, Tag):
            raise ParseError("content body could not be normalized")
        for unwanted in clean_body.select("script, style, noscript"):
            unwanted.decompose()
        images: list[str] = []
        attachments: list[str] = []
        for tag in clean_body.find_all(True):
            for attribute in tuple(tag.attrs):
                if attribute.lower().startswith("on") or attribute.lower() == "style":
                    del tag.attrs[attribute]
            if tag.name == "img":
                absolute_src = _absolute(page_url, str(tag.get("src") or ""))
                if absolute_src:
                    tag["src"] = absolute_src
                    if absolute_src not in images:
                        images.append(absolute_src)
            if tag.name == "a":
                absolute_href = _absolute(page_url, str(tag.get("href") or ""))
                if absolute_href:
                    tag["href"] = absolute_href
                    if _ATTACHMENT_RE.search(absolute_href) and absolute_href not in attachments:
                        attachments.append(absolute_href)
                elif "href" in tag.attrs:
                    del tag.attrs["href"]
        for link in self._extra_attachments(soup, page_url):
            if link not in attachments:
                attachments.append(link)
        published_at, attribution, view_count, previous_url, next_url = self._parse_meta(
            soup, page_url
        )
        return ContentDetail(
            title=title,
            url=page_url,
            content_text=clean_body.get_text("\n", strip=True),
            content_html=clean_body.decode_contents(formatter="html"),
            images=tuple(images),
            attachments=tuple(attachments),
            published_at=published_at,
            attribution=attribution,
            view_count=view_count,
            previous_url=previous_url,
            next_url=next_url,
            category=category,
            kind=kind,
            source=self.code,
        )

    # -- home ----------------------------------------------------------------

    def get_home(self) -> SiteHome:
        raise NotImplementedError

    def _home_section(
        self,
        scope: BeautifulSoup | Tag,
        page_url: str,
        *,
        category: str,
        title: str,
        row_parser: RowParser,
        selector: str,
    ) -> HomeSection | None:
        items = [
            item
            for item in (
                row_parser(row, page_url, category)
                for row in scope.select(selector)
            )
            if item is not None
        ]
        deduped = _dedupe_articles(items)
        if not deduped:
            return None
        return HomeSection(category=category, title=title, items=deduped, source=self.code)

    # -- search --------------------------------------------------------------

    def search(self, keyword: str, page: int = 1) -> PageResult[ArticleSummary]:
        if self.search_row_selector is None:
            raise ParseError(f"{self.code} has no search support")
        _validate_page(page)
        normalized_keyword = keyword.strip()
        if not normalized_keyword:
            raise ValueError("keyword cannot be empty")
        encoded = base64.b64encode(normalized_keyword.encode("utf-8")).decode("ascii")
        if page == 1:
            params: dict[str, str | int] = {"wbtreeid": "1001"}
            data = {
                "lucenenewssearchkeyword": encoded,
                "_lucenesearchtype": "1",
                "searchScope": "0",
            }
            html, response_url = self._client._request_text(
                "POST", urljoin(self._base_url, "search.jsp"), params=params, data=data
            )
        else:
            params = {
                "wbtreeid": "1001",
                "searchScope": "0",
                "currentnum": page,
                "newskeycode2": encoded,
            }
            html, response_url = self._client._request_text(
                "GET", urljoin(self._base_url, "search.jsp"), params=params
            )
        soup = BeautifulSoup(html, "html.parser")
        items = [
            item
            for item in (
                self._article_row_parser(row, response_url, "search")
                for row in soup.select(self.search_row_selector)
            )
            if item is not None
        ]
        match = _SEARCH_PAGE_RE.search(soup.get_text(" ", strip=True))
        if match:
            total_items, total_pages, current_page = (int(value) for value in match.groups())
        else:
            total_items, total_pages, current_page = len(items), 1, page
        if total_pages > 0 and page > total_pages:
            raise InvalidPageError(
                f"page {page} is outside the available search range 1..{total_pages}"
            )
        return PageResult(
            _dedupe_articles(items),
            current_page if total_pages > 1 else page,
            total_pages,
            total_items,
            response_url,
        )


# ---------------------------------------------------------------------------
# Shared detail-template base.
# ---------------------------------------------------------------------------

#: "作者 X 时间 YYYY-MM-DD 点击数" meta line of the main_art theme
_AUTHOR_TIME_RE = re.compile(r"作者[\uFF1A:]\s*(.*?)\s*时间[\uFF1A:]\s*(\d{4}-\d{2}-\d{2})")


class MainArtVsbAdapter(VsbAdapter):
    """VS Builder sites whose article detail pages use the ``main_contit``
    title/meta block, a ``main_art`` previous/next list, and ``download.jsp``
    attachment links (jmx, gsgl, xxgc, jrsx themes)."""

    def _parse_meta(
        self, soup: BeautifulSoup, page_url: str
    ) -> tuple[date | None, str | None, int | None, str | None, str | None]:
        published_at: date | None = None
        attribution: str | None = None
        meta = soup.select_one(".main_contit")
        if meta is not None:
            match = _AUTHOR_TIME_RE.search(meta.get_text(" ", strip=True))
            if match:
                attribution = _clean_text(match.group(1))
                published_at = _parse_date(match.group(2))
        previous_url: str | None = None
        next_url: str | None = None
        nav = soup.select_one(".main_art")
        if nav is not None:
            for item in nav.select("li"):
                label = _clean_text(item.get_text(" ", strip=True)) or ""
                anchor = item.find("a", href=True)
                if not isinstance(anchor, Tag) or not label:
                    continue
                link = _absolute(page_url, str(anchor.get("href")))
                if not link:
                    continue
                if label.startswith("上一篇"):
                    previous_url = link
                elif label.startswith("下一篇"):
                    next_url = link
        return published_at, attribution, None, previous_url, next_url

    def _extra_attachments(self, soup: BeautifulSoup, page_url: str) -> tuple[str, ...]:
        return _download_attachments(soup, page_url)
