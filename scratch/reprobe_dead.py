"""Re-probe the remaining unavailable GDUF domains for the 2026-10-08 check."""

from __future__ import annotations

import httpx

DOMAINS = [
    "dsai",
    "fx",
    "ggglxy",
    "mkszyxy",
    "gjjyxy",
    "jjxy",
]

client = httpx.Client(timeout=10.0, follow_redirects=True)
client.headers["User-Agent"] = "Mozilla/5.0 (gduf-web-api probe)"

for code in DOMAINS:
    for scheme in ("https", "http"):
        url = f"{scheme}://{code}.gduf.edu.cn/"
        try:
            response = client.get(url)
            print(f"{code} {scheme}: {response.status_code} len={len(response.content)}")
            break
        except Exception as exc:
            print(f"{code} {scheme}: {type(exc).__name__}: {str(exc)[:90]}")

client.close()
