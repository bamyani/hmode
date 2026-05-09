from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .config import CONFIG_PATH, Preset, default_config, load_config, save_config, serialize_config
from .timing import build_primer_plan, format_primer_plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hmode", description="Local AI workflow toolkit.")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="Path to the config file")
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
    tpl_add.add_argument("text", nargs="+")
    tpl_sub.add_parser("list", help="List templates")

    session_parser = subparsers.add_parser("session", help="Track a session note")
    session_parser.add_argument("note", nargs="+")

    reminder_parser = subparsers.add_parser("reminder", help="Track simple reminders")
    reminder_sub = reminder_parser.add_subparsers(dest="reminder_command", required=True)
    reminder_add = reminder_sub.add_parser("add", help="Add a reminder")
    reminder_add.add_argument("when")
    reminder_add.add_argument("text", nargs="+")
    reminder_sub.add_parser("list", help="List reminders")

    subparsers.add_parser("export", help="Export config as JSON")
    imp_parser = subparsers.add_parser("import", help="Import config from JSON")
    imp_parser.add_argument("path", type=Path)

    primer_parser = subparsers.add_parser("primer", help="Print a rolling-window primer schedule")
    primer_parser.add_argument("--wake", default="09:00", help="Wake time, such as 09:00 or 9am")
    primer_parser.add_argument("--timezone", default=None, help="Timezone name, such as Pacific/Auckland")
    primer_parser.add_argument("--primer-offset", type=float, default=2.5, help="Hours before wake to start")
    primer_parser.add_argument("--window-hours", type=float, default=5.0, help="Rolling window length")
    primer_parser.add_argument("--resets", type=int, default=3, help="Number of reset times to show")

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
        if config.presets:
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


def cmd_reminder_add(when: str, text: str, path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    config.reminders.append({"when": when, "text": text})
    save_config(config, path)
    print(f"Saved reminder for {when}")
    return 0


def cmd_reminder_list(path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    if not config.reminders:
        print("No reminders saved yet")
        return 0
    for reminder in config.reminders:
        print(f"{reminder['when']}: {reminder['text']}")
    return 0


def cmd_export(path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    print(json.dumps(serialize_config(config), indent=2))
    return 0


def cmd_import(source: Path, path: Path = CONFIG_PATH) -> int:
    try:
        data = json.loads(source.read_text())
    except OSError as exc:
        print(f"Could not read {source}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in {source}: {exc}", file=sys.stderr)
        return 1

    config = default_config()
    active = data.get("active")
    config.active = active if isinstance(active, str) else None
    config.presets = {}
    for name, value in data.get("presets", {}).items():
        model = ""
        if isinstance(value, dict):
            model = str(value.get("model", "")).strip()
        else:
            model = str(value).strip()
        if model:
            config.presets[str(name)] = Preset(name=str(name), model=model)
    config.templates = {str(name): str(value) for name, value in data.get("templates", {}).items()}
    config.sessions = []
    for item in data.get("sessions", []):
        if not isinstance(item, dict):
            continue
        time = str(item.get("time", "")).strip()
        note = str(item.get("note", "")).strip()
        if time and note:
            config.sessions.append({"time": time, "note": note})
    config.reminders = []
    for item in data.get("reminders", []):
        if not isinstance(item, dict):
            continue
        when = str(item.get("when", "")).strip()
        text = str(item.get("text", "")).strip()
        if when and text:
            config.reminders.append({"when": when, "text": text})
    if config.active not in config.presets:
        config.active = None
    save_config(config, path)
    print(f"Imported config from {source}")
    return 0


def cmd_primer(
    wake: str,
    timezone_name: str | None,
    primer_offset_hours: float,
    window_hours: float,
    resets: int,
) -> int:
    try:
        plan = build_primer_plan(
            wake=wake,
            timezone_name=timezone_name,
            primer_offset_hours=primer_offset_hours,
            window_hours=window_hours,
            resets=resets,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(format_primer_plan(plan))
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    path = args.config

    if args.command == "init":
        return cmd_init(path)
    if args.command == "add":
        return cmd_add(args.name, args.model, path)
    if args.command == "set":
        return cmd_set(args.name, path)
    if args.command == "list":
        return cmd_list(path, show_templates=args.templates)
    if args.command == "status":
        return cmd_status(path)
    if args.command == "template":
        if args.template_command == "add":
            return cmd_template_add(args.name, " ".join(args.text).strip(), path)
        if args.template_command == "list":
            return cmd_template_list(path)
    if args.command == "session":
        return cmd_session(" ".join(args.note).strip(), path)
    if args.command == "reminder":
        if args.reminder_command == "add":
            return cmd_reminder_add(args.when, " ".join(args.text).strip(), path)
        if args.reminder_command == "list":
            return cmd_reminder_list(path)
    if args.command == "export":
        return cmd_export(path)
    if args.command == "import":
        return cmd_import(args.path, path)
    if args.command == "primer":
        return cmd_primer(args.wake, args.timezone, args.primer_offset, args.window_hours, args.resets)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
