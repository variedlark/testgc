import tempfile
import unittest
from pathlib import Path

from levels.loader import LevelLoader


_LEVEL_TEMPLATE = """{{
    \"id\": \"{id}\",
    \"name\": \"{name}\",
    \"difficulty\": \"Easy\",
    \"music\": \"track_01\",
    \"speed\": \"normal\",
    \"background_theme\": \"default\",
    \"length\": 2400,
    \"objects\": []
}}
"""


class TestLevelLoader(unittest.TestCase):
    def test_discovery_numeric_order(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "level_10.json").write_text(
                _LEVEL_TEMPLATE.format(id="l10", name="L10"),
                encoding="utf-8",
            )
            (root / "level_2.json").write_text(
                _LEVEL_TEMPLATE.format(id="l2", name="L2"),
                encoding="utf-8",
            )
            (root / "level_1.json").write_text(
                _LEVEL_TEMPLATE.format(id="l1", name="L1"),
                encoding="utf-8",
            )

            loader = LevelLoader(level_dir=root)
            levels = loader.load_all()
            self.assertEqual([lvl.id for lvl in levels], ["l1", "l2", "l10"])


if __name__ == "__main__":
    unittest.main()
