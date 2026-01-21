# ┌─────────────────────────────────────────┐
# │ config.py on Nercone Search             │
# │ Copyright (c) 2026 DiamondGotCat        │
# │ Made by Nercone / MIT License           │
# └─────────────────────────────────────────┘

import toml
from typing import Any
from pathlib import Path

filepath = Path.cwd().joinpath("config.toml")
config: dict[str, Any] = {}

def reload():
    if filepath.is_file():
        with filepath.open("r") as f:
            config = toml.load(f)

reload()
