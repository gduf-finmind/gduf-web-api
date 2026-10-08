"""Adapter for the School of Computer Science site (xxgc.gduf.edu.cn)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gduf_web_api.adapters.vsb import MainArtVsbAdapter, people_xxgc_card, row_kjx

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://xxgc.gduf.edu.cn/"
HOST = "xxgc.gduf.edu.cn"


class XxgcAdapter(MainArtVsbAdapter):
    """Parse the computer science school templates."""

    code = "xxgc"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={
                "xyxw": "index/xyxw.htm",
                "tzgg": "tzgg.htm",
                "jxhd": "index/jxhd.htm",
            },
            article_row_parser=row_kjx,
            people_paths={
                "jsml": "szdw/jsml.htm",
                "jfry": "szdw/jfry.htm",
            },
            people_row_parser=people_xxgc_card,
            content_paths={
                "xyjj": "xygk/xyjj.htm",
                "ldjs": "xygk/ldjs.htm",
                "szgk": "szdw/szgk.htm",
            },
        )
