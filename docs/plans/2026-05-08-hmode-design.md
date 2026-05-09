# hmode design

## Goal
Build a small but credible Python CLI toolkit for managing AI workflow presets, templates, sessions, and timing notes.

## Scope
- add and switch model presets
- store reusable prompt templates
- save lightweight session notes
- export and import config as JSON
- keep config locally in a single file

## Non-goals
- no GUI
- no provider-specific API calls
- no cloud sync
- no authentication layer
- no heavyweight database

## Data model
A config file at `~/.hmode.json` with:
- `active`: string or null
- `presets`: map of preset name to model string
- `templates`: map of template name to template text
- `sessions`: list of timestamped notes

## Commands
- `hmode init`
- `hmode add <name> --model <model>`
- `hmode set <name>`
- `hmode list [--templates]`
- `hmode status`
- `hmode template add <name> <text>`
- `hmode template list`
- `hmode session <note>`
- `hmode export`
- `hmode import <path>`

## Implementation notes
- use only the Python standard library
- keep parsing and persistence separate from CLI logic
- keep output readable and minimal
- make it easy to extend later with reminders or a TUI

## Validation
- unit test the CLI command functions with a temp config path
- verify init/add/set/template/session/export/import flows
