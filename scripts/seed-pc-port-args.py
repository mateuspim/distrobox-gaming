#!/usr/bin/env python3
"""Apply one-time values to a JSON launch profile's flag/value arguments."""

import json
import os
import pathlib
import tempfile
import sys

config = pathlib.Path(sys.argv[1])
marker = config.parent / ".dg-display-input-baseline"
if not config.is_file() or marker.exists():
    sys.exit(0)

document = json.loads(config.read_text())
arguments = document["arguments"]
desired = {key: str(value) for key, value in json.loads(os.environ["DG_PC_PORT_ARG_DEFAULTS"]).items()}
for flag, value in desired.items():
    indices = [i for i, item in enumerate(arguments) if item == flag]
    if len(indices) != 1 or indices[0] + 1 >= len(arguments):
        raise ValueError(f"expected one flag/value pair for {flag}")
    arguments[indices[0] + 1] = value

with tempfile.NamedTemporaryFile("w", dir=config.parent, delete=False) as output:
    json.dump(document, output, indent=2, ensure_ascii=False)
    output.write("\n")
    temporary = pathlib.Path(output.name)
os.chmod(temporary, config.stat().st_mode & 0o777)
os.replace(temporary, config)
marker.touch()
print("applied PC port launch arguments")
