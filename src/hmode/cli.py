from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .config import CONFIG_PATH, Config, Preset, default_config, load_config, save_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hmode", description="Local AI workflow toolkit.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create an empty config file")

    add_parser = subparsers.add_parser("add", help="Add a preset")
    add_parser.add_argument("name")
    add_parser.add_argument("--model", required=True)

    set_parser = subparsers.add_parser("set", help="Set the active preset")
    set_parser.add_argument("name")

    list_parser = subparsers.add_parser("list", help="List presets")
    list_parser.add_argument("--templates", action="store_true", help="Also list templates")

    subparsers.add_parser("status", help="Show active preset")

    tpl_parser = subparsers.add_parser("template", help="Manage prompt templates")
    tpl_sub = tpl_parser.add_subparsers(dest="template_command", required=True)
    tpl_add = tpl_sub.add_parser("add", help="Add a template")
    tpl_add.add_argument("name")
    tpl_add.add_argument("text")
    tpl_sub.add_parser("list", help="List templates")

    session_parser = subparsers.add_parser("session", help="Track a session note")
    session_parser.add_argument("note")

    subparsers.add_parser("export", help="Export config as JSON")
    imp_parser = subparsers.add_parser("import", help="Import config from JSON")
    imp_parser.add_argument("path")

    return parser


def cmd_init(path: Path = CONFIG_PATH) -> int:
    if path.exists():
        print(f"Config already exists at {path}")
        return 0
    save_config(default_config(), path)
    print(f"Created {path}")
    return 0


def cmd_add(name: str, model: str, path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    config.presets[name] = Preset(name=name, model=model)
    if config.active is None:
        config.active = name
    save_config(config, path)
    print(f"Saved preset {name} -> {model}")
    return 0


def cmd_set(name: str, path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    if name not in config.presets:
        print(f"Unknown preset: {name}", file=sys.stderr)
        return 1
    config.active = name
    save_config(config, path)
    print(f"Active preset: {name} ({config.presets[name].model})")
    return 0


def cmd_list(path: Path = CONFIG_PATH, show_templates: bool = False) -> int:
    config = load_config(path)
    if not config.presets:
        print("No presets saved yet")
    else:
        for name, preset in config.presets.items():
            marker = "*" if config.active == name else " "
            print(f"{marker} {name}: {preset.model}")
    if show_templates:
        print()
        cmd_template_list(path)
    return 0


def cmd_status(path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    if not config.active or config.active not in config.presets:
        print("No active preset set")
        return 0
    preset = config.presets[config.active]
    print(f"{config.active}: {preset.model}")
    return 0


def cmd_template_add(name: str, text: str, path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    config.templates[name] = text
    save_config(config, path)
    print(f"Saved template {name}")
    return 0


def cmd_template_list(path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    if not config.templates:
        print("No templates saved yet")
        return 0
    for name, text in config.templates.items():
        print(f"{name}: {text}")
    return 0


def cmd_session(note: str, path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    timestamp = datetime.now().isoformat(timespec="seconds")
    config.sessions.append({"time": timestamp, "note": note})
    save_config(config, path)
    print(f"Saved session note at {timestamp}")
    return 0


def cmd_export(path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    print(json.dumps({"active": config.active, "presets": {k: {"name": v.name, "model": v.model} for k, v in config.presets.items()}, "templates": config.templates, "sessions": config.sessions}, indent=2))
    return 0


def cmd_import(source: Path, path: Path = CONFIG_PATH) -> int:
    data = json.loads(source.read_text())
    config = default_config()
    config.active = data.get("active")
    config.presets = {
        name: Preset(name=name, model=value["model"])
        for name, value in data.get("presets", {}).items()
    }
    config.templates = data.get("templates", {})
    config.sessions = data.get("sessions", [])
    save_config(config, path)
    print(f"Imported config from {source}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        return cmd_init()
    if args.command == "add":
        return cmd_add(args.name, args.model)
    if args.command == "set":
        return cmd_set(args.name)
    if args.command == "list":
        return cmd_list(show_templates=args.templates)
    if args.command == "status":
        return cmd_status()
    if args.command == "template":
        if args.template_command == "add":
            return cmd_template_add(args.name, args.text)
        if args.template_command == "list":
            return cmd_template_list()
    if args.command == "session":
        return cmd_session(args.note)
    if args.command == "export":
        return cmd_export()
    if args.command == "import":
        return cmd_import(Path(args.path))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
