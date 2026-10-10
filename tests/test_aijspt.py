from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest
from bs4 import BeautifulSoup

import gduf_web_api as api
from gduf_web_api import GdufClient, NetworkError, ParseError, UnsupportedSourceError
from gduf_web_api.adapters import aijspt


def test_competition_list_parses_all_snapshot_items(client: GdufClient) -> None:
    result = client.get_competitions()

    assert result.total_items == 14
    assert result.source_url == "https://ai-data-competitions.cn/competitions"
    first = result.items[0]
    assert first.title == "全国大学生机器人大赛-①RoboMaster"
    assert first.registration_start_at is None
    assert first.official_url == "https://www.robomaster.com/zh-CN"

    upcoming = result.items[1]
    assert upcoming.registration_start_at == datetime(
        2026, 11, 4, 5, 49, tzinfo=timezone(timedelta(hours=8))
    )
    assert upcoming.to_dict()["registration_start_at"] == "2026-11-04T05:49:00+08:00"
    assert upcoming.registration_mode == "team"
    assert upcoming.max_team_size is None
    assert upcoming.max_advisors is None


def test_competition_filters_are_combined_and_keep_order(client: GdufClient) -> None:
    all_items = client.get_competitions().items
    filtered = client.get_competitions(
        year=2026,
        status="registration_open",
        category="软件设计类",
        department="大数据与人工智能学院",
        keyword="创新人才",
    )

    assert [item.id for item in filtered.items] == [all_items[2].id]
    assert filtered.total_items == 1

    with pytest.raises(ValueError, match="positive integer"):
        client.get_competitions(year=True)
    with pytest.raises(ValueError, match="cannot be empty"):
        client.get_competitions(keyword="  ")
    with pytest.raises(UnsupportedSourceError):
        client.get_competitions(source="missing")


def test_competition_detail_accepts_all_supported_identifiers(client: GdufClient) -> None:
    competition = client.get_competitions(keyword="软件杯").items[0]
    identifiers = (
        competition,
        competition.id,
        f"/competitions/{competition.id}",
        competition.url,
    )

    for identifier in identifiers:
        detail = client.get_competition_detail(identifier)
        assert detail.id == competition.id
        assert detail.title == competition.title
        assert detail.location == "广州校区"
        assert detail.highlights == ("产教融合", "企业命题")
        assert detail.sub_tracks == ("A 组",)
        assert detail.timeline[1].label == "报名截止"
        assert detail.faqs[0].answer == "需要至少一位指导老师。"
        assert detail.attachments[0].url == "https://ai-data-competitions.cn/files/rules.pdf"
        assert detail.related_questions[0].title == "报名问题"
        assert detail.experience_articles[0].url == "https://example.edu/article"
        assert "script" not in detail.description_html
        assert "style=" not in detail.description_html
        assert "onmouseover" not in detail.description_html
        assert "onerror" not in detail.description_html
        assert "https://ai-data-competitions.cn/images/cup.png" in detail.description_html
        assert "https://ai-data-competitions.cn/rules" in detail.description_html


def test_competition_detail_rejects_invalid_or_unavailable_resources(
    client: GdufClient,
) -> None:
    for invalid in (
        "",
        "not-a-uuid",
        "https://example.com/competitions/3c3f766f-684f-46cb-b265-a686a9f3738b",
        "/competitions/3c3f766f-684f-46cb-b265-a686a9f3738b/apply",
    ):
        with pytest.raises(ValueError):
            client.get_competition_detail(invalid)

    with pytest.raises(NetworkError):
        client.get_competition_detail("e9cd546f-2e1f-4756-8f5b-5d3a5f5d7800")


def test_notices_and_limit_validation(client: GdufClient, request_log: list[httpx.Request]) -> None:
    result = client.get_notices(7)

    assert result.total_items == 1
    assert request_log[-1].url.path == "/notifications"
    notice = result.items[0]
    assert notice.competition_id is None
    assert notice.delivery_scope == "global"
    assert notice.published_at.tzinfo == timezone.utc
    assert notice.to_dict()["published_at"] == "2026-07-20T03:27:49.461000+00:00"

    for invalid in (0, -1, True):
        with pytest.raises(ValueError, match="positive integer"):
            client.get_notices(invalid)


def test_club_list_parses_five_public_cards(client: GdufClient) -> None:
    result = client.get_clubs()

    assert result.total_items == 5
    assert [club.slug for club in result.items] == [
        "quant-investment",
        "java-tribe",
        "ai-studio",
        "bricks-team",
        "acm-team",
    ]
    assert result.items[0].direction == "量化投资"
    assert result.items[-1].url == "https://ai-data-competitions.cn/clubs/acm-team"


def test_club_list_includes_nextjs_streamed_cards_outside_overview() -> None:
    def card(slug: str, name: str) -> str:
        return (
            f'<article><span data-slot="badge">{name}</span><h3>{name}</h3>'
            f"<p>{name} slogan</p><p>{name} club</p>"
            f'<a href="/clubs/{slug}">View</a></article>'
        )

    html = f"""
    <section id="clubs-overview">
      {card("java-tribe", "Java Tribe")}
      {card("ai-studio", "AI Studio")}
    </section>
    <template id="next-stream-1">
      {card("quant-investment", "Quant Studio")}
    </template>
    <template id="next-stream-2">
      {card("bricks-team", "Robotics Studio")}
      {card("acm-team", "ACM Team")}
    </template>
    <article><h3>News</h3><p>News</p><p>Ignore</p><a href="/news/1">View</a></article>
    """

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html, request=request)

    with GdufClient(transport=httpx.MockTransport(handler), retries=0) as streamed_client:
        result = streamed_client.get_clubs()

    assert result.total_items == 5
    assert [club.slug for club in result.items] == [
        "java-tribe",
        "ai-studio",
        "quant-investment",
        "bricks-team",
        "acm-team",
    ]


def test_aijspt_public_helpers_reuse_client(client: GdufClient) -> None:
    competitions = api.get_aijspt_bslb(status="registration_open", client=client)
    assert competitions.items
    assert api.get_aijspt_bsxq(competitions.items[0], client=client).timeline
    assert api.get_aijspt_tzgg(limit=1, client=client).items
    assert api.get_aijspt_stlb(client=client).items


def test_streamed_competitions_years_pagination_and_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """模拟卡片页脚分段、不同年份和下一页,验证去重与缓存到期重新请求。

    所有请求必须使用公开网页,旧 JSON 接口和页面内的外域链接均不可访问。
    """
    html = (Path(__file__).parent / "fixtures/aijspt_competitions.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("[data-slot='card']")
    duplicate = str(cards[0])
    footer = cards[0].select_one("[data-slot='card-footer']")
    footer_html = str(footer)
    footer.replace_with(BeautifulSoup('<template id="P:2"></template>', "html.parser"))
    first = (
        "<h1>比赛列表</h1>"
        + str(cards[0])
        + '<div hidden id="S:2">'
        + footer_html
        + '</div><script>$RS("S:2","P:2")</script>'
    )
    first += '<a href="/competitions?year=2025">2025</a><a href="/competitions?page=2">下一页</a><a href="https://example.com/competitions?page=2">外链</a>'
    older = str(cards[1]).replace("2026 年", "2025 年")
    paths: list[str] = []
    now = [100.0]
    monkeypatch.setattr(aijspt, "monotonic", lambda: now[0])

    def handler(request: httpx.Request) -> httpx.Response:
        """返回三页公开数据并记录请求,重复第一页比赛用于检查去重行为。"""
        assert request.url.host == "ai-data-competitions.cn"
        assert request.url.path == "/competitions"
        paths.append(str(request.url))
        body = (
            "<h1>比赛列表</h1>" + older
            if request.url.params.get("year")
            else "<h1>比赛列表</h1>" + duplicate + str(cards[2])
            if request.url.params.get("page")
            else first
        )
        return httpx.Response(200, text=body)

    with GdufClient(transport=httpx.MockTransport(handler), retries=0) as client:
        result = client.get_competitions()
        assert result.total_items == 3
        assert result.items[0].title == "全国大学生机器人大赛-①RoboMaster"
        assert client.get_competitions(year=2025).total_items == 1
        assert len(paths) == 3
        now[0] += 301
        assert client.get_competitions().total_items == 3
        assert len(paths) == 6


def test_notices_split_rsc_preserves_full_text_and_limit() -> None:
    """把通知 JSON 从正文中间分成两个脚本,验证转义字符、全文和本地限额。

    空数组是正常空态,没有有效 RSC 数组的页面必须抛出解析错误。
    """
    payload = json.loads(
        (Path(__file__).parent / "fixtures/aijspt_notices.json").read_text(encoding="utf-8")
    )
    notice = payload["notices"][0]
    notice["content"] = '完整正文"引号"\n' * 100
    payload["notices"] = [notice, {**notice, "id": "second"}]
    stream = "0:" + json.dumps(payload, ensure_ascii=False) + "\n"
    middle = stream.index("完整正文") + 3
    html = "".join(
        "<script>self.__next_f.push(" + json.dumps([1, chunk], ensure_ascii=False) + ")</script>"
        for chunk in (stream[:middle], stream[middle:])
    )
    with GdufClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, text=html)), retries=0
    ) as client:
        result = client.get_notices(1)
        assert result.total_items == 1
        assert result.items[0].content == notice["content"].strip()
    assert (
        aijspt.AijsptAdapter._notice_payload(
            BeautifulSoup(
                '<script>self.__next_f.push([1,"0:{\\"notices\\":[]}\\n"])</script>', "html.parser"
            )
        )
        == []
    )
    with pytest.raises(ParseError, match="missing notices"):
        aijspt.AijsptAdapter._notice_payload(BeautifulSoup("<h1>登录</h1>", "html.parser"))


def test_invalid_competition_page_is_not_cached() -> None:
    """异常页不可以变成成功空列表,上游恢复后同一客户端应能重新加载。"""
    responses = iter(["<h1>比赛列表</h1>", "<h1>比赛列表</h1><p>暂无比赛</p>"])
    with GdufClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, text=next(responses))),
        retries=0,
    ) as client:
        with pytest.raises(ParseError, match="no recognizable cards"):
            client.get_competitions()
        assert client.get_competitions().total_items == 0
