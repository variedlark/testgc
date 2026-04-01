import tempfile
import unittest
from pathlib import Path

from core.plugin_manager import PluginManager


class _Game:
    def __init__(self):
        self.calls = []


class TestPluginManager(unittest.TestCase):
    def test_load_reload_unload_cycle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)
            plugin_file = plugin_dir / "demo.py"
            plugin_file.write_text(
                "def register(game):\n"
                "    game.calls.append('register_v1')\n"
                "\n"
                "def unregister(game=None):\n"
                "    if game is not None:\n"
                "        game.calls.append('unregister_v1')\n",
                encoding="utf-8",
            )

            game = _Game()
            pm = PluginManager(plugin_dir=plugin_dir)

            mod = pm.load(plugin_file, game)
            self.assertIsNotNone(mod)
            self.assertIn("plugins.demo", pm.loaded_names())
            self.assertEqual(game.calls, ["register_v1"])

            plugin_file.write_text(
                "def register(game):\n"
                "    game.calls.append('register_v2')\n"
                "\n"
                "def unregister(game=None):\n"
                "    if game is not None:\n"
                "        game.calls.append('unregister_v2')\n",
                encoding="utf-8",
            )

            mod2 = pm.reload(plugin_file, game)
            self.assertIsNotNone(mod2)
            self.assertIn("unregister_v1", game.calls)
            self.assertIn("register_v2", game.calls)

            pm.unload("plugins.demo")
            self.assertNotIn("plugins.demo", pm.loaded_names())
            self.assertIn("unregister_v2", game.calls)


if __name__ == "__main__":
    unittest.main()
