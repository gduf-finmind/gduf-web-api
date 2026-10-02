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
    get_kjx_detail,
    get_kjx_dthd,
    get_kjx_fjs,
    get_kjx_js,
    get_kjx_jxgl,
    get_kjx_kydt,
    get_kjx_szgk,
    get_kjx_xrld,
    get_kjx_xxgg,
    get_kjx_xyjj,
    get_kjx_xzry,
)

XXGG_TITLE = "月圆中秋 情暖会院\u2014\u2014会计学院开展中秋慰问活动"
XXGG_URL = "https://kjx.gduf.edu.cn/info/1106/2952.htm"
FIRST_ROLE = "教授\uFF0C会计学院副院长\uFF08主持工作\uFF09"


def test_kjx_xxgg_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_kjx_xxgg(client=client)
    assert request_log[-1].url.host == "kjx.gduf.edu.cn"
    assert request_log[-1].url.path == "/index/xxgg.htm"
    assert len(result.items) == 16
    assert result.total_items == 357
    assert result.total_pages == 23
    first = result.items[0]
    assert first.title == XXGG_TITLE
    assert first.url == XXGG_URL
    assert first.published_at == date(2026, 9, 29)


def test_kjx_xxgg_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_kjx_xxgg(client=client)
    page2 = get_kjx_xxgg(page=2, client=client)
    assert request_log[-1].url.path == "/index/xxgg/22.htm"
    assert page2.items[0].url != page1.items[0].url
    assert page2.items[0].published_at is not None


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_kjx_dthd, "/dtjs/dthd.htm", 32, 2),
        (get_kjx_jxgl, "/zyjx/jxgl.htm", 67, 5),
        (get_kjx_kydt, "/kxyj/kydt.htm", 96, 6),
    ],
)
def test_kjx_article_columns(
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
    assert first.url.startswith("https://kjx.gduf.edu.cn/info/")
    assert first.published_at is not None


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (999, InvalidPageError)])
def test_kjx_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    get_kjx_xxgg(client=client)
    with pytest.raises(exc):
        get_kjx_xxgg(page=page, client=client)


def test_kjx_js_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_kjx_js(client=client)
    assert request_log[-1].url.path == "/szdw/js.htm"
    assert len(result.items) == 6
    assert result.total_items == 14
    assert result.total_pages == 3
    first = result.items[0]
    # names rendered with layout spacing come out compacted
    assert first.name == "秦格"
    assert first.role == FIRST_ROLE
    assert first.url == "https://kjx.gduf.edu.cn/info/1067/1151.htm"
    assert first.image_url is not None
    assert first.image_url.startswith("https://kjx.gduf.edu.cn/__local/")


def test_kjx_js_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_kjx_js(client=client)
    page2 = get_kjx_js(page=2, client=client)
    assert request_log[-1].url.path == "/szdw/js/2.htm"
    assert page2.items[0].name != page1.items[0].name


def test_kjx_fjs_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_kjx_fjs(client=client)
    assert request_log[-1].url.path == "/szdw/fjs.htm"
    assert len(result.items) == 6
    assert result.total_items == 12
    assert result.total_pages == 2
    names = [person.name for person in result.items]
    assert all(names)
    assert all(person.role for person in result.items)


def test_kjx_xzry_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_kjx_xzry(client=client)
    assert request_log[-1].url.path == "/szdw/xzry.htm"
    assert len(result.items) == 2
    assert result.total_items == 2
    assert result.total_pages == 1


@pytest.mark.parametrize(
    ("fetch", "path", "title"),
    [
        (get_kjx_xyjj, "/yxgk/xyjj.htm", "学院简介"),
        (get_kjx_szgk, "/szdw/szgk.htm", "师资概况"),
        (get_kjx_xrld, "/yxgk/xrld.htm", "会计学院现任领导"),
    ],
)
def test_kjx_static_content(
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
    assert result.source == "kjx"
    assert result.content_html


def test_kjx_detail_from_summary(client: GdufClient) -> None:
    summary = get_kjx_xxgg(client=client).items[0]
    result = get_kjx_detail(summary, client=client)
    assert result.url == summary.url == XXGG_URL
    assert result.title == XXGG_TITLE
    assert result.kind == "article"
    assert result.published_at == date(2026, 9, 29)
    assert result.next_url == "https://kjx.gduf.edu.cn/info/1106/2951.htm"
    assert result.previous_url is None
    assert result.attribution is None
    assert len(result.content_text) > 100


def test_kjx_detail_from_person(client: GdufClient) -> None:
    person: PersonSummary = get_kjx_js(client=client).items[0]
    result = get_kjx_detail(person, client=client)
    assert result.url == person.url == "https://kjx.gduf.edu.cn/info/1067/1151.htm"
    assert result.source == "kjx"


def test_kjx_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_kjx_detail("https://example.com/info/1106/2952.htm", client=client)


def test_kjx_has_no_search(client: GdufClient) -> None:
    with pytest.raises(ParseError):
        client.search("测试", source="kjx")
