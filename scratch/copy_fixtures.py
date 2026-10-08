"""Copy probed pages into tests/fixtures with canonical fixture names."""

from __future__ import annotations

import shutil
from pathlib import Path

PROBED = Path("scratch/probed")
FIXTURES = Path("tests/fixtures")

COPY: dict[str, str] = {
    # gjjrx
    "gjjrx_xwzx_xyxw.htm.html": "gjjrx_xyxw.html",
    "gjjrx_xwzx_tzgg.htm.html": "gjjrx_tzgg.html",
    "gjjrx_xwzx_jxky.htm.html": "gjjrx_jxky.html",
    "gjjrx_xwzx_dtxg.htm.html": "gjjrx_dtxg.html",
    "gjjrx_xwzx_gjzk.htm.html": "gjjrx_gjzk.html",
    "gjjrx_szdw_zrjs.htm.html": "gjjrx_zrjs.html",
    "gjjrx_szdw_jfry.htm.html": "gjjrx_jfry.html",
    "gjjrx_szdw_bsfc.htm.html": "gjjrx_bsfc.html",
    "gjjrx_szdw_jsfc.htm.html": "gjjrx_jsfc.html",
    "gjjrx_xygk_xyld.htm.html": "gjjrx_xrld.html",
    "gjjrx_xygk_xyjj.htm.html": "gjjrx_xyjj.html",
    "gjjrx_xygk_jgsz.htm.html": "gjjrx_jgsz.html",
    "gjjrx_szdw_szgk.htm.html": "gjjrx_szgk.html",
    "gjjrx_info_1056_2284.htm.html": "gjjrx_detail.html",
    "gjjrx_search_p1.html": "gjjrx_search_p1.html",
    # jmx
    "jmx_index_xwgg.htm.html": "jmx_xwgg.html",
    "jmx_index_djhd.htm.html": "jmx_djhd.html",
    "jmx_index_jxhd.htm.html": "jmx_jxhd.html",
    "jmx_index_kyhd.htm.html": "jmx_kyhd.html",
    "jmx_index_ssfc.htm.html": "jmx_ssfc.html",
    "jmx_xygk_xyjj.htm.html": "jmx_xyjj.html",
    "jmx_xygk_jgsz.htm.html": "jmx_jgsz.html",
    "jmx_xygk_xrld.htm.html": "jmx_xrld.html",
    "jmx_info_1093_3725.htm.html": "jmx_detail.html",
    # gsgl
    "gsgl_xwxx.htm.html": "gsgl_xwxx.html",
    "gsgl_jxky1_jyhd.htm.html": "gsgl_jyhd.html",
    "gsgl_djgz_djhd.htm.html": "gsgl_djhd.html",
    "gsgl_xsgz_xshd.htm.html": "gsgl_xshd.html",
    "gsgl_szdw_js.htm.html": "gsgl_js.html",
    "gsgl_szdw_fjs.htm.html": "gsgl_fjs.html",
    "gsgl_szdw_bs.htm.html": "gsgl_bs.html",
    "gsgl_szdw_szgk.htm.html": "gsgl_szgk.html",
    "gsgl_xygk_ykjj.htm.html": "gsgl_ykjj.html",
    "gsgl_xygk_ldjs.htm.html": "gsgl_ldjs.html",
    "gsgl_info_1137_3494.htm.html": "gsgl_detail.html",
    # xxgc
    "xxgc_index_xyxw.htm.html": "xxgc_xyxw.html",
    "xxgc_tzgg.htm.html": "xxgc_tzgg.html",
    "xxgc_index_jxhd.htm.html": "xxgc_jxhd.html",
    "xxgc_szdw_jsml.htm.html": "xxgc_jsml.html",
    "xxgc_szdw_jfry.htm.html": "xxgc_jfry.html",
    "xxgc_szdw_szgk.htm.html": "xxgc_szgk.html",
    "xxgc_xygk_xyjj.htm.html": "xxgc_xyjj.html",
    "xxgc_xygk_ldjs.htm.html": "xxgc_ldjs.html",
    "xxgc_info_1055_3902.htm.html": "xxgc_detail.html",
    # jrsx
    "jrsx_index_xwxx.htm.html": "jrsx_xwxx.html",
    "jrsx_index_tzgg.htm.html": "jrsx_tzgg.html",
    "jrsx_szdw_jsml.htm.html": "jrsx_jsml.html",
    "jrsx_szdw_ssds.htm.html": "jrsx_ssds.html",
    "jrsx_szdw_msfc.htm.html": "jrsx_msfc.html",
    "jrsx_szdw_szgk.htm.html": "jrsx_szgk.html",
    "jrsx_xygk1_xyjj.htm.html": "jrsx_xyjj.html",
    "jrsx_xygk1_xyld.htm.html": "jrsx_xyld.html",
    "jrsx_info_1055_3611.htm.html": "jrsx_detail.html",
}

for src, dst in COPY.items():
    source = PROBED / src
    if not source.exists():
        print("MISSING:", src)
        continue
    shutil.copyfile(source, FIXTURES / dst)
print("copied", len(COPY), "fixtures")
