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
    if path == "/api/competitions":
        return httpx.Response(
            200,
            text=fixture_text("aijspt_competitions.json"),
            headers={"content-type": "application/json"},
            request=request,
        )
    if path == "/api/notices/published":
        return httpx.Response(
            200,
            text=fixture_text("aijspt_notices.json"),
            headers={"content-type": "application/json"},
            request=request,
        )
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
