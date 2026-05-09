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


def load_config(path: Path = CONFIG_PATH) -> Config:
    if not path.exists():
        return default_config()

    data = json.loads(path.read_text())
    presets: dict[str, Preset] = {}
    for name, value in data.get("presets", {}).items():
        model = ""
        if isinstance(value, dict):
            model = str(value.get("model", "")).strip()
        else:
            model = str(value).strip()
        if model:
            presets[str(name)] = Preset(name=str(name), model=model)

    templates: dict[str, str] = {}
    for name, value in data.get("templates", {}).items():
        templates[str(name)] = str(value)

    sessions: list[dict[str, str]] = []
    for item in data.get("sessions", []):
        if not isinstance(item, dict):
            continue
        time = str(item.get("time", "")).strip()
        note = str(item.get("note", "")).strip()
        if time and note:
            sessions.append({"time": time, "note": note})

    active = data.get("active")
    if not isinstance(active, str) or active not in presets:
        active = None

    return Config(active=active, presets=presets, templates=templates, sessions=sessions)


def save_config(config: Config, path: Path = CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(serialize_config(config), indent=2) + "\n")


def serialize_config(config: Config) -> dict[str, Any]:
    return {
        "active": config.active,
        "presets": {name: asdict(preset) for name, preset in config.presets.items()},
        "templates": config.templates,
        "sessions": config.sessions,
    }
