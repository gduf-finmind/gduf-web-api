"""Adapter for the School of Financial Mathematics and Statistics site (jrsx.gduf.edu.cn)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gduf_web_api.adapters.vsb import MainArtVsbAdapter, people_em_name, row_kjx

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://jrsx.gduf.edu.cn/"
HOST = "jrsx.gduf.edu.cn"


class JrsxAdapter(MainArtVsbAdapter):
    """Parse the financial mathematics and statistics school templates."""

    code = "jrsx"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={
                "xwxx": "index/xwxx.htm",
                "tzgg": "index/tzgg.htm",
                "msfc": "szdw/msfc.htm",
                "szgk": "szdw/szgk.htm",
            },
            article_row_parser=row_kjx,
            people_paths={
                "jsml": "szdw/jsml.htm",
                "ssds": "szdw/ssds.htm",
            },
            people_row_parser=people_em_name,
            content_paths={
                "xyjj": "xygk1/xyjj.htm",
                "xyld": "xygk1/xyld.htm",
            },
        )
