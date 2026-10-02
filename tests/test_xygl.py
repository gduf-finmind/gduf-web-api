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
    get_xygl_detail,
    get_xygl_kydt,
    get_xygl_msfc,
    get_xygl_szgk,
    get_xygl_xrld,
    get_xygl_xyjj,
    get_xygl_zrjs,
    get_xygl_zxzx,
)

ZXZX_TITLE = "信用管理学院开展期中教学观摩评议活动"
ZXZX_URL = "https://xygl.gduf.edu.cn/info/1036/2744.htm"


def test_xygl_zxzx_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_xygl_zxzx(client=client)
    assert request_log[-1].url.host == "xygl.gduf.edu.cn"
    assert request_log[-1].url.path == "/index/zxzx.htm"
    assert len(result.items) == 10
    assert result.total_items == 135
    assert result.total_pages == 14
    first = result.items[0]
    assert first.title == ZXZX_TITLE
    assert first.url == ZXZX_URL
    # rows render "day + English month" without a year, so no date is guessed
    assert first.published_at is None
    assert first.summary is not None


def test_xygl_zxzx_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_xygl_zxzx(client=client)
    page2 = get_xygl_zxzx(page=2, client=client)
    assert request_log[-1].url.path == "/index/zxzx/13.htm"
    assert page2.items[0].url != page1.items[0].url
    assert page2.items[0].title


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_xygl_kydt, "/xsky/kydt.htm", 30, 3),
        (get_xygl_msfc, "/index/msfc.htm", 4, 1),
    ],
)
def test_xygl_article_columns(
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
    assert first.url.startswith("https://xygl.gduf.edu.cn/info/")


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (999, InvalidPageError)])
def test_xygl_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    get_xygl_zxzx(client=client)
    with pytest.raises(exc):
        get_xygl_zxzx(page=page, client=client)


def test_xygl_zrjs_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_xygl_zrjs(client=client)
    assert request_log[-1].url.path == "/szdw/zrjs.htm"
    assert len(result.items) == 10
    assert result.total_items == 28
    assert result.total_pages == 3
    first = result.items[0]
    assert first.name == "黄苹"
    assert first.url == "https://xygl.gduf.edu.cn/info/1085/2295.htm"
    assert first.responsibility is not None
    assert first.image_url is not None
    assert first.image_url.startswith("https://xygl.gduf.edu.cn/__local/")


@pytest.mark.parametrize(
    ("fetch", "path", "title"),
    [
        (get_xygl_xyjj, "/xygk/xyjj.htm", "学院简介"),
        (get_xygl_szgk, "/szdw/szgk.htm", "师资概况"),
        (get_xygl_xrld, "/xygk/xrld.htm", "现任领导"),
    ],
)
def test_xygl_static_content(
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
    assert result.source == "xygl"
    assert result.content_html


def test_xygl_detail_from_summary(client: GdufClient) -> None:
    summary = get_xygl_zxzx(client=client).items[0]
    result = get_xygl_detail(summary, client=client)
    assert result.url == summary.url == ZXZX_URL
    assert result.title == ZXZX_TITLE
    assert result.kind == "article"
    # the detail h3 renders the publication date
    assert result.published_at == date(2026, 5, 26)
    assert len(result.content_text) > 100


def test_xygl_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_xygl_detail("https://example.com/info/1036/2744.htm", client=client)


def test_xygl_has_no_search(client: GdufClient) -> None:
    with pytest.raises(ParseError):
        client.search("测试", source="xygl")
