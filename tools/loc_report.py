from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable


DEFAULT_EXTENSIONS = (".py", ".json", ".md")
DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}


@dataclass
class LocSummary:
    total_lines: int
    files_counted: int
    by_extension: Dict[str, int]


def count_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        return sum(1 for _ in f)


def should_skip(path: Path, excludes: Iterable[str]) -> bool:
    parts = set(path.parts)
    return any(ex in parts for ex in excludes)


def collect_summary(root: Path, exts: Iterable[str], excludes: Iterable[str]) -> LocSummary:
    by_ext: Dict[str, int] = {ext: 0 for ext in exts}
    total = 0
    files = 0

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if should_skip(p.relative_to(root), excludes):
            continue
        if p.suffix not in by_ext:
            continue

        line_count = count_lines(p)
        by_ext[p.suffix] += line_count
        total += line_count
        files += 1

    return LocSummary(total_lines=total, files_counted=files, by_extension=by_ext)


def main() -> None:
    parser = argparse.ArgumentParser(description="Report LOC progress toward a target.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--target", type=int, default=100_000, help="Target LOC")
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=list(DEFAULT_EXTENSIONS),
        help="File extensions to include, e.g. .py .json .md",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=sorted(DEFAULT_EXCLUDES),
        help="Directory names to exclude",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=None,
        help="Optional path to write JSON summary",
    )

    args = parser.parse_args()
    root = args.root.resolve()
    summary = collect_summary(root, args.extensions, args.exclude)

    remaining = max(args.target - summary.total_lines, 0)
    pct = (summary.total_lines / args.target * 100.0) if args.target > 0 else 100.0

    print(f"Root: {root}")
    print(f"Files counted: {summary.files_counted}")
    print(f"Total LOC: {summary.total_lines}")
    print(f"Target LOC: {args.target}")
    print(f"Progress: {pct:.2f}%")
    print(f"Remaining: {remaining}")
    print("By extension:")
    for ext, lines in sorted(summary.by_extension.items()):
        print(f"  {ext}: {lines}")

    if args.json_output is not None:
        payload = {
            "root": str(root),
            "target": args.target,
            "remaining": remaining,
            "progress_percent": round(pct, 4),
            "summary": asdict(summary),
        }
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"JSON report written to: {args.json_output}")


if __name__ == "__main__":
    main()
