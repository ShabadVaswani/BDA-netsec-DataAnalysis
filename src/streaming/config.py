import json
from pathlib import Path
from typing import Any, Dict


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config() -> Dict[str, Any]:
    root = repo_root()
    config_path = root / "config.json"
    if not config_path.exists():
        config_path = root / "config.example.json"

    with config_path.open("r", encoding="utf-8") as fp:
        return json.load(fp)
