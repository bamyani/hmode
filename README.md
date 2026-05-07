# hmode

A tiny Python CLI for switching AI model presets fast.

## Why
If you keep changing models by hand, `hmode` gives you a dead-simple way to store presets and switch between them with one command.

## Features
- save presets like `fast`, `balanced`, and `best`
- list all presets
- show the active preset
- switch presets from the terminal
- simple JSON config in your home directory

## Install
```bash
pip install -e .
```

## Usage
```bash
hmode init
hmode add fast --model gpt-4.1-mini
hmode add balanced --model claude-3-5-sonnet-latest
hmode add best --model claude-opus-4
hmode list
hmode set fast
hmode status
```

## Config file
`~/.hmode.json`

## Roadmap
- add support for multiple provider profiles
- add usage window reminders
- add export/import for preset packs
- add shell completion

## License
MIT
