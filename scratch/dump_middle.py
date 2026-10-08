"""Print the middle content region of a saved page (between nav and footer)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

html = Path(sys.argv[1]).read_text(encoding="utf-8")
start = int(sys.argv[2]) if len(sys.argv) > 2 else 15000
end = int(sys.argv[3]) if len(sys.argv) > 3 else start + 9000
region = html[start:end]
region = re.sub(r"<!--.*?-->", "", region, flags=re.S)
region = re.sub(r"\n\s*\n", "\n", region)
print(region)
