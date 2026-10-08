from __future__ import annotations

import pytest

from gduf_web_api import SourceInfo, get_source_info, list_sources


def test_list_sources_covers_all_college_sites() -> None:
    codes = {source.code for source in list_sources()}
    expected = {
        "main",
        "ai",
        "dsai",
        "jrx",
        "kjx",
        "bxx",
        "jmx",
        "xygl",
        "gsgl",
        "jrsxy",
        "gjjrx",
        "jsjxy",
        "fx",
        "ggglxy",
        "wyx",
        "cjcm",
        "mkszyxy",
        "gjjyxy",
        "jjxy",
    }
    assert expected <= codes


def test_sources_have_unique_codes_and_valid_status() -> None:
    sources = list_sources()
    codes = [source.code for source in sources]
    assert len(codes) == len(set(codes))
    for source in sources:
        assert source.status in {"available", "unavailable"}
        assert source.base_url.startswith("https://")
        assert source.checked_at
        assert isinstance(source, SourceInfo)


def test_unavailable_sites_carry_a_note() -> None:
    for source in list_sources():
        if source.status == "unavailable":
            assert source.note


def test_get_source_info_roundtrip() -> None:
    source = get_source_info("jrx")
    assert source.base_url == "https://jrx.gduf.edu.cn/"
    assert source.status == "available"


def test_get_source_info_unknown_code() -> None:
    with pytest.raises(KeyError):
        get_source_info("nope")


def test_to_dict_is_json_compatible() -> None:
    import json

    payload = json.dumps(list_sources(), default=lambda value: value.to_dict())
    assert "jrx" in payload
