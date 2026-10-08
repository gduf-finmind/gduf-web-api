from __future__ import annotations

from collections.abc import Callable
from datetime import date

import httpx
import pytest

from gduf_web_api import (
    ContentDetail,
    GdufClient,
    InvalidPageError,
    PageResult,
    ParseError,
    PersonSummary,
    get_xxgc_detail,
    get_xxgc_jfry,
    get_xxgc_jsml,
    get_xxgc_jxhd,
    get_xxgc_ldjs,
    get_xxgc_szgk,
    get_xxgc_tzgg,
    get_xxgc_xyjj,
    get_xxgc_xyxw,
)

XYXW_TITLE = (
    "逐梦科创启新程 拔尖笃行向未来——"
    "我校2026级计算机科学与技术拔尖班\uFF08首届\uFF09顺利开班"
)
XYXW_URL = "https://xxgc.gduf.edu.cn/info/1055/3902.htm"


def test_xxgc_xyxw_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_xxgc_xyxw(client=client)
    assert request_log[-1].url.host == "xxgc.gduf.edu.cn"
    assert request_log[-1].url.path == "/index/xyxw.htm"
    assert len(result.items) == 16
    assert result.total_items == 343
    assert result.total_pages == 22
    first = result.items[0]
    assert first.title == XYXW_TITLE
    assert first.url == XYXW_URL
    assert first.published_at == date(2026, 9, 29)


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_xxgc_tzgg, "/tzgg.htm", 19, 2),
        (get_xxgc_jxhd, "/index/jxhd.htm", 46, 3),
    ],
)
def test_xxgc_article_columns(
    client: GdufClient,
    request_log: list[httpx.Request],
    fetch: Callable[..., PageResult],
    path: str,
    total_items: int,
    total_pages: int,
) -> None:
    result = fetch(client=client)
    assert request_log[-1].url.path == path
    assert result.total_items == total_items
    assert result.total_pages == total_pages
    first = result.items[0]
    assert first.title
    assert first.published_at is not None


def test_xxgc_xyxw_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_xxgc_xyxw(client=client)
    page2 = get_xxgc_xyxw(page=2, client=client)
    assert request_log[-1].url.path == "/index/xyxw/21.htm"
    assert page2.items[0].url != page1.items[0].url
    assert page2.items[0].url == "https://xxgc.gduf.edu.cn/info/1055/3889.htm"
    assert page2.items[0].published_at == date(2026, 7, 8)


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages", "first_name", "first_url", "bio_prefix"),
    [
        (
            get_xxgc_jsml,
            "/szdw/jsml.htm",
            77,
            13,
            "潘章明",
            "https://xxgc.gduf.edu.cn/info/1108/1689.htm",
            "潘章明\uFF0C男",
        ),
        (
            get_xxgc_jfry,
            "/szdw/jfry.htm",
            11,
            2,
            "曹馨",
            "https://xxgc.gduf.edu.cn/info/1112/3136.htm",
            "曹馨\uFF0C女",
        ),
    ],
)
def test_xxgc_people_columns(
    client: GdufClient,
    request_log: list[httpx.Request],
    fetch: Callable[..., PageResult],
    path: str,
    total_items: int,
    total_pages: int,
    first_name: str,
    first_url: str,
    bio_prefix: str,
) -> None:
    result: PageResult[PersonSummary] = fetch(client=client)
    assert request_log[-1].url.path == path
    assert result.total_items == total_items
    assert result.total_pages == total_pages
    first = result.items[0]
    assert first.name == first_name
    assert first.url == first_url
    assert first.image_url
    assert first.responsibility is not None
    assert first.responsibility.startswith(bio_prefix)
    assert "详细" not in first.responsibility


@pytest.mark.parametrize(
    ("fetch", "path", "title"),
    [
        (get_xxgc_xyjj, "/xygk/xyjj.htm", "计算机学院简介"),
        (get_xxgc_ldjs, "/xygk/ldjs.htm", "学院领导"),
        (get_xxgc_szgk, "/szdw/szgk.htm", "师资概况"),
    ],
)
def test_xxgc_static_content(
    client: GdufClient,
    request_log: list[httpx.Request],
    fetch: Callable[..., ContentDetail],
    path: str,
    title: str,
) -> None:
    result = fetch(client=client)
    assert request_log[-1].url.path == path
    assert result.title == title
    assert result.kind == "static"
    assert result.source == "xxgc"


def test_xxgc_detail_from_summary(client: GdufClient) -> None:
    summary = get_xxgc_xyxw(client=client).items[0]
    result = get_xxgc_detail(summary, client=client)
    assert result.url == summary.url == XYXW_URL
    assert result.title == XYXW_TITLE
    assert result.kind == "article"
    assert result.published_at == date(2026, 9, 29)
    assert result.attribution == "计算机学院"
    assert result.previous_url is None
    assert result.next_url == "https://xxgc.gduf.edu.cn/info/1055/3899.htm"
    assert len(result.content_text) > 100


def test_xxgc_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_xxgc_detail("https://www.gduf.edu.cn/index.htm", client=client)


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (23, InvalidPageError)])
def test_xxgc_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    with pytest.raises(exc):
        get_xxgc_xyxw(page=page, client=client)


def test_xxgc_has_no_search(client: GdufClient) -> None:
    with pytest.raises(ParseError):
        client.search("测试", source="xxgc")
