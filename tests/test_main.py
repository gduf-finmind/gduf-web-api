from __future__ import annotations

from datetime import date

import httpx
import pytest

from gduf_web_api import (
    GdufClient,
    InvalidPageError,
    get_main_detail,
    get_main_gjjj,
    get_main_gjyw,
    get_main_home,
    get_main_tzgg,
    get_main_xrld,
    search_main,
)


def test_main_home_sections(
    client: GdufClient,
    request_log: list[httpx.Request],
) -> None:
    home = get_main_home(client=client)
    assert request_log[-1].url.host == "www.gduf.edu.cn"
    categories = [section.category for section in home.sections]
    assert categories == ["gjyw", "tzgg", "xshd", "mtgj", "ybxw"]
    by_category = {section.category: section for section in home.sections}
    gjyw = by_category["gjyw"].items
    assert gjyw[0].title == "学校开展本科教育教学审核评估中期整改专项检查"
    assert gjyw[0].url == "https://www.gduf.edu.cn/info/1036/14944.htm"
    assert gjyw[0].published_at == date(2026, 9, 24)
    tzgg = by_category["tzgg"].items
    assert tzgg[0].url == "https://www.gduf.edu.cn/info/1040/14945.htm"
    assert tzgg[0].published_at == date(2026, 9, 24)
    assert len(gjyw) == 7
    assert len(tzgg) == 6
    assert [len(by_category[key].items) for key in ("xshd", "mtgj", "ybxw")] == [4, 4, 4]
    for section in home.sections:
        assert section.source == "main"


def test_main_gjyw_list(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_main_gjyw(client=client)
    assert request_log[-1].url.path == "/index/gjyw.htm"
    assert len(result.items) >= 10
    assert result.total_items >= 2000
    assert result.total_pages >= 2
    assert result.items[0].title == "我校举行升国旗仪式\uFF0C传承长征精神\uFF0C厚植爱国初心"
    assert result.items[0].url == "https://www.gduf.edu.cn/info/1036/14958.htm"
    assert result.items[0].published_at == date(2026, 9, 30)


def test_main_gjyw_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    get_main_gjyw(client=client)
    page2 = get_main_gjyw(page=2, client=client)
    assert request_log[-1].url.path == "/index/gjyw/136.htm"
    assert page2.items[0].url != get_main_gjyw(client=client).items[0].url


def test_main_tzgg_list(client: GdufClient) -> None:
    result = get_main_tzgg(client=client)
    assert len(result.items) >= 5
    assert result.items[0].url.endswith("/info/1040/14945.htm")


@pytest.mark.parametrize(("page", "exc"), [(0, InvalidPageError), (999, InvalidPageError)])
def test_main_invalid_page(client: GdufClient, page: int, exc: type[Exception]) -> None:
    get_main_gjyw(client=client)
    with pytest.raises(exc):
        get_main_gjyw(page=page, client=client)


def test_main_leaders(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_main_xrld(client=client)
    assert request_log[-1].url.path == "/xygk/xrld.htm"
    names = [person.name for person in result.items]
    assert "易行健" in names
    assert "刘春阳" in names
    assert "刘绍武" in names
    by_name = {person.name: person for person in result.items}
    assert by_name["刘春阳"].role == "党委副书记"
    assert by_name["刘绍武"].role == "纪委书记"
    assert by_name["刘锋"].role == "副院长"
    assert by_name["黄琼"].role == "副院长"


def test_main_static_content(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = get_main_gjjj(client=client)
    assert request_log[-1].url.path == "/xygk/gjjj.htm"
    assert result.title == "广金简介"
    assert result.kind == "static"
    assert "广东金融学院是一所省属公办普通本科院校" in result.content_text
    assert "script" not in result.content_html


def test_main_detail_from_url(client: GdufClient) -> None:
    result = get_main_detail("info/1036/14944.htm", client=client)
    assert result.title == "学校开展本科教育教学审核评估中期整改专项检查"
    assert result.url == "https://www.gduf.edu.cn/info/1036/14944.htm"
    assert result.kind == "article"
    assert len(result.content_text) > 100
    assert result.source == "main"


def test_main_detail_from_summary(client: GdufClient) -> None:
    summary = get_main_gjyw(client=client).items[0]
    result = get_main_detail(summary, client=client)
    assert result.url == summary.url


def test_main_detail_rejects_external_url(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        get_main_detail("https://example.com/info/1036/14944.htm", client=client)


def test_main_search(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = search_main("测试", client=client)
    assert request_log[-1].url.path == "/search.jsp"
    assert request_log[-1].method == "POST"
    assert len(result.items) >= 5
    assert result.total_items == 82
    assert result.total_pages == 6
    assert result.items[0].url == "https://www.gduf.edu.cn/info/1040/14945.htm"
    assert result.items[0].published_at == date(2026, 9, 24)
    assert result.items[6].url == "https://www.gduf.edu.cn/info/1036/14469.htm"


def test_main_search_second_page(client: GdufClient, request_log: list[httpx.Request]) -> None:
    search_main("测试", client=client)
    page2 = search_main("测试", page=2, client=client)
    assert request_log[-1].url.path == "/search.jsp"
    assert request_log[-1].url.params["currentnum"] == "2"
    assert page2.items[0].url != search_main("测试", client=client).items[0].url


def test_main_search_empty_keyword(client: GdufClient) -> None:
    with pytest.raises(ValueError):
        search_main("   ", client=client)


def test_main_search_out_of_range(client: GdufClient) -> None:
    search_main("测试", client=client)
    with pytest.raises(InvalidPageError):
        search_main("测试", page=99, client=client)
