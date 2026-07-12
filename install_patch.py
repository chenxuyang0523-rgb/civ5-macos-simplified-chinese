#!/usr/bin/env python3
"""Install the locally built Civ V Mac Simplified Chinese patch with rollback data."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


GAME_APP = Path.home() / "Library/Application Support/Steam/steamapps/common/Sid Meier's Civilization V/Civilization V.app"
USER_DATA = Path.home() / "Library/Application Support/Sid Meier's Civilization 5"
DEFAULT_PATCH = Path(__file__).resolve().parent / "dist/Civ5_Simplified_Chinese_Mac"


def game_is_running() -> bool:
    result = subprocess.run(["pgrep", "-f", "Civilization V.app"], capture_output=True, text=True)
    return bool(result.stdout.strip())


def backup_file(source: Path, backup_root: Path, game_root: Path) -> None:
    if not source.exists():
        return
    relative = source.relative_to(game_root)
    destination = backup_root / "game" / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def replace_config(config: Path, backup_root: Path) -> None:
    if config.exists():
        shutil.copy2(config, backup_root / "config.ini.original")
        text = config.read_text(encoding="utf-8")
    else:
        text = ""
    if re.search(r"^Language\s*=", text, flags=re.MULTILINE):
        text = re.sub(r"^Language\s*=.*$", "Language = zh_Hant_HK", text, flags=re.MULTILINE)
    else:
        text += "\nLanguage = zh_Hant_HK\n"
    config.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--game", type=Path, default=GAME_APP)
    parser.add_argument("--user-data", type=Path, default=USER_DATA)
    args = parser.parse_args()

    patch = args.patch.expanduser().resolve()
    game = args.game.expanduser().resolve()
    user_data = args.user_data.expanduser().resolve()
    patch_manifest = patch / "patch-manifest.json"
    if not patch_manifest.is_file():
        raise FileNotFoundError(f"patch not built: {patch_manifest}")
    if not game.is_dir():
        raise FileNotFoundError(f"Civ V app not found: {game}")
    if game_is_running():
        raise RuntimeError("Civilization V is running; close it before installing the patch")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = user_data / f"SimplifiedChineseBackup_{timestamp}"
    backup_root.mkdir(parents=True, exist_ok=False)
    # The patch mirrors paths relative to the .app bundle itself.
    game_root = game
    installed = []
    for source in sorted(patch.rglob("*")):
        if not source.is_file() or source.name == "patch-manifest.json":
            continue
        relative = source.relative_to(patch)
        destination = game_root / relative
        backup_file(destination, backup_root, game_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        installed.append(str(relative))

    config = user_data / "config.ini"
    replace_config(config, backup_root)
    cache = user_data / "cache"
    if cache.exists():
        shutil.move(str(cache), str(backup_root / "cache.original"))
    logs = user_data / "Logs"
    if logs.exists():
        shutil.copytree(logs, backup_root / "Logs.original")

    metadata = {
        "installed_at": datetime.now().isoformat(timespec="seconds"),
        "backup": str(backup_root),
        "game": str(game),
        "patch_files": installed,
        "manifest": json.loads(patch_manifest.read_text(encoding="utf-8")),
    }
    (backup_root / "install.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
