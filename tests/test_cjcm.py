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
    get_cjcm_detail,
    get_cjcm_jxdt,
    get_cjcm_kydt,
    get_cjcm_szgk,
    get_cjcm_tzgg,
    get_cjcm_wlyxmtx,
    get_cjcm_xrld,
    get_cjcm_xyjj,
    get_cjcm_xykj,
    get_cjcm_xyxw,
)

XYXW_TITLE = "校际携手共拓育人新局\uFF1A我院赴深圳大学传播学院开展网络与新媒体专业专题调研"
XYXW_URL = "https://cjcm.gduf.edu.cn/info/1061/2722.htm"
DETAIL_TITLE = "数字媒体艺术专业2026本科毕业设计答辩暨作品展"


def test_cjcm_xyxw_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_cjcm_xyxw(client=client)
    assert request_log[-1].url.host == "cjcm.gduf.edu.cn"
    assert request_log[-1].url.path == "/xyxw.htm"
    assert len(result.items) == 15
    assert result.total_items == 218
    assert result.total_pages == 15
    first = result.items[0]
    assert first.title == XYXW_TITLE
    assert first.url == XYXW_URL
    assert first.published_at == date(2026, 6, 25)


def test_cjcm_xyxw_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_cjcm_xyxw(client=client)
    page2 = get_cjcm_xyxw(page=2, client=client)
    assert request_log[-1].url.path == "/xyxw/14.htm"
    assert page2.items[0].url != page1.items[0].url
    assert page2.items[0].published_at is not None


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_cjcm_tzgg, "/tzgg.htm", 232, 16),
        (get_cjcm_jxdt, "/jxgz/jxdt.htm", 93, 7),
        (get_cjcm_kydt, "/xsky/kydt.htm", 20, 2),
        (get_cjcm_xykj, "/xykj.htm", 63, 5),
    ],
)
def test_cjcm_article_columns(
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


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (999, InvalidPageError)])
def test_cjcm_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    get_cjcm_xyxw(client=client)
    with pytest.raises(exc):
        get_cjcm_xyxw(page=page, client=client)


def test_cjcm_wlyxmtx_people(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_cjcm_wlyxmtx(client=client)
    assert request_log[-1].url.path == "/szdw/wlyxmtx.htm"
    assert len(result.items) == 12
    assert result.total_items == 18
    assert result.total_pages == 2
    first = result.items[0]
    # photo cards carry "姓名 职务" and split name-first
    assert first.name == "陈映"
    assert first.role == "院长"
    assert first.url == "https://cjcm.gduf.edu.cn/info/1079/1171.htm"
    assert first.image_url is not None
    assert first.image_url.startswith("https://cjcm.gduf.edu.cn/__local/")


@pytest.mark.parametrize(
    ("fetch", "path", "title"),
    [
        (get_cjcm_xyjj, "/xygk/xyjj.htm", "财经与新媒体学院的历史沿革与概况"),
        (get_cjcm_szgk, "/szdw/szgk.htm", "财经与新媒体学院师资概况"),
        (get_cjcm_xrld, "/xygk/xrld.htm", "现任领导"),
    ],
)
def test_cjcm_static_content(
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
    assert result.source == "cjcm"
    assert result.content_html


def test_cjcm_detail_from_summary(client: GdufClient) -> None:
    summary = get_cjcm_xyxw(client=client).items[0]
    result = get_cjcm_detail(summary, client=client)
    assert result.url == summary.url == XYXW_URL
    assert result.title == DETAIL_TITLE
    assert result.kind == "article"
    # neighboring articles often live on the WeChat platform
    assert result.previous_url == "https://mp.weixin.qq.com/s/a6Al3oLpZfqaJS-CiexHvA"
    assert result.next_url == "https://mp.weixin.qq.com/s/Uvh47Xwf_9koSAbAMYhbvw"
    # attachments link through download.jsp without a file extension
    assert result.attachments
    assert "wbfileid=15475894" in result.attachments[0]
    assert len(result.content_text) > 100


def test_cjcm_detail_rejects_external_url(client: GdufClient) -> None:
    # WeChat article links cannot be fetched as cjcm details
    with pytest.raises(ValueError):
        get_cjcm_detail("https://mp.weixin.qq.com/s/a6Al3oLpZfqaJS-CiexHvA", client=client)


def test_cjcm_has_no_search(client: GdufClient) -> None:
    with pytest.raises(ParseError):
        client.search("测试", source="cjcm")
