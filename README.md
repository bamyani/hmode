# hmode

`hmode` is a local AI workflow toolkit for people who switch models, prompts, and work modes a lot.

It helps you keep things simple:
- save model presets
- store reusable prompt templates
- note sessions and context
- track usage timing reminders
- switch fast from the terminal

## Why it exists
If you keep bouncing between tools or model settings, this gives you one small place to organise the workflow.

## Features
- model presets like `fast`, `balanced`, and `best`
- prompt templates for repeat tasks
- lightweight session notes
- usage-window reminders
- import/export for your config
- simple JSON config in your home directory

## Install
```bash
pip install .
```

## Quick start
```bash
hmode init
hmode add fast --model gpt-4.1-mini
hmode add best --model claude-opus-4
hmode set best
hmode list
hmode status
```

## Config
Your config lives at `~/.hmode.json`.

Example:
```json
{
  "active": "best",
  "presets": {
    "fast": {
      "name": "fast",
      "model": "gpt-4.1-mini"
    },
    "best": {
      "name": "best",
      "model": "claude-opus-4"
    }
  }
}
```

## Roadmap
- prompt template manager
- session logging
- reminder scheduler
- export/import commands
- optional TUI later

## License
MIT
