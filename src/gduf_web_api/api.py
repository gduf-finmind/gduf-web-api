"""Stable source-specific convenience functions."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from gduf_web_api.client import GdufClient
from gduf_web_api.models import (
    AiHome,
    ArticleSummary,
    ClubSummary,
    CompetitionDetail,
    CompetitionSummary,
    ContentDetail,
    ListResult,
    Notice,
    PageResult,
    PersonSummary,
    SiteHome,
)

R = TypeVar("R")


def _using(client: GdufClient | None, operation: Callable[[GdufClient], R]) -> R:
    if client is not None:
        return operation(client)
    with GdufClient() as owned:
        return operation(owned)


def get_ai_home(*, client: GdufClient | None = None) -> AiHome:
    def _home(active: GdufClient) -> AiHome:
        result = active.get_home("ai")
        assert isinstance(result, AiHome)
        return result

    return _using(client, _home)


def get_ai_xyxw(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    return _using(client, lambda active: active.get_articles("xyxw", page, source="ai"))


def get_ai_xshuhd(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    return _using(client, lambda active: active.get_articles("xshuhd", page, source="ai"))


def get_ai_xshenghd(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    return _using(client, lambda active: active.get_articles("xshenghd", page, source="ai"))


def get_ai_tzgg(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    return _using(client, lambda active: active.get_articles("tzgg", page, source="ai"))


def get_ai_xyld(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    return _using(client, lambda active: active.get_people("xyld", page, source="ai"))


def get_ai_zrjs(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    return _using(client, lambda active: active.get_people("zrjs", page, source="ai"))


def get_ai_jfry(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    return _using(client, lambda active: active.get_people("jfry", page, source="ai"))


def _content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="ai"))


def get_ai_xyjj(*, client: GdufClient | None = None) -> ContentDetail:
    return _content("xyjj", client)


def get_ai_jgsz(*, client: GdufClient | None = None) -> ContentDetail:
    return _content("jgsz", client)


def get_ai_jsjkxyjs(*, client: GdufClient | None = None) -> ContentDetail:
    return _content("jsjkxyjs", client)


def get_ai_rjgc(*, client: GdufClient | None = None) -> ContentDetail:
    return _content("rjgc", client)


def get_ai_sjkxydsjjs(*, client: GdufClient | None = None) -> ContentDetail:
    return _content("sjkxydsjjs", client)


def get_ai_yytjx(*, client: GdufClient | None = None) -> ContentDetail:
    return _content("yytjx", client)


def get_ai_rgzn(*, client: GdufClient | None = None) -> ContentDetail:
    return _content("rgzn", client)


def search_ai(
    keyword: str, page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    return _using(client, lambda active: active.search(keyword, page, source="ai"))


def get_ai_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    return _using(client, lambda active: active.get_detail(item_or_url, source="ai"))


def get_main_home(*, client: GdufClient | None = None) -> SiteHome:
    """Get the home page information blocks (广金要闻/广金公告/学术活动/媒体广金/院部新闻)."""

    def _home(active: GdufClient) -> SiteHome:
        result = active.get_home("main")
        assert isinstance(result, SiteHome)
        return result

    return _using(client, _home)


def get_main_gjyw(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 广金要闻 (university headline news)."""

    return _using(client, lambda active: active.get_articles("gjyw", page, source="main"))


def get_main_tzgg(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 广金公告 (university announcements)."""

    return _using(client, lambda active: active.get_articles("tzgg", page, source="main"))


def get_main_xshd(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 学术活动 (academic activities)."""

    return _using(client, lambda active: active.get_articles("xshd", page, source="main"))


def get_main_mtgj(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 媒体广金 (media coverage)."""

    return _using(client, lambda active: active.get_articles("mtgj", page, source="main"))


def get_main_ybxw(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 院部新闻 (college news)."""

    return _using(client, lambda active: active.get_articles("ybxw", page, source="main"))


def get_main_xrld(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 现任领导 (current university leaders, with role labels)."""

    return _using(client, lambda active: active.get_people("xrld", page, source="main"))


def _main_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="main"))


def get_main_gjjj(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 广金简介 (university profile)."""

    return _main_content("gjjj", client)


def get_main_gjyg(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 广金沿革 (university history)."""

    return _main_content("gjyg", client)


def get_main_gjjs(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 广金精神 (university spirit)."""

    return _main_content("gjjs", client)


def get_main_bxln(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 办学理念 (educational philosophy)."""

    return _main_content("bxln", client)


def get_main_jgsz(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 机构设置 (institutional setup)."""

    return _main_content("jgsz", client)


def search_main(
    keyword: str, page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Search the main university website."""

    return _using(client, lambda active: active.search(keyword, page, source="main"))


def get_main_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one main-site article or leader profile detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="main"))


def get_jrx_xwgg(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 新闻公告 (college news and notices)."""

    return _using(client, lambda active: active.get_articles("xwgg", page, source="jrx"))


def get_jrx_zrjs(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 专任教师 (full-time teaching staff)."""

    return _using(client, lambda active: active.get_people("zrjs", page, source="jrx"))


def get_jrx_jfry(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 教辅人员 (teaching support staff)."""

    return _using(client, lambda active: active.get_people("jfry", page, source="jrx"))


def _jrx_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="jrx"))


def get_jrx_xyjj(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 学院简介 (college profile)."""

    return _jrx_content("xyjj", client)


def get_jrx_jgsz(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 机构设置 (organizational structure)."""

    return _jrx_content("jgsz", client)


def get_jrx_kydt(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 科研动态 (research highlights)."""

    return _jrx_content("kydt", client)


def get_jrx_bsfc(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 博士风采 (faculty with doctoral degrees)."""

    return _jrx_content("bsfc", client)


def get_jrx_xyld(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 学院领导 (college leadership)."""

    return _jrx_content("xyld", client)


def search_jrx(
    keyword: str, page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Search the finance and investment college website."""

    return _using(client, lambda active: active.search(keyword, page, source="jrx"))


def get_jrx_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one jrx article or staff profile detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="jrx"))


def get_kjx_xxgg(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 信息公告 (information announcements)."""

    return _using(client, lambda active: active.get_articles("xxgg", page, source="kjx"))


def get_kjx_dthd(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 党团活动 (party and league activities)."""

    return _using(client, lambda active: active.get_articles("dthd", page, source="kjx"))


def get_kjx_jxgl(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 教学管理 (teaching management)."""

    return _using(client, lambda active: active.get_articles("jxgl", page, source="kjx"))


def get_kjx_kydt(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 科研动态 (research updates)."""

    return _using(client, lambda active: active.get_articles("kydt", page, source="kjx"))


def get_kjx_js(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 教授 (professors)."""

    return _using(client, lambda active: active.get_people("js", page, source="kjx"))


def get_kjx_fjs(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 副教授 (associate professors)."""

    return _using(client, lambda active: active.get_people("fjs", page, source="kjx"))


def get_kjx_xzry(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 行政人员 (administrative staff)."""

    return _using(client, lambda active: active.get_people("xzry", page, source="kjx"))


def _kjx_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="kjx"))


def get_kjx_xyjj(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 学院简介 (college profile)."""

    return _kjx_content("xyjj", client)


def get_kjx_szgk(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 师资概况 (faculty overview)."""

    return _kjx_content("szgk", client)


def get_kjx_xrld(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 现任领导 (current leadership)."""

    return _kjx_content("xrld", client)


def get_kjx_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one kjx article or teacher profile detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="kjx"))


def get_bxx_xwgg(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 新闻公告 (college news and notices)."""

    return _using(client, lambda active: active.get_articles("xwgg", page, source="bxx"))


def get_bxx_kydt(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 科研动态 (research updates)."""

    return _using(client, lambda active: active.get_articles("kydt", page, source="bxx"))


def get_bxx_xsjl(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 学术交流 (academic exchanges)."""

    return _using(client, lambda active: active.get_articles("xsjl", page, source="bxx"))


def get_bxx_xrld(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 现任领导 (current leadership)."""

    return _using(client, lambda active: active.get_people("xrld", page, source="bxx"))


def get_bxx_js(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 教授 (professors)."""

    return _using(client, lambda active: active.get_people("js", page, source="bxx"))


def get_bxx_fjs(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 副教授 (associate professors)."""

    return _using(client, lambda active: active.get_people("fjs", page, source="bxx"))


def _bxx_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="bxx"))


def get_bxx_xyjj(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 学院简介 (college profile)."""

    return _bxx_content("xyjj", client)


def get_bxx_szgk(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 师资概况 (faculty overview)."""

    return _bxx_content("szgk", client)


def get_bxx_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one bxx article or teacher profile detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="bxx"))


def get_cjcm_xyxw(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 学院新闻 (college news)."""

    return _using(client, lambda active: active.get_articles("xyxw", page, source="cjcm"))


def get_cjcm_tzgg(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 通知公告 (notices and announcements)."""

    return _using(client, lambda active: active.get_articles("tzgg", page, source="cjcm"))


def get_cjcm_jxdt(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 教学动态 (teaching updates)."""

    return _using(client, lambda active: active.get_articles("jxdt", page, source="cjcm"))


def get_cjcm_kydt(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 科研动态 (research updates)."""

    return _using(client, lambda active: active.get_articles("kydt", page, source="cjcm"))


def get_cjcm_xykj(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 校友空间 (alumni space)."""

    return _using(client, lambda active: active.get_articles("xykj", page, source="cjcm"))


def get_cjcm_wlyxmtx(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[PersonSummary]:
    """Get 网络与新媒体系 (network and new media department staff)."""

    return _using(client, lambda active: active.get_people("wlyxmtx", page, source="cjcm"))


def _cjcm_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="cjcm"))


def get_cjcm_xyjj(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 学院简介 (college profile)."""

    return _cjcm_content("xyjj", client)


def get_cjcm_szgk(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 师资概况 (faculty overview)."""

    return _cjcm_content("szgk", client)


def get_cjcm_xrld(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 现任领导 (current leadership)."""

    return _cjcm_content("xrld", client)


def get_cjcm_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one cjcm article or staff profile detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="cjcm"))


def get_gjjrx_xyxw(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 学院新闻 (college news)."""

    return _using(client, lambda active: active.get_articles("xyxw", page, source="gjjrx"))


def get_gjjrx_tzgg(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 通知公告 (notices and announcements)."""

    return _using(client, lambda active: active.get_articles("tzgg", page, source="gjjrx"))


def get_gjjrx_jxky(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 教学科研 (teaching and research news)."""

    return _using(client, lambda active: active.get_articles("jxky", page, source="gjjrx"))


def get_gjjrx_dtxg(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 党团学工 (party, league and student affairs news)."""

    return _using(client, lambda active: active.get_articles("dtxg", page, source="gjjrx"))


def get_gjjrx_gjzk(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 国金智库 (think tank articles)."""

    return _using(client, lambda active: active.get_articles("gjzk", page, source="gjjrx"))


def get_gjjrx_xrld(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 学院领导 (college leadership)."""

    return _using(client, lambda active: active.get_people("xrld", page, source="gjjrx"))


def get_gjjrx_zrjs(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 专任教师 (full-time teaching staff)."""

    return _using(client, lambda active: active.get_people("zrjs", page, source="gjjrx"))


def get_gjjrx_jfry(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 教辅人员 (teaching support staff)."""

    return _using(client, lambda active: active.get_people("jfry", page, source="gjjrx"))


def get_gjjrx_bsfc(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 博士风采 (faculty with doctoral degrees)."""

    return _using(client, lambda active: active.get_people("bsfc", page, source="gjjrx"))


def get_gjjrx_jsfc(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 教授风采 (professors)."""

    return _using(client, lambda active: active.get_people("jsfc", page, source="gjjrx"))


def _gjjrx_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="gjjrx"))


def get_gjjrx_xyjj(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 学院简介 (college profile)."""

    return _gjjrx_content("xyjj", client)


def get_gjjrx_jgsz(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 机构设置 (organizational structure)."""

    return _gjjrx_content("jgsz", client)


def get_gjjrx_szgk(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 师资概况 (faculty overview)."""

    return _gjjrx_content("szgk", client)


def search_gjjrx(
    keyword: str, page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Search the national finance school website."""

    return _using(client, lambda active: active.search(keyword, page, source="gjjrx"))


def get_gjjrx_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one gjjrx article or staff profile detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="gjjrx"))


def get_jmx_xwgg(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 新闻公告 (college news and notices)."""

    return _using(client, lambda active: active.get_articles("xwgg", page, source="jmx"))


def get_jmx_djhd(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 党建活动 (party building activities)."""

    return _using(client, lambda active: active.get_articles("djhd", page, source="jmx"))


def get_jmx_jxhd(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 教学活动 (teaching activities)."""

    return _using(client, lambda active: active.get_articles("jxhd", page, source="jmx"))


def get_jmx_kyhd(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 科研活动 (research activities)."""

    return _using(client, lambda active: active.get_articles("kyhd", page, source="jmx"))


def get_jmx_ssfc(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 硕士风采 (master's program showcase)."""

    return _using(client, lambda active: active.get_articles("ssfc", page, source="jmx"))


def get_jmx_xyjj(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 学院概况 column articles (college profile and recruitment)."""

    return _using(client, lambda active: active.get_articles("xyjj", page, source="jmx"))


def get_jmx_szdw(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 师资队伍 column articles (faculty group photos)."""

    return _using(client, lambda active: active.get_articles("szdw", page, source="jmx"))


def _jmx_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="jmx"))


def get_jmx_jgsz(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 机构设置 (organizational structure)."""

    return _jmx_content("jgsz", client)


def get_jmx_xrld(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 现任领导 (current leadership)."""

    return _jmx_content("xrld", client)


def get_jmx_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one jmx article detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="jmx"))


def get_gsgl_xwxx(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 新闻信息 (college news)."""

    return _using(client, lambda active: active.get_articles("xwxx", page, source="gsgl"))


def get_gsgl_jyhd(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 教研活动 (teaching and research activities)."""

    return _using(client, lambda active: active.get_articles("jyhd", page, source="gsgl"))


def get_gsgl_djhd(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 党建活动 (party building activities)."""

    return _using(client, lambda active: active.get_articles("djhd", page, source="gsgl"))


def get_gsgl_xshd(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 学生活动 (student activities)."""

    return _using(client, lambda active: active.get_articles("xshd", page, source="gsgl"))


def get_gsgl_js(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 教授 (professors)."""

    return _using(client, lambda active: active.get_people("js", page, source="gsgl"))


def get_gsgl_fjs(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 副教授 (associate professors)."""

    return _using(client, lambda active: active.get_people("fjs", page, source="gsgl"))


def get_gsgl_bs(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 博士 (faculty with doctoral degrees)."""

    return _using(client, lambda active: active.get_people("bs", page, source="gsgl"))


def _gsgl_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="gsgl"))


def get_gsgl_ykjj(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 学院概况 (college profile)."""

    return _gsgl_content("ykjj", client)


def get_gsgl_ldjs(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 领导介绍 (leadership)."""

    return _gsgl_content("ldjs", client)


def get_gsgl_szgk(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 师资概况 (faculty overview)."""

    return _gsgl_content("szgk", client)


def get_gsgl_glry(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 管理人员 (administrative staff)."""

    return _gsgl_content("glry", client)


def get_gsgl_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one gsgl article or staff profile detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="gsgl"))


def get_xxgc_xyxw(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 学院新闻 (college news)."""

    return _using(client, lambda active: active.get_articles("xyxw", page, source="xxgc"))


def get_xxgc_tzgg(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 通知公告 (notices and announcements)."""

    return _using(client, lambda active: active.get_articles("tzgg", page, source="xxgc"))


def get_xxgc_jxhd(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 教学活动 (teaching activities)."""

    return _using(client, lambda active: active.get_articles("jxhd", page, source="xxgc"))


def get_xxgc_jsml(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 教师名录 (teacher roster)."""

    return _using(client, lambda active: active.get_people("jsml", page, source="xxgc"))


def get_xxgc_jfry(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 教辅人员 (teaching support staff)."""

    return _using(client, lambda active: active.get_people("jfry", page, source="xxgc"))


def _xxgc_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="xxgc"))


def get_xxgc_xyjj(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 学院简介 (college profile)."""

    return _xxgc_content("xyjj", client)


def get_xxgc_ldjs(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 领导介绍 (leadership)."""

    return _xxgc_content("ldjs", client)


def get_xxgc_szgk(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 师资概况 (faculty overview)."""

    return _xxgc_content("szgk", client)


def get_xxgc_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one xxgc article or staff profile detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="xxgc"))


def get_xygl_zxzx(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 最新资讯 (latest updates)."""

    return _using(client, lambda active: active.get_articles("zxzx", page, source="xygl"))


def get_xygl_kydt(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 科研动态 (research updates)."""

    return _using(client, lambda active: active.get_articles("kydt", page, source="xygl"))


def get_xygl_msfc(
    page: int = 1, *, client: GdufClient | None = None
) -> PageResult[ArticleSummary]:
    """Get 名师风采 (distinguished teachers)."""

    return _using(client, lambda active: active.get_articles("msfc", page, source="xygl"))


def get_xygl_zrjs(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 专任教师 (full-time teaching staff)."""

    return _using(client, lambda active: active.get_people("zrjs", page, source="xygl"))


def _xygl_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="xygl"))


def get_xygl_xyjj(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 学院简介 (college profile)."""

    return _xygl_content("xyjj", client)


def get_xygl_szgk(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 师资概况 (faculty overview)."""

    return _xygl_content("szgk", client)


def get_xygl_xrld(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 现任领导 (current leadership)."""

    return _xygl_content("xrld", client)


def get_xygl_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one xygl article or teacher profile detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="xygl"))


def get_wyx_tzgg(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 通知公告 (notices and announcements)."""

    return _using(client, lambda active: active.get_articles("tzgg", page, source="wyx"))


def get_wyx_xyxw(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 学院新闻 (college news)."""

    return _using(client, lambda active: active.get_articles("xyxw", page, source="wyx"))


def get_wyx_djdt(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 党建动态 (party building updates)."""

    return _using(client, lambda active: active.get_articles("djdt", page, source="wyx"))


def get_wyx_kydt(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 科研动态 (research updates)."""

    return _using(client, lambda active: active.get_articles("kydt", page, source="wyx"))


def get_wyx_xgdt(page: int = 1, *, client: GdufClient | None = None) -> PageResult[ArticleSummary]:
    """Get 学工动态 (student affairs updates)."""

    return _using(client, lambda active: active.get_articles("xgdt", page, source="wyx"))


def get_wyx_js(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 教授 (professors)."""

    return _using(client, lambda active: active.get_people("js", page, source="wyx"))


def get_wyx_fjs(page: int = 1, *, client: GdufClient | None = None) -> PageResult[PersonSummary]:
    """Get 副教授 (associate professors)."""

    return _using(client, lambda active: active.get_people("fjs", page, source="wyx"))


def _wyx_content(category: str, client: GdufClient | None) -> ContentDetail:
    return _using(client, lambda active: active.get_content(category, source="wyx"))


def get_wyx_xyjj(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 学院简介 (college profile)."""

    return _wyx_content("xyjj", client)


def get_wyx_szgk(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 队伍概况 (faculty overview)."""

    return _wyx_content("szgk", client)


def get_wyx_xrld(*, client: GdufClient | None = None) -> ContentDetail:
    """Get 现任领导 (current leadership)."""

    return _wyx_content("xrld", client)


def get_wyx_detail(
    item_or_url: ArticleSummary | PersonSummary | str,
    *,
    client: GdufClient | None = None,
) -> ContentDetail:
    """Get one wyx article or teacher profile detail."""

    return _using(client, lambda active: active.get_detail(item_or_url, source="wyx"))


def get_aijspt_bslb(
    *,
    year: int | None = None,
    status: str | None = None,
    category: str | None = None,
    department: str | None = None,
    keyword: str | None = None,
    client: GdufClient | None = None,
) -> ListResult[CompetitionSummary]:
    """Get the competition list (比赛列表) with optional local filters."""

    return _using(
        client,
        lambda active: active.get_competitions(
            year=year,
            status=status,
            category=category,
            department=department,
            keyword=keyword,
            source="aijspt",
        ),
    )


def get_aijspt_bsxq(
    competition_or_id: CompetitionSummary | str,
    *,
    client: GdufClient | None = None,
) -> CompetitionDetail:
    """Get one competition's public detail (比赛详情)."""

    return _using(
        client,
        lambda active: active.get_competition_detail(competition_or_id, source="aijspt"),
    )


def get_aijspt_tzgg(limit: int = 20, *, client: GdufClient | None = None) -> ListResult[Notice]:
    """Get published platform notices (通知公告)."""

    return _using(client, lambda active: active.get_notices(limit, source="aijspt"))


def get_aijspt_stlb(*, client: GdufClient | None = None) -> ListResult[ClubSummary]:
    """Get the public student-club list (社团列表)."""

    return _using(client, lambda active: active.get_clubs(source="aijspt"))
