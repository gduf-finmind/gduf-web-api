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
    get_jmx_detail,
    get_jmx_djhd,
    get_jmx_jgsz,
    get_jmx_jxhd,
    get_jmx_kyhd,
    get_jmx_ssfc,
    get_jmx_szdw,
    get_jmx_xrld,
    get_jmx_xwgg,
    get_jmx_xyjj,
)

XWGG_TITLE = "广东金融学院经济贸易学院2026级经济学拔尖人才培养创新实验班招生简章"
XWGG_URL = "https://jmx.gduf.edu.cn/info/1093/3725.htm"
DETAIL_TITLE = XWGG_TITLE


def test_jmx_xwgg_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_jmx_xwgg(client=client)
    assert request_log[-1].url.host == "jmx.gduf.edu.cn"
    assert request_log[-1].url.path == "/index/xwgg.htm"
    assert len(result.items) == 16
    assert result.total_items == 233
    assert result.total_pages == 15
    first = result.items[0]
    assert first.title == XWGG_TITLE
    assert first.url == XWGG_URL
    assert first.published_at == date(2026, 9, 3)


def test_jmx_xwgg_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_jmx_xwgg(client=client)
    page2 = get_jmx_xwgg(page=2, client=client)
    assert request_log[-1].url.path == "/index/xwgg/14.htm"
    assert page2.items[0].url != page1.items[0].url
    assert page2.items[0].url == "https://jmx.gduf.edu.cn/info/1093/3640.htm"
    assert page2.items[0].published_at == date(2026, 6, 11)


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_jmx_djhd, "/index/djhd.htm", 51, 4),
        (get_jmx_jxhd, "/index/jxhd.htm", 44, 3),
        (get_jmx_kyhd, "/index/kyhd.htm", 30, 2),
        (get_jmx_ssfc, "/index/ssfc.htm", 44, 3),
    ],
)
def test_jmx_article_columns(
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


def test_jmx_column_lists(client: GdufClient, request_log: list[httpx.Request]) -> None:
    # 学院概况/师资队伍 are column lists rather than static pages
    profile = get_jmx_xyjj(client=client)
    assert request_log[-1].url.path == "/xygk/xyjj.htm"
    assert profile.total_items == 2
    assert profile.items[0].title == "经济贸易学院简介"
    assert profile.items[0].url == "https://jmx.gduf.edu.cn/info/1057/2128.htm"

    staff = get_jmx_szdw(client=client)
    assert request_log[-1].url.path == "/xygk/szdw.htm"
    assert staff.total_items == 1
    assert staff.items[0].title == "经济贸易学院全体教师合影"


@pytest.mark.parametrize(
    ("fetch", "path", "title"),
    [
        (get_jmx_jgsz, "/xygk/jgsz.htm", "经济贸易学院机构设置"),
        (get_jmx_xrld, "/xygk/xrld.htm", "现任领导、系、教研负责人"),
    ],
)
def test_jmx_static_content(
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
    assert result.source == "jmx"


def test_jmx_detail_from_summary(client: GdufClient) -> None:
    summary = get_jmx_xwgg(client=client).items[0]
    result = get_jmx_detail(summary, client=client)
    assert result.url == summary.url == XWGG_URL
    assert result.title == DETAIL_TITLE
    assert result.kind == "article"
    assert result.published_at == date(2026, 9, 3)
    assert result.previous_url == "https://jmx.gduf.edu.cn/info/1093/3726.htm"
    assert result.next_url == "https://jmx.gduf.edu.cn/info/1093/3723.htm"
    # attachments link through download.jsp without a file extension
    assert result.attachments
    assert "wbfileid=15479501" in result.attachments[0]
    assert len(result.content_text) > 100


def test_jmx_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_jmx_detail("https://www.gduf.edu.cn/index.htm", client=client)


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (16, InvalidPageError)])
def test_jmx_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    with pytest.raises(exc):
        get_jmx_xwgg(page=page, client=client)


def test_jmx_has_no_search(client: GdufClient) -> None:
    with pytest.raises(ParseError):
        client.search("测试", source="jmx")
