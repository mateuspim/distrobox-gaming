#!/usr/bin/env python3
"""Set a one-time high-resolution baseline in Unleashed Recompiled's TOML."""

import json
import os
import pathlib
import re
import tempfile
import sys
import tomllib

config = pathlib.Path(sys.argv[1])
marker = config.parent / ".dg-display-input-baseline"
if not config.is_file() or marker.exists():
    sys.exit(0)

desired = {key: str(value) for key, value in json.loads(os.environ["DG_PC_PORT_UNLEASHED_VIDEO"]).items()}
section = None
seen = set()
output_lines = []
for line in config.read_text().splitlines(keepends=True):
    heading = re.match(r"\s*\[([^]]+)\]\s*$", line)
    if heading:
        section = heading.group(1)
    if section == "Video":
        setting = re.match(r"(\s*)([A-Za-z]+)(\s*=\s*)([^#\r\n]*)(.*)", line)
        if setting and setting.group(2) in desired:
            key = setting.group(2)
            newline = "\n" if line.endswith("\n") else ""
            line = f"{setting.group(1)}{key}{setting.group(3)}{desired[key]}{setting.group(5)}{newline}"
            seen.add(key)
    output_lines.append(line)

if seen != desired.keys():
    raise ValueError(f"Unleashed video settings missing: {desired.keys() - seen}")
contents = "".join(output_lines)
tomllib.loads(contents)
with tempfile.NamedTemporaryFile("w", dir=config.parent, delete=False) as output:
    output.write(contents)
    temporary = pathlib.Path(output.name)
os.chmod(temporary, config.stat().st_mode & 0o777)
os.replace(temporary, config)
marker.touch()
print("applied Unleashed video defaults")
