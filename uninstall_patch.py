#!/usr/bin/env python3
"""Restore the newest Civ V Simplified Chinese patch backup."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


GAME_APP = Path.home() / "Library/Application Support/Steam/steamapps/common/Sid Meier's Civilization V/Civilization V.app"
USER_DATA = Path.home() / "Library/Application Support/Sid Meier's Civilization 5"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--game", type=Path, default=GAME_APP)
    parser.add_argument("--user-data", type=Path, default=USER_DATA)
    args = parser.parse_args()

    user_data = args.user_data.expanduser().resolve()
    game = args.game.expanduser().resolve()
    backup = args.backup.expanduser().resolve() if args.backup else None
    if backup is None:
        candidates = sorted(user_data.glob("SimplifiedChineseBackup_*/install.json"), reverse=True)
        if not candidates:
            raise FileNotFoundError("no SimplifiedChinese backup found")
        backup = candidates[0].parent
    if not (backup / "install.json").is_file():
        raise FileNotFoundError(f"invalid backup: {backup}")

    metadata = json.loads((backup / "install.json").read_text(encoding="utf-8"))
    game_root = game
    for relative in metadata["patch_files"]:
        destination = game_root / relative
        original = backup / "game" / relative
        if original.is_file():
            shutil.copy2(original, destination)
        elif destination.exists():
            destination.unlink()

    original_config = backup / "config.ini.original"
    config = user_data / "config.ini"
    if original_config.is_file():
        shutil.copy2(original_config, config)
    cache = user_data / "cache"
    if cache.exists():
        shutil.rmtree(cache)
    original_cache = backup / "cache.original"
    if original_cache.exists():
        shutil.move(str(original_cache), str(cache))
    print(f"restored {backup}")


if __name__ == "__main__":
    main()
