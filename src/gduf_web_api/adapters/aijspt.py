"""Adapter for the AI college competition and Q&A platform."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from time import monotonic
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urljoin, urlparse
from uuid import UUID

from bs4 import BeautifulSoup, Tag

from gduf_web_api.errors import ParseError
from gduf_web_api.models import (
    ClubSummary,
    CompetitionDetail,
    CompetitionFaq,
    CompetitionSummary,
    CompetitionTimelineItem,
    ListResult,
    Notice,
    ResourceLink,
)

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://ai-data-competitions.cn/"
_DETAIL_PATH_RE = re.compile(
    r"^/competitions/([0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})/?$"
)
_CLUB_PATH_RE = re.compile(r"^/clubs/([^/]+)/?$", re.IGNORECASE)


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.replace("\u200b", "").split())
    return cleaned or None


def _tag_text(tag: Tag) -> str | None:
    """Return text from regular markup and inert template payloads."""
    return _clean_text(" ".join(str(node) for node in tag.find_all(string=True)))


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not (cleaned := _clean_text(value)):
        raise ParseError(f"aijspt field {field!r} must be a non-empty string")
    return cleaned


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ParseError(f"aijspt field {field!r} must be a string or null")
    return _clean_text(value)


def _parse_datetime(value: Any, field: str, *, required: bool = False) -> datetime | None:
    if value is None and not required:
        return None
    if not isinstance(value, str):
        raise ParseError(f"aijspt field {field!r} must be an ISO datetime")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ParseError(f"invalid aijspt datetime in {field!r}: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ParseError(f"aijspt datetime in {field!r} must include a timezone")
    return parsed


def _absolute(page_url: str, value: str | None) -> str | None:
    if not value or value.lower().startswith(("javascript:", "data:")):
        return None
    return urljoin(page_url, value)


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


class AijsptAdapter:
    """读取竞赛平台公开服务端页面,为后端提供结构化比赛、通知和社团数据。"""

    code = "aijspt"

    def __init__(self, client: GdufClient) -> None:
        self._client = client
        self._competition_cache: tuple[tuple[CompetitionSummary, ...], str] | None = None
        self._competition_cached_at = 0.0

    @staticmethod
    def _page_soup(html: str) -> BeautifulSoup:
        """将服务端分段 HTML 拼回占位位置,返回可查询的页面树。

        只读取 Next.js 的片段搬运参数,不执行网页脚本;否则卡片页脚会与标题分离。
        """
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script"):
            for source_id, target_id in re.findall(
                r'\$RS\("(S:[\w]+)","(P:[\w]+)"\)', script.get_text()
            ):
                source = soup.find(id=source_id)
                target = soup.find(id=target_id)
                if isinstance(source, Tag) and isinstance(target, Tag):
                    for child in list(source.contents):
                        target.insert_before(child.extract())
                    target.decompose()
                    source.decompose()
        return soup

    @staticmethod
    def _notice_payload(soup: BeautifulSoup) -> list[Any]:
        """读取公开页面内嵌的通知数组,保留正文和关联赛事字段。

        合并分段 RSC 字符串后按 JSON 解码,避免跨片段、转义引号或换行截断正文。
        缺少数据时报告解析错误,不能把登录页或异常页误判成空列表。
        """
        chunks: list[str] = []
        decoder = json.JSONDecoder()
        for script in soup.find_all("script"):
            text = script.get_text().strip()
            prefix = "self.__next_f.push("
            if not text.startswith(prefix):
                continue
            try:
                value, _ = decoder.raw_decode(text[len(prefix) :])
            except json.JSONDecodeError:
                continue
            if (
                isinstance(value, list)
                and len(value) == 2
                and value[0] == 1
                and isinstance(value[1], str)
            ):
                chunks.append(value[1])
        stream = "".join(chunks)
        for match in re.finditer(r'"notices"\s*:\s*', stream):
            try:
                value, _ = decoder.raw_decode(stream[match.end() :])
            except json.JSONDecodeError:
                continue
            if isinstance(value, list):
                return value
        raise ParseError("aijspt public page is missing notices data")

    @staticmethod
    def _parse_card(card: Tag, competition_id: str) -> CompetitionSummary:
        """从公开比赛卡片提取展示字段,转换为客户端既有的比赛模型。

        页面日期采用北京时间;没有公开的限额与时间保持空值,避免伪造报名条件。
        """
        heading = card.select_one("[data-slot='card-title']")
        header = card.select_one("[data-slot='card-header']")
        content = card.select_one("[data-slot='card-content']")
        footer = card.select_one("[data-slot='card-footer']")
        if not all(isinstance(node, Tag) for node in (heading, header, content, footer)):
            raise ParseError("aijspt competition card is incomplete")
        badges = header.select("[data-slot='badge']")
        status_labels = {
            "草稿": "draft",
            "即将开始": "upcoming",
            "报名中": "registration_open",
            "进行中": "in_progress",
            "已结束": "finished",
            "往期比赛补录中": "previous_recording",
            "已归档": "archived",
        }
        recognition_labels = {
            "校内名单+全国名单": "school_and_national",
            "校内名单": "school_only",
            "全国名单": "national_only",
            "名单外": "unlisted",
        }
        status = _tag_text(badges[0]) if badges else None
        recognition = _tag_text(badges[1]) if len(badges) > 1 else None
        category = heading.find_previous_sibling()
        summary = content.find("p")
        spans = footer.select("span")
        year_match = re.search(r"\b(\d{4})\b", _tag_text(spans[0]) or "") if spans else None
        if (
            year_match is None
            or status not in status_labels
            or recognition not in recognition_labels
        ):
            raise ParseError("aijspt competition card metadata is invalid")
        date_label = next((p for p in content.find_all("p") if _tag_text(p) == "报名时间"), None)
        date_node = date_label.find_next_sibling("p") if date_label else None
        date_parts = (_tag_text(date_node) or "").split("至") if date_node else []
        parsed_dates: list[datetime | None] = []
        for value in date_parts:
            match = re.search(r"\d{4}/\d{2}/\d{2} \d{2}:\d{2}", value)
            try:
                parsed_dates.append(
                    datetime.strptime(match.group(), "%Y/%m/%d %H:%M").replace(
                        tzinfo=timezone(timedelta(hours=8))
                    )
                    if match
                    else None
                )
            except ValueError as exc:
                raise ParseError("aijspt competition registration date is invalid") from exc
        mode_label = next((p for p in content.find_all("p") if _tag_text(p) == "报名方式"), None)
        mode_node = mode_label.find_next_sibling("p") if mode_label else None
        mode = {"团队报名": "team", "个人报名": "individual"}.get(
            _tag_text(mode_node) if mode_node else None, ""
        )
        official = None
        wechat = None
        for anchor in card.select("a[href]"):
            href = str(anchor.get("href"))
            if "official-link" in href or _tag_text(anchor) == "官网报名":
                official = _absolute(BASE_URL, href)
            if urlparse(href).hostname == "mp.weixin.qq.com":
                wechat = href
        return CompetitionSummary(
            id=competition_id,
            title=_required_text(_tag_text(heading), "title"),
            url=urljoin(BASE_URL, f"competitions/{competition_id}"),
            category=_required_text(
                _tag_text(category) if isinstance(category, Tag) else None, "category"
            ),
            competition_year=int(year_match.group(1)),
            recognition=recognition_labels[recognition],
            status=status_labels[status],
            summary=_required_text(
                _tag_text(summary) if isinstance(summary, Tag) else None, "summary"
            ),
            department=_required_text(
                _tag_text(spans[1]) if len(spans) > 1 else None, "department"
            ),
            registration_mode=mode,
            max_team_size=None,
            max_advisors=None,
            registration_start_at=parsed_dates[0] if parsed_dates else None,
            registration_end_at=parsed_dates[1] if len(parsed_dates) > 1 else None,
            official_url=official,
            wechat_article_url=wechat,
        )

    def _all_competitions(self) -> tuple[tuple[CompetitionSummary, ...], str]:
        """遍历公开年份与分页链接并去重比赛,成功结果缓存五分钟。

        仅请求固定竞赛域名的列表路由。失败结果不缓存,避免长期隐藏上游恢复。
        """
        if self._competition_cache is not None and monotonic() - self._competition_cached_at < 300:
            return self._competition_cache
        source_url = urljoin(BASE_URL, "competitions")
        pending = [source_url]
        visited: set[str] = set()
        collected: dict[str, CompetitionSummary] = {}
        while pending:
            url = pending.pop(0)
            if url in visited:
                continue
            if len(visited) >= 100:
                raise ParseError("aijspt competition pagination exceeds 100 pages")
            visited.add(url)
            html, response_url = self._client._request_text("GET", url)
            soup = self._page_soup(html)
            page_items = 0
            for anchor in soup.select("a[href]"):
                parsed = urlparse(urljoin(source_url, str(anchor.get("href"))))
                if parsed.hostname != urlparse(BASE_URL).hostname:
                    continue
                match = _DETAIL_PATH_RE.fullmatch(parsed.path)
                if match:
                    card = anchor.find_parent(attrs={"data-slot": "card"})
                    if isinstance(card, Tag) and match.group(1) not in collected:
                        collected[match.group(1)] = self._parse_card(card, match.group(1))
                    if isinstance(card, Tag):
                        page_items += 1
                elif parsed.path == "/competitions" and parsed.query:
                    params = parse_qs(parsed.query)
                    if set(params) <= {"year", "page"} and all(
                        len(values) == 1 and values[0].isdigit() for values in params.values()
                    ):
                        page_url = (
                            urljoin(source_url, parsed.path)
                            + "?"
                            + "&".join(f"{key}={params[key][0]}" for key in sorted(params))
                        )
                        if page_url not in visited and page_url not in pending:
                            pending.append(page_url)
            if soup.find("h1") is None or "比赛列表" not in soup.find("h1").get_text():
                raise ParseError("aijspt competition list heading not found")
            if not page_items and not any(
                marker in soup.get_text()
                for marker in ("暂无比赛", "暂无符合", "没有找到", "共 0 场")
            ):
                raise ParseError("aijspt competition list contains no recognizable cards")
        items = tuple(collected.values())
        response_url = source_url
        self._competition_cache = (items, response_url)
        self._competition_cached_at = monotonic()
        return items, response_url

    def get_competitions(
        self,
        *,
        year: int | None = None,
        status: str | None = None,
        category: str | None = None,
        department: str | None = None,
        keyword: str | None = None,
    ) -> ListResult[CompetitionSummary]:
        if year is not None:
            _positive_int(year, "year")
        normalized_filters: dict[str, str] = {}
        for name, value in (
            ("status", status),
            ("category", category),
            ("department", department),
            ("keyword", keyword),
        ):
            if value is not None:
                if not isinstance(value, str) or not (cleaned := _clean_text(value)):
                    raise ValueError(f"{name} cannot be empty")
                normalized_filters[name] = cleaned

        items, source_url = self._all_competitions()
        selected: list[CompetitionSummary] = []
        for item in items:
            if year is not None and item.competition_year != year:
                continue
            if "status" in normalized_filters and item.status != normalized_filters["status"]:
                continue
            if "category" in normalized_filters and item.category != normalized_filters["category"]:
                continue
            if (
                "department" in normalized_filters
                and item.department != normalized_filters["department"]
            ):
                continue
            if "keyword" in normalized_filters:
                needle = normalized_filters["keyword"].casefold()
                if needle not in f"{item.title}\n{item.summary}".casefold():
                    continue
            selected.append(item)
        return ListResult(tuple(selected), len(selected), source_url)

    @staticmethod
    def _normalize_competition_id(
        competition_or_id: CompetitionSummary | str,
    ) -> tuple[str, CompetitionSummary | None]:
        if isinstance(competition_or_id, CompetitionSummary):
            if competition_or_id.source != "aijspt":
                raise ValueError("competition must belong to the aijspt source")
            return competition_or_id.id, competition_or_id
        if not isinstance(competition_or_id, str) or not competition_or_id.strip():
            raise ValueError("competition_or_id must be a competition, UUID, or detail URL")
        value = competition_or_id.strip()
        try:
            return str(UUID(value)), None
        except ValueError:
            pass
        parsed = urlparse(urljoin(BASE_URL, value))
        if parsed.scheme not in {"http", "https"} or parsed.hostname != "ai-data-competitions.cn":
            raise ValueError("competition detail URL must belong to ai-data-competitions.cn")
        match = _DETAIL_PATH_RE.fullmatch(parsed.path)
        if match is None:
            raise ValueError("competition detail URL must identify one competition")
        return str(UUID(match.group(1))), None

    def _find_competition(self, competition_id: str) -> CompetitionSummary:
        items, _ = self._all_competitions()
        for item in items:
            if item.id == competition_id:
                return item
        raise ValueError(f"unknown aijspt competition id: {competition_id}")

    @staticmethod
    def _clean_html(tag: Tag, page_url: str) -> tuple[str, str]:
        fragment_soup = BeautifulSoup(str(tag), "html.parser")
        fragment = fragment_soup.find()
        if not isinstance(fragment, Tag):
            raise ParseError("aijspt detail content could not be normalized")
        for unwanted in fragment.select("script, style, noscript"):
            unwanted.decompose()
        for node in fragment.find_all(True):
            for attribute in tuple(node.attrs):
                if attribute.lower().startswith("on") or attribute.lower() == "style":
                    del node.attrs[attribute]
            if node.name == "img":
                src = _absolute(page_url, str(node.get("src") or ""))
                if src:
                    node["src"] = src
                elif "src" in node.attrs:
                    del node.attrs["src"]
            elif node.name == "a":
                href = _absolute(page_url, str(node.get("href") or ""))
                if href:
                    node["href"] = href
                elif "href" in node.attrs:
                    del node.attrs["href"]
        return fragment.get_text("\n", strip=True), fragment.decode_contents(formatter="html")

    @staticmethod
    def _card(soup: BeautifulSoup, *titles: str) -> Tag | None:
        expected = set(titles)
        for title in soup.select("[data-slot='card-title']"):
            if _clean_text(title.get_text(" ", strip=True)) in expected:
                card = title.find_parent(attrs={"data-slot": "card"})
                if isinstance(card, Tag):
                    return card
        return None

    @classmethod
    def _timeline(cls, soup: BeautifulSoup) -> tuple[CompetitionTimelineItem, ...]:
        card = cls._card(soup, "时间安排")
        content = card.select_one("[data-slot='card-content']") if card else None
        if not isinstance(content, Tag):
            return ()
        items: list[CompetitionTimelineItem] = []
        for row in content.select(":scope > div"):
            children = [child for child in row.find_all(recursive=False) if isinstance(child, Tag)]
            if len(children) < 2:
                continue
            date_value = _clean_text(children[0].get_text(" ", strip=True))
            paragraphs = children[1].find_all("p")
            label = _clean_text(
                paragraphs[0].get_text(" ", strip=True)
                if paragraphs
                else children[1].get_text(" ", strip=True)
            )
            description = (
                _clean_text(paragraphs[1].get_text(" ", strip=True))
                if len(paragraphs) > 1
                else None
            )
            if date_value and label:
                items.append(CompetitionTimelineItem(date_value, label, description))
        return tuple(items)

    @classmethod
    def _faqs(cls, soup: BeautifulSoup) -> tuple[CompetitionFaq, ...]:
        card = cls._card(soup, "常见问题")
        if card is None:
            return ()
        items: list[CompetitionFaq] = []
        for row in card.select("[data-slot='accordion-item']"):
            question_node = row.select_one("[data-slot='accordion-trigger']")
            answer_node = row.select_one("[data-slot='accordion-content']")
            question = (
                _clean_text(question_node.get_text(" ", strip=True)) if question_node else None
            )
            answer = _clean_text(answer_node.get_text(" ", strip=True)) if answer_node else None
            if question and answer:
                items.append(CompetitionFaq(question, answer))
        return tuple(items)

    @classmethod
    def _links(cls, soup: BeautifulSoup, *titles: str) -> tuple[ResourceLink, ...]:
        card = cls._card(soup, *titles)
        if card is None:
            return ()
        links: list[ResourceLink] = []
        seen: set[str] = set()
        for anchor in card.select("[data-slot='card-content'] a[href]"):
            url = _absolute(BASE_URL, str(anchor.get("href")))
            title = _clean_text(str(anchor.get("title") or anchor.get_text(" ", strip=True)))
            if url and title and url not in seen:
                seen.add(url)
                links.append(ResourceLink(title, url))
        return tuple(links)

    @classmethod
    def _text_items(cls, soup: BeautifulSoup, *titles: str) -> tuple[str, ...]:
        card = cls._card(soup, *titles)
        if card is None:
            return ()
        content = card.select_one("[data-slot='card-content']")
        if not isinstance(content, Tag):
            return ()
        values: list[str] = []
        for node in content.select("li, [data-slot='badge']"):
            value = _clean_text(node.get_text(" ", strip=True))
            if value and value not in values:
                values.append(value)
        return tuple(values)

    def get_competition_detail(
        self, competition_or_id: CompetitionSummary | str
    ) -> CompetitionDetail:
        competition_id, supplied = self._normalize_competition_id(competition_or_id)
        competition = supplied or self._find_competition(competition_id)
        html, response_url = self._client._request_text("GET", competition.url)
        soup = self._page_soup(html)
        heading = soup.find("h1")
        if not isinstance(heading, Tag):
            raise ParseError("aijspt competition detail heading not found")
        title = _clean_text(heading.get_text(" ", strip=True))
        if title != competition.title:
            raise ParseError("aijspt competition detail does not match the requested competition")
        description = (
            heading.parent.select_one(".prose") if isinstance(heading.parent, Tag) else None
        )
        if not isinstance(description, Tag):
            description_soup = BeautifulSoup(
                f"<div><p>{competition.summary}</p></div>", "html.parser"
            )
            description = description_soup.div
        if not isinstance(description, Tag):
            raise ParseError("aijspt competition description not found")
        description_text, description_html = self._clean_html(description, response_url)

        location = None
        location_label = soup.find(string=lambda value: value and value.strip() == "地点与归属")
        if location_label and isinstance(location_label.parent, Tag):
            value_container = location_label.parent.parent
            if isinstance(value_container, Tag):
                paragraphs = value_container.find_all("p", recursive=False)
                if len(paragraphs) > 1:
                    combined = _clean_text(paragraphs[1].get_text(" ", strip=True))
                    if combined:
                        location = combined.rsplit("·", 1)[-1].strip()

        return CompetitionDetail(
            competition=competition,
            description_text=description_text,
            description_html=description_html,
            location=location,
            highlights=self._text_items(soup, "比赛亮点", "赛事亮点"),
            sub_tracks=self._text_items(soup, "子赛项", "子赛道"),
            timeline=self._timeline(soup),
            faqs=self._faqs(soup),
            attachments=self._links(soup, "附件", "相关附件", "比赛附件"),
            related_questions=self._links(soup, "问答讨论"),
            experience_articles=self._links(soup, "经验文章"),
        )

    def get_notices(self, limit: int = 20) -> ListResult[Notice]:
        _positive_int(limit, "limit")
        html, response_url = self._client._request_text("GET", urljoin(BASE_URL, "notifications"))
        raw_items = self._notice_payload(self._page_soup(html))[:limit]
        items: list[Notice] = []
        for value in raw_items:
            if not isinstance(value, dict):
                raise ParseError("aijspt notice entry must be an object")
            published_at = _parse_datetime(value.get("publishedAt"), "publishedAt", required=True)
            if published_at is None:
                raise ParseError("aijspt notice publishedAt is required")
            allow_popup = value.get("allowPopup")
            if not isinstance(allow_popup, bool):
                raise ParseError("aijspt field 'allowPopup' must be a boolean")
            # 验证正文非空后保留原始换行,避免通知段落在小程序弹层中合并。
            _required_text(value.get("content"), "content")
            items.append(
                Notice(
                    id=_required_text(value.get("id"), "id"),
                    competition_id=_optional_text(value.get("competitionId"), "competitionId"),
                    competition_title=_optional_text(
                        value.get("competitionTitle"), "competitionTitle"
                    ),
                    title=_required_text(value.get("title"), "title"),
                    content=value["content"].strip(),
                    priority=_required_text(value.get("priority"), "priority"),
                    delivery_scope=_required_text(value.get("deliveryScope"), "deliveryScope"),
                    allow_popup=allow_popup,
                    published_at=published_at,
                    expires_at=_parse_datetime(value.get("expiresAt"), "expiresAt"),
                    updated_at=_parse_datetime(value.get("updatedAt"), "updatedAt"),
                )
            )
        return ListResult(tuple(items), len(items), response_url)

    def get_clubs(self) -> ListResult[ClubSummary]:
        html, response_url = self._client._request_text("GET", urljoin(BASE_URL, "clubs"))
        soup = BeautifulSoup(html, "html.parser")
        container = soup.select_one("#clubs-overview")
        if container is None:
            raise ParseError("aijspt club overview not found")
        items: list[ClubSummary] = []
        seen: set[str] = set()
        # Next.js may stream some cards in template payloads outside #clubs-overview.
        # Scan the complete response and identify club cards by their detail URL.
        for card in soup.select("article"):
            heading = card.find("h3")
            paragraphs = card.find_all("p", recursive=False)
            badge = card.select_one("[data-slot='badge']")
            if not isinstance(heading, Tag) or len(paragraphs) < 2:
                continue

            url = None
            slug = None
            for anchor in card.find_all("a", href=True):
                candidate_url = _absolute(response_url, str(anchor.get("href")))
                if not candidate_url:
                    continue
                parsed = urlparse(candidate_url)
                match = _CLUB_PATH_RE.fullmatch(parsed.path)
                if parsed.hostname == urlparse(response_url).hostname and match:
                    url = candidate_url
                    slug = match.group(1)
                    break
            if url is None or slug is None or slug in seen:
                continue
            seen.add(slug)
            items.append(
                ClubSummary(
                    slug=slug,
                    name=_required_text(_tag_text(heading), "club.name"),
                    direction=_required_text(
                        _tag_text(badge) if isinstance(badge, Tag) else None, "club.direction"
                    ),
                    slogan=_required_text(_tag_text(paragraphs[0]), "club.slogan"),
                    description=_required_text(_tag_text(paragraphs[1]), "club.description"),
                    url=url,
                )
            )
        if not items:
            raise ParseError("aijspt club overview contains no clubs")
        return ListResult(tuple(items), len(items), response_url)
