#!/usr/bin/env python3
"""Apply a one-time baseline to a simple key/value PC port config."""

import json
import os
import pathlib
import re
import tempfile
import sys

config = pathlib.Path(sys.argv[1])
marker = config.parent / ".dg-display-input-baseline"
if not config.is_file() or marker.exists():
    sys.exit(0)

desired = json.loads(os.environ["DG_PC_PORT_KV_DEFAULTS"])
seen = set()
output_lines = []
for line in config.read_text().splitlines(keepends=True):
    setting = re.match(r"([A-Za-z_][A-Za-z_0-9]*)(\s*=\s*|\s+)([^#\r\n]*)(.*)", line)
    if setting and setting.group(1) in desired:
        key = setting.group(1)
        newline = "\n" if line.endswith("\n") else ""
        line = f"{key}{setting.group(2)}{desired[key]}{setting.group(4)}{newline}"
        seen.add(key)
    output_lines.append(line)
if seen != desired.keys():
    raise ValueError(f"PC port settings missing: {desired.keys() - seen}")

with tempfile.NamedTemporaryFile("w", dir=config.parent, delete=False) as output:
    output.write("".join(output_lines))
    temporary = pathlib.Path(output.name)
os.chmod(temporary, config.stat().st_mode & 0o777)
os.replace(temporary, config)
marker.touch()
print("applied PC port key-value defaults")
