from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import CONFIG_PATH, Config, Preset, default_config, load_config, save_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hmode", description="Switch AI model presets fast.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create an empty config file")

    add_parser = subparsers.add_parser("add", help="Add a preset")
    add_parser.add_argument("name")
    add_parser.add_argument("--model", required=True)

    set_parser = subparsers.add_parser("set", help="Set the active preset")
    set_parser.add_argument("name")

    subparsers.add_parser("list", help="List presets")
    subparsers.add_parser("status", help="Show active preset")

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


def cmd_list(path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    if not config.presets:
        print("No presets saved yet")
        return 0
    for name, preset in config.presets.items():
        marker = "*" if config.active == name else " "
        print(f"{marker} {name}: {preset.model}")
    return 0


def cmd_status(path: Path = CONFIG_PATH) -> int:
    config = load_config(path)
    if not config.active or config.active not in config.presets:
        print("No active preset set")
        return 0
    preset = config.presets[config.active]
    print(f"{config.active}: {preset.model}")
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
        return cmd_list()
    if args.command == "status":
        return cmd_status()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
