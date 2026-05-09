# hmode

`hmode` is a local AI workflow toolkit for people who switch models, prompts, and work modes a lot.

It helps you keep things simple:
- save model presets
- store reusable prompt templates
- note sessions and context
- plan usage-window primers
- switch fast from the terminal

## Why it exists
If you keep bouncing between tools or model settings, this gives you one small place to organise the workflow.

## Features
- model presets like `fast`, `balanced`, and `best`
- prompt templates for repeat tasks
- lightweight session notes
- usage-window primer planning
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
hmode template add review "Give me a concise review."
hmode session "Swapped to best"
hmode primer --wake 9am --timezone Pacific/Auckland
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
  },
  "templates": {
    "review": "Give me a concise review."
  },
  "sessions": [
    {
      "time": "2026-05-09T08:00:00",
      "note": "Swapped to best"
    }
  ]
}
```

## Primer planning
`hmode primer` helps you line up an early-morning rolling-window starter so your resets happen during your workday. It doesn’t make extra usage available — it just shifts the timing.

## Roadmap
- richer template library
- preset profiles for different providers
- reminder export
- optional TUI later

## License
MIT
