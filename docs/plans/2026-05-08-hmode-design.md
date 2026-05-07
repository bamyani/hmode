# hmode design

## Goal
Build a tiny Python CLI for switching AI model presets quickly.

## Scope
- add presets
- list presets
- set the active preset
- show current status
- store config locally in JSON

## Non-goals
- no GUI
- no provider-specific API calls
- no sync service
- no complex account handling

## Data model
A config file at `~/.hmode.json` with:
- `active`: string or null
- `presets`: map of preset name to model string

## Commands
- `hmode init`
- `hmode add <name> --model <model>`
- `hmode set <name>`
- `hmode list`
- `hmode status`

## Implementation notes
- use only the Python standard library
- keep parsing and persistence separate from CLI logic
- make the output simple and readable

## Validation
- unit test the CLI command functions with a temp config path
- verify init/add/set/list/status flows
