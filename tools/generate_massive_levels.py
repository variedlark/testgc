from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config


def build_objects(seed: int, base_length: int = 20) -> list[dict[str, object]]:
    objects: list[dict[str, object]] = []
    x = 320.0

    for segment in range(base_length):
        stride = 220 + ((seed + segment) % 5) * 20
        block_y = 560 - ((seed + segment * 2) % 4) * 40
        spike_y = 580 - ((seed + segment) % 3) * 20

        objects.append(
            {
                "type": "block",
                "x": round(x, 2),
                "y": block_y,
                "width": 120 + ((seed + segment) % 3) * 20,
                "height": 50,
            }
        )

        objects.append(
            {
                "type": "spike",
                "x": round(x + 140, 2),
                "y": spike_y,
                "size": 40,
            }
        )

        if segment % 2 == 0:
            objects.append(
                {
                    "type": "orb",
                    "x": round(x + 185, 2),
                    "y": 460 - ((seed + segment) % 3) * 30,
                }
            )

        if segment % 3 == 0:
            objects.append(
                {
                    "type": "platform",
                    "x": round(x + 210, 2),
                    "y": 460 - ((seed + segment) % 2) * 70,
                    "width": 100,
                    "height": 22,
                }
            )

        if segment % 4 == 0:
            objects.append(
                {
                    "type": "pad",
                    "x": round(x + 70, 2),
                    "y": 600,
                    "width": 42,
                    "height": 20,
                }
            )

        if segment % 5 == 0:
            portal_kind = "speed" if ((seed + segment) % 2 == 0) else "gravity"
            portal_value = "fast" if portal_kind == "speed" else "invert"
            objects.append(
                {
                    "type": "portal",
                    "x": round(x + 250, 2),
                    "y": 470,
                    "kind": portal_kind,
                    "value": portal_value,
                }
            )

        x += stride

    return objects


def generate_levels(start_index: int = 6, count: int = 180) -> tuple[int, int]:
    level_dir = Path(config.LEVELS_DIR)
    level_dir.mkdir(parents=True, exist_ok=True)

    files_written = 0
    total_objects = 0

    for i in range(start_index, start_index + count):
        level_id = f"massive_{i:04d}"
        level_name = f"Massive Grid {i:04d}"
        difficulty = ["Easy", "Normal", "Hard", "Insane"][i % 4]
        speed = ["normal", "fast", "faster", "slow"][i % 4]
        theme = ["default", "aqua", "neon", "sunset"][i % 4]
        music = ["track_01", "track_02", "track_03"][i % 3]

        objects = build_objects(seed=i, base_length=20)
        level = {
            "id": level_id,
            "name": level_name,
            "difficulty": difficulty,
            "music": music,
            "speed": speed,
            "background_theme": theme,
            "length": int(6000 + i * 45),
            "objects": objects,
        }

        out_path = level_dir / f"level_{i:04d}.json"
        out_path.write_text(json.dumps(level, indent=2), encoding="utf-8")

        files_written += 1
        total_objects += len(objects)

    return files_written, total_objects


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a large set of level JSON files.")
    parser.add_argument("--start", type=int, default=6, help="Start level index, inclusive")
    parser.add_argument("--count", type=int, default=180, help="Number of levels to generate")
    args = parser.parse_args()

    written, objects = generate_levels(start_index=args.start, count=args.count)
    print(f"Generated level files: {written}")
    print(f"Total objects generated: {objects}")


if __name__ == "__main__":
    main()
