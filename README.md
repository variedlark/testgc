# Pulse Runner

A Geometry Dash-inspired rhythm platformer built with Pygame using a modular architecture (scene stack, fixed timestep, event bus, plugin hooks, and hot-reload for development).

## Current Architecture

- `core/game.py`: Main loop, subsystem wiring, DI registrations, plugin manager integration, hot-reload callback.
- `core/events.py`: Event bus with priorities, one-shot handlers, deferred queue support.
- `core/di.py`: Service container for singleton/factory resolution.
- `core/plugin_manager.py`: Source-based plugin loader with `load/reload/unload` lifecycle.
- `core/hotreload.py`: Polling file watcher for `created/modified/deleted` changes.

## Running the Game

```powershell
& ".venv/Scripts/python.exe" main.py
```

## Development Hot-Reload

Enable development watcher:

```powershell
$env:TESTGC_HOTRELOAD = "1"
& ".venv/Scripts/python.exe" main.py
```

When enabled:
- plugin `.py` file changes trigger plugin reload/unload events.
- level `.json` changes trigger in-memory level list refresh.
- other watched assets emit `hotreload.file_changed` on the event bus.

## Plugin API

A plugin is a Python file in `plugins/`.

Supported hooks:
- `register(game)` or `register()`
- `unregister(game)` or `unregister()`

Minimal example:

```python
def register(game):
    def on_reload(payload):
        print("reload event", payload)

    game.event_bus.subscribe("plugin.reloaded", on_reload)


def unregister(game=None):
    print("plugin unloading")
```

## Tests

Run all tests:

```powershell
& ".venv/Scripts/python.exe" -m unittest discover -s tests -v
```

## LOC Progress Toward 100,000 Goal

Use the built-in tracker:

```powershell
& ".venv/Scripts/python.exe" tools/loc_report.py --target 100000
```

Optional JSON report output:

```powershell
& ".venv/Scripts/python.exe" tools/loc_report.py --target 100000 --json-output data/loc_progress.json
```

This gives a concrete progress metric so we can keep implementation growth measurable over time.
