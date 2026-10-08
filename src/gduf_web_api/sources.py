"""Registry of known GDUF website sources and their availability status.

The availability status was established by probing every listed host
(reachability plus template inspection) on :data:`CHECKED_AT`. Sites whose
TLS handshake is dropped by their load balancer are marked ``unavailable``;
re-probe them before re-adding an adapter.
"""

from __future__ import annotations

from dataclasses import dataclass

from gduf_web_api.models import JsonModel

CHECKED_AT = "2026-10-01"

TLS_NOTE = "TLS 握手失败 (SSL: UNEXPECTED_EOF_WHILE_READING), 站点暂不可访问"
DSAI_NOTE = (
    f"新域名暂不可访问 ({TLS_NOTE}); 同一学院内容仍可通过 ai 来源 (ai.gduf.edu.cn) 获取"
)


@dataclass(frozen=True, slots=True)
class SourceInfo(JsonModel):
    """Metadata for one registered website source."""

    code: str
    name: str
    base_url: str
    status: str
    note: str | None = None
    checked_at: str = CHECKED_AT


SOURCES: tuple[SourceInfo, ...] = (
    SourceInfo("main", "学校官网", "https://www.gduf.edu.cn/", "available"),
    SourceInfo(
        "ai", "大数据与人工智能学院 (ai 域名)", "https://ai.gduf.edu.cn/", "available"
    ),
    SourceInfo("jrx", "金融与投资学院", "https://jrx.gduf.edu.cn/", "available"),
    SourceInfo("kjx", "会计学院", "https://kjx.gduf.edu.cn/", "available"),
    SourceInfo("bxx", "保险学院", "https://bxx.gduf.edu.cn/", "available"),
    SourceInfo("jmx", "经济贸易学院", "https://jmx.gduf.edu.cn/", "available"),
    SourceInfo("xygl", "信用管理学院", "https://xygl.gduf.edu.cn/", "available"),
    SourceInfo("gsgl", "工商管理学院", "https://gsgl.gduf.edu.cn/", "available"),
    SourceInfo(
        "jrsx", "金融数学与统计学院", "https://jrsx.gduf.edu.cn/", "available"
    ),
    SourceInfo("gjjrx", "国家金融学学院", "https://gjjrx.gduf.edu.cn/", "available"),
    SourceInfo(
        "dsai",
        "大数据与人工智能学院 (dsai 域名)",
        "https://dsai.gduf.edu.cn/",
        "unavailable",
        DSAI_NOTE,
    ),
    SourceInfo("xxgc", "计算机学院", "https://xxgc.gduf.edu.cn/", "available"),
    SourceInfo("fx", "法学院", "https://fx.gduf.edu.cn/", "unavailable", TLS_NOTE),
    SourceInfo("ggglxy", "公共管理学院", "https://ggglxy.gduf.edu.cn/", "unavailable", TLS_NOTE),
    SourceInfo("wyx", "外国语言与文化学院", "https://wyx.gduf.edu.cn/", "available"),
    SourceInfo("cjcm", "财经与新媒体学院", "https://cjcm.gduf.edu.cn/", "available"),
    SourceInfo(
        "mkszyxy", "马克思主义学院", "https://mkszyxy.gduf.edu.cn/", "unavailable", TLS_NOTE
    ),
    SourceInfo("gjjyxy", "国际教育学院", "https://gjjyxy.gduf.edu.cn/", "unavailable", TLS_NOTE),
    SourceInfo("jjxy", "继续教育学院", "https://jjxy.gduf.edu.cn/", "unavailable", TLS_NOTE),
)

_BY_CODE: dict[str, SourceInfo] = {source.code: source for source in SOURCES}


def list_sources() -> tuple[SourceInfo, ...]:
    """Return all registered sources, including unavailable ones."""

    return SOURCES


def get_source_info(code: str) -> SourceInfo:
    """Return the registry entry for ``code``.

    Raises:
        KeyError: when ``code`` is not a registered source.
    """

    return _BY_CODE[code]
