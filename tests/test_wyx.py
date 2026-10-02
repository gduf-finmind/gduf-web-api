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
    get_wyx_detail,
    get_wyx_djdt,
    get_wyx_fjs,
    get_wyx_js,
    get_wyx_kydt,
    get_wyx_szgk,
    get_wyx_tzgg,
    get_wyx_xgdt,
    get_wyx_xrld,
    get_wyx_xyjj,
    get_wyx_xyxw,
)

TZGG_TITLE = "2026年广东省研究生学术论坛暨第四届行业话语与翻译论坛二号通知"
TZGG_URL = "https://wyx.gduf.edu.cn/info/1068/3532.htm"


def test_wyx_tzgg_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_wyx_tzgg(client=client)
    assert request_log[-1].url.host == "wyx.gduf.edu.cn"
    assert request_log[-1].url.path == "/tzgg.htm"
    assert len(result.items) == 15
    assert result.total_items == 26
    assert result.total_pages == 2
    first = result.items[0]
    assert first.title == TZGG_TITLE
    assert first.url == TZGG_URL
    assert first.published_at == date(2026, 9, 20)


def test_wyx_tzgg_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_wyx_tzgg(client=client)
    page2 = get_wyx_tzgg(page=2, client=client)
    assert request_log[-1].url.path == "/tzgg/1.htm"
    assert page2.items[0].url != page1.items[0].url
    assert page2.items[0].published_at is not None


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_wyx_xyxw, "/xyxw.htm", 1172, 79),
        (get_wyx_djdt, "/dqgz/djdt.htm", 161, 11),
        (get_wyx_kydt, "/xsky/kydt.htm", 127, 9),
        (get_wyx_xgdt, "/xszc/xgdt.htm", 101, 7),
    ],
)
def test_wyx_article_columns(
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
    assert first.url.startswith("https://wyx.gduf.edu.cn/info/")
    assert first.published_at is not None


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (999, InvalidPageError)])
def test_wyx_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    get_wyx_tzgg(client=client)
    with pytest.raises(exc):
        get_wyx_tzgg(page=page, client=client)


def test_wyx_js_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_wyx_js(client=client)
    assert request_log[-1].url.path == "/szll/js.htm"
    assert len(result.items) == 5
    first = result.items[0]
    assert first.name == "黄中习"
    assert first.role == "三级教授"
    assert first.url == "https://wyx.gduf.edu.cn/info/1048/1458.htm"
    assert first.image_url is not None
    assert first.image_url.startswith("https://wyx.gduf.edu.cn/__local/")


def test_wyx_fjs_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_wyx_fjs(client=client)
    assert request_log[-1].url.path == "/szll/fjs.htm"
    assert len(result.items) == 14
    assert all(person.name for person in result.items)


@pytest.mark.parametrize(
    ("fetch", "path", "title"),
    [
        (get_wyx_xyjj, "/xygk/xyjj.htm", "学院简介"),
        (get_wyx_szgk, "/szll/dwgk.htm", "队伍概况"),
        (get_wyx_xrld, "/xygk/xrld.htm", "现任领导"),
    ],
)
def test_wyx_static_content(
    client: GdufClient,
    request_log: list[httpx.Request],
    fetch: Callable[..., ContentDetail],
    path: str,
    title: str,
) -> None:
    # static pages have no heading; the title repeats as the last breadcrumb segment
    result = fetch(client=client)
    assert request_log[-1].url.path == path
    assert result.title == title
    assert result.kind == "static"
    assert result.source == "wyx"
    assert result.content_html


def test_wyx_detail_from_summary(client: GdufClient) -> None:
    summary = get_wyx_tzgg(client=client).items[0]
    result = get_wyx_detail(summary, client=client)
    assert result.url == summary.url == TZGG_URL
    assert result.title == TZGG_TITLE
    assert result.kind == "article"
    assert result.published_at == date(2026, 9, 20)
    assert len(result.content_text) > 100


def test_wyx_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_wyx_detail("https://example.com/info/1068/3532.htm", client=client)


def test_wyx_has_no_search(client: GdufClient) -> None:
    with pytest.raises(ParseError):
        client.search("测试", source="wyx")
