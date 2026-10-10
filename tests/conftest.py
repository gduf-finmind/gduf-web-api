from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest

from gduf_web_api import GdufClient

FIXTURES = Path(__file__).parent / "fixtures"


def fixture_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def html_response(name: str, request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        text=fixture_text(name),
        headers={"content-type": "text/html; charset=utf-8"},
        request=request,
    )


@pytest.fixture
def request_log() -> list[httpx.Request]:
    return []


def main_site_response(request: httpx.Request, path: str) -> httpx.Response:
    if path == "/search.jsp":
        if request.method == "POST":
            return html_response("main_search_p1.html", request)
        current = request.url.params.get("currentnum")
        return html_response(
            "main_search_p2.html" if current == "2" else "main_search_p1.html", request
        )
    if path == "/":
        return html_response("main_home.html", request)
    if path == "/index/gjyw.htm":
        return html_response("main_gjyw.html", request)
    if path in {"/index/gjyw/2.htm", "/index/gjyw/136.htm"}:
        return html_response("main_gjyw_p2.html", request)
    if path in {"/index/gjgg1.htm", "/index/xshd.htm", "/index/mtgj.htm", "/index/ybxw.htm"}:
        return html_response("main_tzgg.html", request)
    if path == "/xygk/xrld.htm":
        return html_response("main_xrld.html", request)
    if path.startswith("/xygk/") and path.endswith(".htm"):
        return html_response("main_gjjj.html", request)
    if path.startswith("/info/"):
        return html_response("main_detail.html", request)
    return httpx.Response(404, request=request)


def jrx_site_response(request: httpx.Request, path: str) -> httpx.Response:
    if path == "/search.jsp":
        if request.method == "POST":
            return html_response("jrx_search_p1.html", request)
        current = request.url.params.get("currentnum")
        return html_response(
            "jrx_search_p2.html" if current == "2" else "jrx_search_p1.html", request
        )
    pages = {
        "/xwgg.htm": "jrx_xwgg.html",
        "/xwgg/64.htm": "jrx_xwgg_p2.html",
        "/szdw/zrjs.htm": "jrx_zrjs.html",
        "/szdw/jfry.htm": "jrx_jfry.html",
        "/xygk/xyjj.htm": "jrx_xyjj.html",
        "/xygk/jgsz.htm": "jrx_jgsz.html",
        "/kydt/kydt.htm": "jrx_kydt.html",
        "/szdw/bsfc.htm": "jrx_bsfc.html",
        "/xygk/xyld.htm": "jrx_xyld.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("jrx_detail.html", request)
    return httpx.Response(404, request=request)


def kjx_site_response(request: httpx.Request, path: str) -> httpx.Response:
    pages = {
        "/index/xxgg.htm": "kjx_xxgg.html",
        "/index/xxgg/22.htm": "kjx_xxgg_p2.html",
        "/dtjs/dthd.htm": "kjx_dthd.html",
        "/zyjx/jxgl.htm": "kjx_jxgl.html",
        "/kxyj/kydt.htm": "kjx_kydt.html",
        "/szdw/js.htm": "kjx_js.html",
        "/szdw/js/2.htm": "kjx_js_p2.html",
        "/szdw/fjs.htm": "kjx_fjs.html",
        "/szdw/xzry.htm": "kjx_xzry.html",
        "/yxgk/xyjj.htm": "kjx_xyjj.html",
        "/szdw/szgk.htm": "kjx_szgk.html",
        "/yxgk/xrld.htm": "kjx_xrld.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("kjx_detail.html", request)
    return httpx.Response(404, request=request)


def bxx_site_response(request: httpx.Request, path: str) -> httpx.Response:
    pages = {
        "/xwgg.htm": "bxx_xwgg.html",
        "/xwgg/14.htm": "bxx_xwgg_p2.html",
        "/kxyj/kydt.htm": "bxx_kydt.html",
        "/kxyj/xsjl.htm": "bxx_xsjl.html",
        "/xygk1/xrld.htm": "bxx_xrld.html",
        "/szdw/jsml/js.htm": "bxx_js.html",
        "/szdw/jsml/fjs.htm": "bxx_fjs.html",
        "/xygk1/xyjj.htm": "bxx_xyjj.html",
        "/szdw/szgk.htm": "bxx_szgk.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("bxx_detail.html", request)
    return httpx.Response(404, request=request)


def xygl_site_response(request: httpx.Request, path: str) -> httpx.Response:
    pages = {
        "/index/zxzx.htm": "xygl_zxzx.html",
        "/index/zxzx/13.htm": "xygl_zxzx_p2.html",
        "/xsky/kydt.htm": "xygl_kydt.html",
        "/index/msfc.htm": "xygl_msfc.html",
        "/szdw/zrjs.htm": "xygl_zrjs.html",
        "/xygk/xyjj.htm": "xygl_xyjj.html",
        "/szdw/szgk.htm": "xygl_szgk.html",
        "/xygk/xrld.htm": "xygl_xrld.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("xygl_detail.html", request)
    return httpx.Response(404, request=request)


def wyx_site_response(request: httpx.Request, path: str) -> httpx.Response:
    pages = {
        "/tzgg.htm": "wyx_tzgg.html",
        "/tzgg/1.htm": "wyx_tzgg_p2.html",
        "/xyxw.htm": "wyx_xyxw.html",
        "/dqgz/djdt.htm": "wyx_djdt.html",
        "/xsky/kydt.htm": "wyx_kydt.html",
        "/xszc/xgdt.htm": "wyx_xgdt.html",
        "/szll/js.htm": "wyx_js.html",
        "/szll/fjs.htm": "wyx_fjs.html",
        "/xygk/xyjj.htm": "wyx_xyjj.html",
        "/szll/dwgk.htm": "wyx_szgk.html",
        "/xygk/xrld.htm": "wyx_xrld.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("wyx_detail.html", request)
    return httpx.Response(404, request=request)


def cjcm_site_response(request: httpx.Request, path: str) -> httpx.Response:
    pages = {
        "/xyxw.htm": "cjcm_xyxw.html",
        "/xyxw/14.htm": "cjcm_xyxw_p2.html",
        "/tzgg.htm": "cjcm_tzgg.html",
        "/jxgz/jxdt.htm": "cjcm_jxdt.html",
        "/xsky/kydt.htm": "cjcm_kydt.html",
        "/xykj.htm": "cjcm_xykj.html",
        "/szdw/wlyxmtx.htm": "cjcm_wlyxmtx.html",
        "/xygk/xyjj.htm": "cjcm_xyjj.html",
        "/szdw/szgk.htm": "cjcm_szgk.html",
        "/xygk/xrld.htm": "cjcm_xrld.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("cjcm_detail.html", request)
    return httpx.Response(404, request=request)


def gjjrx_site_response(request: httpx.Request, path: str) -> httpx.Response:
    if path == "/search.jsp":
        if request.method == "POST":
            return html_response("gjjrx_search_p1.html", request)
        current = request.url.params.get("currentnum")
        return html_response(
            "gjjrx_search_p2.html" if current == "2" else "gjjrx_search_p1.html", request
        )
    pages = {
        "/xwzx/xyxw.htm": "gjjrx_xyxw.html",
        "/xwzx/xyxw/10.htm": "gjjrx_xyxw_p2.html",
        "/xwzx/tzgg.htm": "gjjrx_tzgg.html",
        "/xwzx/jxky.htm": "gjjrx_jxky.html",
        "/xwzx/dtxg.htm": "gjjrx_dtxg.html",
        "/xwzx/gjzk.htm": "gjjrx_gjzk.html",
        "/szdw/zrjs.htm": "gjjrx_zrjs.html",
        "/szdw/zrjs/2.htm": "gjjrx_zrjs_p2.html",
        "/szdw/jfry.htm": "gjjrx_jfry.html",
        "/szdw/bsfc.htm": "gjjrx_bsfc.html",
        "/szdw/jsfc.htm": "gjjrx_jsfc.html",
        "/xygk/xyld.htm": "gjjrx_xrld.html",
        "/xygk/xyjj.htm": "gjjrx_xyjj.html",
        "/xygk/jgsz.htm": "gjjrx_jgsz.html",
        "/szdw/szgk.htm": "gjjrx_szgk.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("gjjrx_detail.html", request)
    return httpx.Response(404, request=request)


def jmx_site_response(request: httpx.Request, path: str) -> httpx.Response:
    pages = {
        "/index/xwgg.htm": "jmx_xwgg.html",
        "/index/xwgg/14.htm": "jmx_xwgg_p2.html",
        "/index/djhd.htm": "jmx_djhd.html",
        "/index/jxhd.htm": "jmx_jxhd.html",
        "/index/kyhd.htm": "jmx_kyhd.html",
        "/index/ssfc.htm": "jmx_ssfc.html",
        "/xygk/xyjj.htm": "jmx_xyjj.html",
        "/xygk/szdw.htm": "jmx_szdw.html",
        "/xygk/jgsz.htm": "jmx_jgsz.html",
        "/xygk/xrld.htm": "jmx_xrld.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("jmx_detail.html", request)
    return httpx.Response(404, request=request)


def gsgl_site_response(request: httpx.Request, path: str) -> httpx.Response:
    pages = {
        "/xwxx.htm": "gsgl_xwxx.html",
        "/jxky1/jyhd.htm": "gsgl_jyhd.html",
        "/jxky1/jyhd/3.htm": "gsgl_jyhd_p2.html",
        "/djgz/djhd.htm": "gsgl_djhd.html",
        "/xsgz/xshd.htm": "gsgl_xshd.html",
        "/szdw/js.htm": "gsgl_js.html",
        "/szdw/fjs.htm": "gsgl_fjs.html",
        "/szdw/bs.htm": "gsgl_bs.html",
        "/szdw/glry.htm": "gsgl_glry.html",
        "/szdw/szgk.htm": "gsgl_szgk.html",
        "/xygk/ykjj.htm": "gsgl_ykjj.html",
        "/xygk/ldjs.htm": "gsgl_ldjs.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("gsgl_detail.html", request)
    return httpx.Response(404, request=request)


def xxgc_site_response(request: httpx.Request, path: str) -> httpx.Response:
    pages = {
        "/index/xyxw.htm": "xxgc_xyxw.html",
        "/index/xyxw/21.htm": "xxgc_xyxw_p2.html",
        "/tzgg.htm": "xxgc_tzgg.html",
        "/index/jxhd.htm": "xxgc_jxhd.html",
        "/szdw/jsml.htm": "xxgc_jsml.html",
        "/szdw/jfry.htm": "xxgc_jfry.html",
        "/szdw/szgk.htm": "xxgc_szgk.html",
        "/xygk/xyjj.htm": "xxgc_xyjj.html",
        "/xygk/ldjs.htm": "xxgc_ldjs.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("xxgc_detail.html", request)
    return httpx.Response(404, request=request)


def jrsx_site_response(request: httpx.Request, path: str) -> httpx.Response:
    pages = {
        "/index/xwxx.htm": "jrsx_xwxx.html",
        "/index/xwxx/25.htm": "jrsx_xwxx_p2.html",
        "/index/tzgg.htm": "jrsx_tzgg.html",
        "/szdw/msfc.htm": "jrsx_msfc.html",
        "/szdw/szgk.htm": "jrsx_szgk.html",
        "/szdw/jsml.htm": "jrsx_jsml.html",
        "/szdw/ssds.htm": "jrsx_ssds.html",
        "/xygk1/xyjj.htm": "jrsx_xyjj.html",
        "/xygk1/xyld.htm": "jrsx_xyld.html",
    }
    if path in pages:
        return html_response(pages[path], request)
    if path.startswith("/info/"):
        return html_response("jrsx_detail.html", request)
    return httpx.Response(404, request=request)


def ai_site_response(
    request: httpx.Request,
    path: str,
    article_roots: set[str],
    content_paths: set[str],
) -> httpx.Response:
    if request.method == "POST" and path == "/search.jsp":
        return html_response("search.html", request)
    if path == "/":
        name = "home.html"
    elif path in article_roots:
        name = "article_list_first.html"
    elif re_page_path(path):
        name = "article_list_middle.html"
    elif path == "/xygk/xyld.htm":
        name = "leader_list.html"
    elif path in {"/xygk/zrjs.htm", "/xygk/jfry.htm"}:
        name = "staff_list.html"
    elif path in content_paths:
        name = "static_content.html"
    elif path.startswith("/info/"):
        name = "detail.html"
    else:
        return httpx.Response(404, request=request)
    return html_response(name, request)


def aijspt_response(request: httpx.Request, path: str) -> httpx.Response:
    if path == "/competitions":
        return html_response("aijspt_competitions.html", request)
    if path == "/notifications":
        return html_response("aijspt_notifications.html", request)
    if path == "/clubs":
        return html_response("aijspt_clubs.html", request)
    if path == "/competitions/3c3f766f-684f-46cb-b265-a686a9f3738b":
        return html_response("aijspt_detail.html", request)
    return httpx.Response(404, request=request)


@pytest.fixture
def transport(request_log: list[httpx.Request]) -> httpx.MockTransport:
    article_roots = {"/jxky/xyxw.htm", "/xshd1.htm", "/xshd.htm", "/tzgg.htm"}
    content_paths = {
        "/xygk/xyjj.htm",
        "/xygk/jgsz.htm",
        "/zyjx/jsjkxyjs.htm",
        "/zyjx/rjgc.htm",
        "/zyjx/sjkxydsjjs.htm",
        "/zyjx/yytjx.htm",
        "/zyjx/rgzn.htm",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        request_log.append(request)
        path = request.url.path
        if request.url.host == "www.gduf.edu.cn":
            return main_site_response(request, path)
        if request.url.host == "jrx.gduf.edu.cn":
            return jrx_site_response(request, path)
        if request.url.host == "kjx.gduf.edu.cn":
            return kjx_site_response(request, path)
        if request.url.host == "bxx.gduf.edu.cn":
            return bxx_site_response(request, path)
        if request.url.host == "xygl.gduf.edu.cn":
            return xygl_site_response(request, path)
        if request.url.host == "wyx.gduf.edu.cn":
            return wyx_site_response(request, path)
        if request.url.host == "cjcm.gduf.edu.cn":
            return cjcm_site_response(request, path)
        if request.url.host == "gjjrx.gduf.edu.cn":
            return gjjrx_site_response(request, path)
        if request.url.host == "jmx.gduf.edu.cn":
            return jmx_site_response(request, path)
        if request.url.host == "gsgl.gduf.edu.cn":
            return gsgl_site_response(request, path)
        if request.url.host == "xxgc.gduf.edu.cn":
            return xxgc_site_response(request, path)
        if request.url.host == "jrsx.gduf.edu.cn":
            return jrsx_site_response(request, path)
        if request.url.host == "ai-data-competitions.cn":
            return aijspt_response(request, path)
        if request.url.host == "ai.gduf.edu.cn":
            return ai_site_response(request, path, article_roots, content_paths)
        return httpx.Response(404, request=request)

    return httpx.MockTransport(handler)


def re_page_path(path: str) -> bool:
    return path.endswith("/2.htm") and not path.startswith("/info/")


@pytest.fixture
def client(transport: httpx.MockTransport) -> Iterator[GdufClient]:
    with GdufClient(transport=transport, retries=0) as active:
        yield active
