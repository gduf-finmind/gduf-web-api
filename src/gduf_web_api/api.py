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
