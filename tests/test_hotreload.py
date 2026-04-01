import tempfile
import time
import unittest
from pathlib import Path

from core.hotreload import HotReloader


class TestHotReload(unittest.TestCase):
    def test_created_modified_deleted_callbacks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            events = []

            def callback(path: Path, change: str):
                events.append((path.name, change))

            hr = HotReloader([root], callback, interval=0.01)

            # Initial scan seeds mtimes without reporting create events.
            hr._scan_once()

            file_path = root / "x.py"
            file_path.write_text("a = 1\n", encoding="utf-8")
            hr._scan_once()
            self.assertIn(("x.py", "created"), events)

            # Ensure mtime changes for modified detection
            time.sleep(0.02)
            file_path.write_text("a = 2\n", encoding="utf-8")
            hr._scan_once()
            self.assertIn(("x.py", "modified"), events)

            file_path.unlink()
            hr._scan_once()
            self.assertIn(("x.py", "deleted"), events)


if __name__ == "__main__":
    unittest.main()
