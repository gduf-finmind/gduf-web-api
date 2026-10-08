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
    get_gsgl_bs,
    get_gsgl_detail,
    get_gsgl_djhd,
    get_gsgl_fjs,
    get_gsgl_glry,
    get_gsgl_js,
    get_gsgl_jyhd,
    get_gsgl_ldjs,
    get_gsgl_szgk,
    get_gsgl_xshd,
    get_gsgl_xwxx,
    get_gsgl_ykjj,
)

XWXX_TITLE = "一起向未来\uFF01 | 广金工管2026年招生宣传"
XWXX_URL = "https://gsgl.gduf.edu.cn/info/1055/3333.htm"
JYHD_TITLE = "工商管理学院举办“融合与创新\uFF1A国家自然科学基金申报交流会”"
JYHD_URL = "https://gsgl.gduf.edu.cn/info/1190/3493.htm"


def test_gsgl_xwxx_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_gsgl_xwxx(client=client)
    assert request_log[-1].url.host == "gsgl.gduf.edu.cn"
    assert request_log[-1].url.path == "/xwxx.htm"
    assert len(result.items) == 16
    assert result.total_items == 201
    assert result.total_pages == 13
    first = result.items[0]
    assert first.title == XWXX_TITLE
    assert first.url == XWXX_URL
    assert first.published_at == date(2026, 4, 28)


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages"),
    [
        (get_gsgl_jyhd, "/jxky1/jyhd.htm", 54, 4),
        (get_gsgl_djhd, "/djgz/djhd.htm", 36, 3),
        (get_gsgl_xshd, "/xsgz/xshd.htm", 80, 5),
    ],
)
def test_gsgl_article_columns(
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


def test_gsgl_jyhd_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    page1 = get_gsgl_jyhd(client=client)
    page2 = get_gsgl_jyhd(page=2, client=client)
    assert request_log[-1].url.path == "/jxky1/jyhd/3.htm"
    assert page2.items[0].url != page1.items[0].url
    assert page2.items[0].url == "https://gsgl.gduf.edu.cn/info/1190/3464.htm"
    assert page2.items[0].published_at == date(2026, 6, 14)


@pytest.mark.parametrize(
    ("fetch", "path", "total_items", "total_pages", "first_name", "first_url"),
    [
        (get_gsgl_js, "/szdw/js.htm", 8, 1, "周国林", "https://gsgl.gduf.edu.cn/info/1103/2684.htm"),
        (get_gsgl_fjs, "/szdw/fjs.htm", 30, 2, "程雪莲", "https://gsgl.gduf.edu.cn/info/1104/3053.htm"),
        (get_gsgl_bs, "/szdw/bs.htm", 53, 4, "梁翎", "https://gsgl.gduf.edu.cn/info/1166/2553.htm"),
    ],
)
def test_gsgl_people_columns(
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
        (get_gsgl_ykjj, "/xygk/ykjj.htm", "学院简介"),
        (get_gsgl_ldjs, "/xygk/ldjs.htm", "现任领导"),
        (get_gsgl_szgk, "/szdw/szgk.htm", "师资概况"),
        (get_gsgl_glry, "/szdw/glry.htm", "学生管理人员"),
    ],
)
def test_gsgl_static_content(
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
    assert result.source == "gsgl"


def test_gsgl_detail_from_summary(client: GdufClient) -> None:
    summary = get_gsgl_jyhd(client=client).items[0]
    result = get_gsgl_detail(summary, client=client)
    assert result.url == summary.url == JYHD_URL
    assert result.title == JYHD_TITLE
    assert result.kind == "article"
    assert result.published_at == date(2026, 9, 16)
    assert result.attribution is None
    assert result.previous_url is None
    assert result.next_url == "https://gsgl.gduf.edu.cn/info/1190/3481.htm"
    assert len(result.content_text) > 100


def test_gsgl_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_gsgl_detail("https://www.gduf.edu.cn/index.htm", client=client)


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (14, InvalidPageError)])
def test_gsgl_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    with pytest.raises(exc):
        get_gsgl_xwxx(page=page, client=client)


def test_gsgl_has_no_search(client: GdufClient) -> None:
    with pytest.raises(ParseError):
        client.search("测试", source="gsgl")
