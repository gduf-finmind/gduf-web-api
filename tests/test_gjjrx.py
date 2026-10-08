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
    get_gjjrx_bsfc,
    get_gjjrx_detail,
    get_gjjrx_dtxg,
    get_gjjrx_gjzk,
    get_gjjrx_jfry,
    get_gjjrx_jgsz,
    get_gjjrx_jsfc,
    get_gjjrx_jxky,
    get_gjjrx_szgk,
    get_gjjrx_tzgg,
    get_gjjrx_xrld,
    get_gjjrx_xyjj,
    get_gjjrx_xyxw,
    get_gjjrx_zrjs,
    search_gjjrx,
)

XYXW_TITLE = "喜讯\uFF1A国家金融学学院院长张玲教授获批2026年度国家自然科学基金项目"
XYXW_URL = "https://gjjrx.gduf.edu.cn/info/1056/2264.htm"
DETAIL_TITLE = "国家金融学学院院长张玲教授应邀参加两场数字金融与金融科技学术会议"


def test_gjjrx_xyxw_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_gjjrx_xyxw(client=client)
    assert request_log[-1].url.host == "gjjrx.gduf.edu.cn"
    assert request_log[-1].url.path == "/xwzx/xyxw.htm"
    assert len(result.items) == 15
    assert result.total_items == 157
    assert result.total_pages == 11
    first = result.items[0]
    assert first.title == XYXW_TITLE
    assert first.url == XYXW_URL
    assert first.published_at == date(2026, 9, 4)


def test_gjjrx_xyxw_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_gjjrx_xyxw(client=client)
    page2 = get_gjjrx_xyxw(page=2, client=client)
    assert request_log[-1].url.path == "/xwzx/xyxw/10.htm"
    assert page2.items[0].url != page1.items[0].url
    assert page2.items[0].url == "https://gjjrx.gduf.edu.cn/info/1056/2279.htm"
    assert page2.items[0].published_at is not None


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_gjjrx_tzgg, "/xwzx/tzgg.htm", 32, 3),
        (get_gjjrx_jxky, "/xwzx/jxky.htm", 70, 5),
        (get_gjjrx_dtxg, "/xwzx/dtxg.htm", 130, 9),
        (get_gjjrx_gjzk, "/xwzx/gjzk.htm", 14, 1),
    ],
)
def test_gjjrx_article_columns(
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


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_gjjrx_zrjs, "/szdw/zrjs.htm", 26, 3),
        (get_gjjrx_bsfc, "/szdw/bsfc.htm", 20, 2),
        (get_gjjrx_jsfc, "/szdw/jsfc.htm", 14, 2),
    ],
)
def test_gjjrx_staff_lists(
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
    assert first.name
    assert first.image_url is not None
    assert first.image_url.startswith("https://gjjrx.gduf.edu.cn/__local/")


def test_gjjrx_zrjs_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    get_gjjrx_zrjs(client=client)
    page2 = get_gjjrx_zrjs(page=2, client=client)
    assert request_log[-1].url.path == "/szdw/zrjs/2.htm"
    assert page2.items[0].name == "马克和"
    assert page2.items[0].url == "https://gjjrx.gduf.edu.cn/info/1051/1140.htm"


def test_gjjrx_jfry_splits_department(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_gjjrx_jfry(client=client)
    assert request_log[-1].url.path == "/szdw/jfry.htm"
    assert len(result.items) == 5
    first = result.items[0]
    # the card text reads "部门—姓名"
    assert first.name == "黄朔"
    assert first.role == "办公室"
    assert first.url == "https://gjjrx.gduf.edu.cn/info/1052/1123.htm"


def test_gjjrx_xrld_leader_cards(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_gjjrx_xrld(client=client)
    assert request_log[-1].url.path == "/xygk/xyld.htm"
    assert len(result.items) == 5
    first = result.items[0]
    assert first.name == "丘志君"
    assert first.role == "党总支书记"
    assert first.url == "https://gjjrx.gduf.edu.cn/info/1045/1195.htm"
    assert first.image_url is not None


@pytest.mark.parametrize(
    ("fetch", "path", "title"),
    [
        (get_gjjrx_xyjj, "/xygk/xyjj.htm", "学院简介"),
        (get_gjjrx_jgsz, "/xygk/jgsz.htm", "机构设置"),
        (get_gjjrx_szgk, "/szdw/szgk.htm", "师资概况"),
    ],
)
def test_gjjrx_static_content(
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
    assert result.source == "gjjrx"


def test_gjjrx_detail_from_url(client: GdufClient) -> None:
    result = get_gjjrx_detail("https://gjjrx.gduf.edu.cn/info/1056/2284.htm", client=client)
    assert result.title == DETAIL_TITLE
    assert result.kind == "article"
    assert result.published_at == date(2026, 9, 11)
    assert result.attribution == "本站"
    assert result.previous_url == "https://gjjrx.gduf.edu.cn/info/1056/2287.htm"
    assert result.next_url == "https://gjjrx.gduf.edu.cn/info/1056/2279.htm"
    assert len(result.content_text) > 100
    assert result.images


def test_gjjrx_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_gjjrx_detail("https://www.gduf.edu.cn/index.htm", client=client)


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (12, InvalidPageError)])
def test_gjjrx_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    with pytest.raises(exc):
        get_gjjrx_xyxw(page=page, client=client)


def test_gjjrx_search(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = search_gjjrx("研究生", client=client)
    assert request_log[-1].method == "POST"
    assert request_log[-1].url.path == "/search.jsp"
    assert result.total_items == 94
    assert result.total_pages == 7
    first = result.items[0]
    assert first.url == "https://gjjrx.gduf.edu.cn/info/1056/2304.htm"
    assert first.published_at == date(2026, 9, 30)


def test_gjjrx_search_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = search_gjjrx("研究生", client=client)
    page2 = search_gjjrx("研究生", page=2, client=client)
    assert request_log[-1].method == "GET"
    assert request_log[-1].url.params.get("currentnum") == "2"
    assert page2.items[0].url != page1.items[0].url
    assert page2.items[0].url == "https://gjjrx.gduf.edu.cn/info/1086/2243.htm"


def test_gjjrx_search_empty_keyword(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        search_gjjrx("   ", client=client)
