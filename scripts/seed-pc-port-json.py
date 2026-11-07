#!/usr/bin/env python3
"""Apply one-time, non-destructive defaults to a PC port's JSON config."""

import json
import os
import pathlib
import tempfile
import sys


def merge(existing, defaults):
    for key, value in defaults.items():
        if isinstance(value, dict) and isinstance(existing.get(key), dict):
            merge(existing[key], value)
        else:
            existing[key] = value


config = pathlib.Path(sys.argv[1])
marker = pathlib.Path(sys.argv[2])
if not config.is_file() or marker.exists():
    sys.exit(0)

existing = json.loads(config.read_text())
defaults = json.loads(os.environ["DG_PC_PORT_JSON_DEFAULTS"])
if not isinstance(existing, dict) or not isinstance(defaults, dict):
    raise ValueError("PC port JSON settings must be objects")
merge(existing, defaults)

with tempfile.NamedTemporaryFile("w", dir=config.parent, delete=False) as output:
    json.dump(existing, output, indent=2, ensure_ascii=False)
    output.write("\n")
    temporary = pathlib.Path(output.name)
os.chmod(temporary, config.stat().st_mode & 0o777)
os.replace(temporary, config)
marker.touch()
print("applied PC port defaults")
