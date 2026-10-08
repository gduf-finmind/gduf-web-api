"""Adapter for the School of Economics and Trade site (jmx.gduf.edu.cn)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gduf_web_api.adapters.vsb import MainArtVsbAdapter, row_jmx

if TYPE_CHECKING:
    from gduf_web_api.client import GdufClient

BASE_URL = "https://jmx.gduf.edu.cn/"
HOST = "jmx.gduf.edu.cn"


class JmxAdapter(MainArtVsbAdapter):
    """Parse the economics and trade school templates."""

    code = "jmx"

    def __init__(self, client: GdufClient) -> None:
        super().__init__(
            client,
            base_url=BASE_URL,
            host=HOST,
            # 学院概况/师资队伍 are column lists, not static pages
            article_paths={
                "xwgg": "index/xwgg.htm",
                "djhd": "index/djhd.htm",
                "jxhd": "index/jxhd.htm",
                "kyhd": "index/kyhd.htm",
                "ssfc": "index/ssfc.htm",
                "xyjj": "xygk/xyjj.htm",
                "szdw": "xygk/szdw.htm",
            },
            article_row_parser=row_jmx,
            content_paths={
                "jgsz": "xygk/jgsz.htm",
                "xrld": "xygk/xrld.htm",
            },
        )
