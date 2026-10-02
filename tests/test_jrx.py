from __future__ import annotations

from collections.abc import Callable
from datetime import date

import httpx
import pytest

from gduf_web_api import (
    ContentDetail,
    GdufClient,
    InvalidPageError,
    get_jrx_bsfc,
    get_jrx_detail,
    get_jrx_jfry,
    get_jrx_jgsz,
    get_jrx_kydt,
    get_jrx_xwgg,
    get_jrx_xyjj,
    get_jrx_xyld,
    get_jrx_zrjs,
    search_jrx,
)


def test_jrx_xwgg_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_jrx_xwgg(client=client)
    assert request_log[-1].url.host == "jrx.gduf.edu.cn"
    assert request_log[-1].url.path == "/xwgg.htm"
    assert len(result.items) == 8
    assert result.total_items == 520
    assert result.total_pages == 65
    first = result.items[0]
    assert first.title == "2025级金融学辅修拟录取名单公示"
    assert first.url == "https://jrx.gduf.edu.cn/info/1002/2654.htm"
    assert first.published_at == date(2026, 9, 29)
    assert first.summary is not None
    assert first.summary.startswith("根据")


def test_jrx_xwgg_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_jrx_xwgg(client=client)
    page2 = get_jrx_xwgg(page=2, client=client)
    assert request_log[-1].url.path == "/xwgg/64.htm"
    assert page2.items[0].url == "https://jrx.gduf.edu.cn/info/1002/2645.htm"
    assert page2.items[0].url != page1.items[0].url


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (999, InvalidPageError)])
def test_jrx_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    get_jrx_xwgg(client=client)
    with pytest.raises(exc):
        get_jrx_xwgg(page=page, client=client)


def test_jrx_zrjs_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_jrx_zrjs(client=client)
    assert request_log[-1].url.path == "/szdw/zrjs.htm"
    assert len(result.items) == 12
    names = [person.name for person in result.items]
    assert names[0] == "项后军"
    assert "刘昊虹" in names
    assert result.items[0].image_url is not None
    assert result.items[0].image_url.startswith("https://jrx.gduf.edu.cn/")


def test_jrx_jfry_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_jrx_jfry(client=client)
    assert request_log[-1].url.path == "/szdw/jfry.htm"
    assert len(result.items) == 7
    # names rendered with layout spacing come out compacted
    assert "韦筱" in [person.name for person in result.items]


@pytest.mark.parametrize(
    ("fetch", "path", "title"),
    [
        (get_jrx_xyjj, "/xygk/xyjj.htm", "金融与投资学院简介"),
        (get_jrx_jgsz, "/xygk/jgsz.htm", "机构设置"),
        (get_jrx_kydt, "/kydt/kydt.htm", "科研动态"),
        (get_jrx_bsfc, "/szdw/bsfc.htm", "博士风采"),
        (get_jrx_xyld, "/xygk/xyld.htm", "金融与投资学院领导班子成员"),
    ],
)
def test_jrx_static_content(
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
    assert result.source == "jrx"
    assert result.content_html


def test_jrx_detail_from_summary(client: GdufClient) -> None:
    summary = get_jrx_xwgg(client=client).items[0]
    result = get_jrx_detail(summary, client=client)
    assert result.url == summary.url == "https://jrx.gduf.edu.cn/info/1002/2654.htm"
    assert result.title == "2025级金融学辅修拟录取名单公示"
    assert result.kind == "article"
    assert result.published_at == date(2026, 9, 29)
    assert result.next_url == "https://jrx.gduf.edu.cn/info/1002/2652.htm"
    assert result.previous_url is None
    assert len(result.content_text) > 100


def test_jrx_detail_from_url(client: GdufClient) -> None:
    result = get_jrx_detail("info/1002/2654.htm", client=client)
    assert result.title == "2025级金融学辅修拟录取名单公示"
    assert result.source == "jrx"


def test_jrx_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_jrx_detail("https://example.com/info/1002/2654.htm", client=client)


def test_jrx_search(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = search_jrx("测试", client=client)
    assert request_log[-1].url.path == "/search.jsp"
    assert request_log[-1].method == "POST"
    assert result.total_items == 19
    assert result.total_pages == 3
    assert result.items[0].url == "https://jrx.gduf.edu.cn/info/1002/2645.htm"
    assert result.items[0].published_at == date(2026, 8, 31)


def test_jrx_search_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = search_jrx("测试", client=client)
    page2 = search_jrx("测试", page=2, client=client)
    assert request_log[-1].url.params["currentnum"] == "2"
    assert page2.items[0].url == "https://jrx.gduf.edu.cn/info/1002/2549.htm"
    assert page2.items[0].url != page1.items[0].url


def test_jrx_search_empty_keyword(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        search_jrx("   ", client=client)
