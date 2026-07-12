#!/usr/bin/env python3
"""Fail when a repository checkout contains known non-redistributable output."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {".dds", ".civ5mod", ".ips"}
FORBIDDEN_PARTS = {"dist", "SimplifiedChineseBackup"}
MAX_TRACKED_FILE_SIZE = 1_000_000


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]


def main() -> None:
    violations = []
    for path in tracked_files():
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            violations.append(str(relative))
        if any(part == "dist" or part.startswith("SimplifiedChineseBackup") for part in relative.parts):
            violations.append(str(relative))
        if "Contents" in relative.parts and "Assets" in relative.parts:
            violations.append(str(relative))
        if path.is_file() and path.stat().st_size > MAX_TRACKED_FILE_SIZE:
            violations.append(f"{relative} (larger than 1 MB)")
    if violations:
        raise SystemExit("release audit failed:\n" + "\n".join(sorted(set(violations))))
    print("release audit passed: no generated patch, font atlas, or backup is tracked")


if __name__ == "__main__":
    main()
