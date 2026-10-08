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
    get_jrsx_detail,
    get_jrsx_jsml,
    get_jrsx_msfc,
    get_jrsx_ssds,
    get_jrsx_szgk,
    get_jrsx_tzgg,
    get_jrsx_xwxx,
    get_jrsx_xyjj,
    get_jrsx_xyld,
)

XWXX_TITLE = "涵养正确价值追求 书写时代奋进篇章"
XWXX_URL = "https://jrsx.gduf.edu.cn/info/1055/3563.htm"
DETAIL_TITLE = "数统学院举办国家自然科学基金项目申报经验分享会"


def test_jrsx_xwxx_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_jrsx_xwxx(client=client)
    assert request_log[-1].url.host == "jrsx.gduf.edu.cn"
    assert request_log[-1].url.path == "/index/xwxx.htm"
    assert len(result.items) == 16
    assert result.total_items == 415
    assert result.total_pages == 26
    first = result.items[0]
    assert first.title == XWXX_TITLE
    assert first.url == XWXX_URL
    assert first.published_at == date(2026, 4, 30)


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_jrsx_tzgg, "/index/tzgg.htm", 35, 3),
        (get_jrsx_msfc, "/szdw/msfc.htm", 5, 1),
        (get_jrsx_szgk, "/szdw/szgk.htm", 6, 1),
    ],
)
def test_jrsx_article_columns(
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


def test_jrsx_xwxx_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_jrsx_xwxx(client=client)
    page2 = get_jrsx_xwxx(page=2, client=client)
    assert request_log[-1].url.path == "/index/xwxx/25.htm"
    assert page2.items[0].url != page1.items[0].url
    # the column lists external WeChat entries alongside on-site articles
    assert page2.items[0].url == "https://mp.weixin.qq.com/s/LnaXUT1kgL838A_njDyJoA"
    assert page2.items[0].published_at == date(2026, 5, 14)


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages", "first_name", "first_url"),
    [
        (
            get_jrsx_jsml,
            "/szdw/jsml.htm",
            78,
            5,
            "屈文鑫",
            "https://jrsx.gduf.edu.cn/info/1150/1856.htm",
        ),
        (
            get_jrsx_ssds,
            "/szdw/ssds.htm",
            43,
            3,
            "易行健",
            "https://jrsx.gduf.edu.cn/info/1169/3441.htm",
        ),
    ],
)
def test_jrsx_people_columns(
    client: GdufClient,
    request_log: list[httpx.Request],
    fetch: Callable[..., PageResult],
    path: str,
    total_items: int,
    total_pages: int,
    first_name: str,
    first_url: str,
) -> None:
    result: PageResult[PersonSummary] = fetch(client=client)
    assert request_log[-1].url.path == path
    assert result.total_items == total_items
    assert result.total_pages == total_pages
    first = result.items[0]
    assert first.name == first_name
    assert first.url == first_url


@pytest.mark.parametrize(
    ("fetch", "path", "title"),
    [
        (get_jrsx_xyjj, "/xygk1/xyjj.htm", "金融数学与统计学院简介"),
        (get_jrsx_xyld, "/xygk1/xyld.htm", "学院领导"),
    ],
)
def test_jrsx_static_content(
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
    assert result.source == "jrsx"


def test_jrsx_detail_from_summary(client: GdufClient) -> None:
    summary = get_jrsx_xwxx(client=client).items[0]
    result = get_jrsx_detail(summary, client=client)
    assert result.url == summary.url == XWXX_URL
    assert result.title == DETAIL_TITLE
    assert result.kind == "article"
    assert result.published_at == date(2026, 9, 20)
    assert result.attribution == "何忠华"
    assert result.previous_url is None
    assert result.next_url == "https://jrsx.gduf.edu.cn/info/1055/3614.htm"
    assert len(result.content_text) > 100


def test_jrsx_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_jrsx_detail("https://www.gduf.edu.cn/index.htm", client=client)


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (27, InvalidPageError)])
def test_jrsx_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    with pytest.raises(exc):
        get_jrsx_xwxx(page=page, client=client)


def test_jrsx_has_no_search(client: GdufClient) -> None:
    with pytest.raises(ParseError):
        client.search("测试", source="jrsx")
