# ┌─────────────────────────────────────────┐
# │ config.py on Nercone Search             │
# │ Copyright (c) 2026 DiamondGotCat        │
# │ Made by Nercone / MIT License           │
# └─────────────────────────────────────────┘

import toml
from pathlib import Path

filepath = Path.cwd().joinpath("config.toml")
if filepath.is_file():
    with filepath.open("r") as f:
        config: dict = toml.load(f)
