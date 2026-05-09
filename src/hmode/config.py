from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

CONFIG_PATH = Path.home() / ".hmode.json"


@dataclass
class Preset:
    name: str
    model: str


@dataclass
class Config:
    active: str | None
    presets: dict[str, Preset]
    templates: dict[str, str]
    sessions: list[dict[str, str]]


def default_config() -> Config:
    return Config(active=None, presets={}, templates={}, sessions=[])


def config_exists(path: Path = CONFIG_PATH) -> bool:
    return path.exists()


def load_config(path: Path = CONFIG_PATH) -> Config:
    if not path.exists():
        return default_config()

    data = json.loads(path.read_text())
    presets = {
        name: Preset(name=name, model=value["model"])
        for name, value in data.get("presets", {}).items()
    }
    return Config(
        active=data.get("active"),
        presets=presets,
        templates=data.get("templates", {}),
        sessions=data.get("sessions", []),
    )


def save_config(config: Config, path: Path = CONFIG_PATH) -> None:
    path.write_text(json.dumps(serialize_config(config), indent=2) + "\n")


def serialize_config(config: Config) -> dict[str, Any]:
    return {
        "active": config.active,
        "presets": {name: asdict(preset) for name, preset in config.presets.items()},
        "templates": config.templates,
        "sessions": config.sessions,
    }
