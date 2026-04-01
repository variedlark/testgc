from __future__ import annotations

import inspect
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
        self._paths: Dict[str, Path] = {}
        self._contexts: Dict[str, object] = {}

    def module_name_for_path(self, path: Path) -> str:
        return f"plugins.{Path(path).stem}"

    def discover(self) -> List[Path]:
        return sorted([p for p in self.plugin_dir.glob("*.py") if p.name != "__init__.py"])

    def loaded_names(self) -> List[str]:
        return sorted(self._modules.keys())

    def load_all(self, game: object) -> None:
        for path in self.discover():
            self.load(path, game)

    def reload_all(self, game: object) -> None:
        for path in self.discover():
            self.reload(path, game)

    def load(self, path: Path, game: object) -> Optional[ModuleType]:
        name = self.module_name_for_path(path)
        path = Path(path)
        if name in self._modules:
            return self._modules[name]

        try:
            if not path.exists():
                return None

            source = path.read_text(encoding="utf-8")
            module = ModuleType(name)
            module.__file__ = str(path)
            sys.modules[name] = module

            # Execute plugin source directly to avoid stale bytecode issues
            exec(compile(source, str(path), "exec"), module.__dict__)

            self._modules[name] = module
            self._paths[name] = path
            self._contexts[name] = game
            # call register if present
            self._invoke_hook(module, "register", game)
            return module
        except Exception as ex:
            print(f"Failed to load plugin {path}: {ex}")
            self._modules.pop(name, None)
            self._paths.pop(name, None)
            self._contexts.pop(name, None)
            sys.modules.pop(name, None)
            return None

    def reload(self, path: Path, game: object) -> Optional[ModuleType]:
        name = self.module_name_for_path(path)
        if name in self._modules:
            self.unload(name)
        return self.load(path, game)

    def unload(self, name: str) -> None:
        module = self._modules.pop(name, None)
        context = self._contexts.pop(name, None)
        self._paths.pop(name, None)
        if module:
            self._invoke_hook(module, "unregister", context)
            sys.modules.pop(name, None)

    def unload_all(self) -> None:
        for name in list(self._modules.keys()):
            self.unload(name)

    def _invoke_hook(self, module: ModuleType, hook_name: str, context: object | None) -> None:
        hook = getattr(module, hook_name, None)
        if hook is None:
            return

        try:
            signature = inspect.signature(hook)
            positional = [
                p
                for p in signature.parameters.values()
                if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]
            accepts_var_args = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in signature.parameters.values())

            if accepts_var_args or len(positional) >= 1:
                hook(context)
            else:
                hook()
        except Exception as ex:
            print(f"Plugin {module.__name__} {hook_name}() failed: {ex}")
