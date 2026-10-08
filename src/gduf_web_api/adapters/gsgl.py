"""Adapter for the School of Business Administration site (gsgl.gduf.edu.cn)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gduf_web_api.adapters.vsb import MainArtVsbAdapter, people_em_name, row_kjx

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://gsgl.gduf.edu.cn/"
HOST = "gsgl.gduf.edu.cn"


class GsglAdapter(MainArtVsbAdapter):
    """Parse the business administration school templates."""

    code = "gsgl"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            article_paths={
                "xwxx": "xwxx.htm",
                "jyhd": "jxky1/jyhd.htm",
                "djhd": "djgz/djhd.htm",
                "xshd": "xsgz/xshd.htm",
            },
            article_row_parser=row_kjx,
            people_paths={
                "js": "szdw/js.htm",
                "fjs": "szdw/fjs.htm",
                "bs": "szdw/bs.htm",
            },
            people_row_parser=people_em_name,
            content_paths={
                "ykjj": "xygk/ykjj.htm",
                "ldjs": "xygk/ldjs.htm",
                "szgk": "szdw/szgk.htm",
                "glry": "szdw/glry.htm",
            },
        )
