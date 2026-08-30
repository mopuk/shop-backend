import json
from pathlib import Path


def load_json(file: Path):
    with open(file) as f:
        return json.load(f)
