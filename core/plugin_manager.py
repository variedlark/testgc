from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional

import config


class PluginManager:
    """Simple plugin loader. Each plugin is a .py file with an optional
    `register(game)` function that receives the game instance.
    """

    def __init__(self, plugin_dir: Path | None = None) -> None:
        self.plugin_dir = plugin_dir or (config.PROJECT_ROOT / "plugins")
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self._modules: Dict[str, ModuleType] = {}
        self._loaded: List[str] = []

    def discover(self) -> List[Path]:
        return [p for p in self.plugin_dir.glob("*.py") if p.name != "__init__.py"]

    def load_all(self, game: object) -> None:
        for path in self.discover():
            self.load(path, game)

    def load(self, path: Path, game: object) -> Optional[ModuleType]:
        name = f"plugins.{path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(name, str(path))
            if spec is None:
                return None
            module = importlib.util.module_from_spec(spec)
            loader = spec.loader
            assert loader is not None
            loader.exec_module(module)
            self._modules[name] = module
            self._loaded.append(name)
            # call register if present
            if hasattr(module, "register"):
                try:
                    module.register(game)
                except Exception as ex:
                    print(f"Plugin {name} register() failed: {ex}")
            return module
        except Exception as ex:
            print(f"Failed to load plugin {path}: {ex}")
            return None

    def unload(self, name: str) -> None:
        module = self._modules.pop(name, None)
        if module:
            if hasattr(module, "unregister"):
                try:
                    module.unregister()
                except Exception:
                    pass
            sys.modules.pop(name, None)
            if name in self._loaded:
                self._loaded.remove(name)
