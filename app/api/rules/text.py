"""Loads config.yaml and the fixed sentence templates. The only I/O in rules/."""
import json
import pathlib

import yaml

_API = pathlib.Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((_API / "config.yaml").read_text())


def templates(lang: str) -> dict[str, str]:
    return json.loads((_API / "rules" / "templates" / f"{lang}.json").read_text(encoding="utf-8"))
