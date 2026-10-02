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
    get_bxx_detail,
    get_bxx_fjs,
    get_bxx_js,
    get_bxx_kydt,
    get_bxx_szgk,
    get_bxx_xrld,
    get_bxx_xsjl,
    get_bxx_xwgg,
    get_bxx_xyjj,
)

DETAIL_TITLE = "广东金融学院2026级精算学专业FRM\uFF08金融风险管理师\uFF09实验班招生简章"


def test_bxx_xwgg_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_bxx_xwgg(client=client)
    assert request_log[-1].url.host == "bxx.gduf.edu.cn"
    assert request_log[-1].url.path == "/xwgg.htm"
    assert len(result.items) == 20
    assert result.total_items == 299
    assert result.total_pages == 15
    first = result.items[0]
    assert first.title == "保险学院举办国家自然科学基金立项经验分享研讨会"
    assert first.url == "https://bxx.gduf.edu.cn/info/1003/3491.htm"
    # bxx list rows render no dates
    assert first.published_at is None


def test_bxx_xwgg_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_bxx_xwgg(client=client)
    page2 = get_bxx_xwgg(page=2, client=client)
    assert request_log[-1].url.path == "/xwgg/14.htm"
    assert page2.items[0].url != page1.items[0].url
    assert page2.items[0].title


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_bxx_kydt, "/kxyj/kydt.htm", 16, 1),
        (get_bxx_xsjl, "/kxyj/xsjl.htm", 43, 3),
    ],
)
def test_bxx_article_columns(
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
    assert first.url.startswith("https://bxx.gduf.edu.cn/info/")


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (999, InvalidPageError)])
def test_bxx_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    get_bxx_xwgg(client=client)
    with pytest.raises(exc):
        get_bxx_xwgg(page=page, client=client)


def test_bxx_xrld_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_bxx_xrld(client=client)
    assert request_log[-1].url.path == "/xygk1/xrld.htm"
    assert len(result.items) == 4
    first = result.items[0]
    # leader rows carry "职务 姓名" and split on the last whitespace run
    assert first.name == "刘新强"
    assert first.role == "保险学院党委书记"
    assert first.url == "https://bxx.gduf.edu.cn/info/1023/2295.htm"


def test_bxx_js_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_bxx_js(client=client)
    assert request_log[-1].url.path == "/szdw/jsml/js.htm"
    assert len(result.items) == 3
    assert result.items[0].name == "初可佳"
    assert result.items[0].role is None


def test_bxx_fjs_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_bxx_fjs(client=client)
    assert request_log[-1].url.path == "/szdw/jsml/fjs.htm"
    assert len(result.items) == 11
    assert result.items[0].name == "张伟"


@pytest.mark.parametrize(
    ("fetch", "path", "title"),
    [
        (get_bxx_xyjj, "/xygk1/xyjj.htm", "学院简介"),
        (get_bxx_szgk, "/szdw/szgk.htm", "师资概况"),
    ],
)
def test_bxx_static_content(
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
    assert result.source == "bxx"
    assert result.content_html


def test_bxx_detail_from_summary(client: GdufClient) -> None:
    summary = get_bxx_xwgg(client=client).items[0]
    result = get_bxx_detail(summary, client=client)
    assert result.url == summary.url == "https://bxx.gduf.edu.cn/info/1003/3491.htm"
    assert result.title == DETAIL_TITLE
    assert result.kind == "article"
    assert result.published_at == date(2026, 8, 7)
    assert result.attribution is None
    assert result.previous_url is None
    assert result.next_url is None
    assert len(result.content_text) > 100


def test_bxx_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_bxx_detail("https://example.com/info/1003/3491.htm", client=client)


def test_bxx_has_no_search(client: GdufClient) -> None:
    with pytest.raises(ParseError):
        client.search("测试", source="bxx")
