# Civilization V macOS Simplified Chinese Builder

An unofficial, open-source builder and reversible installer for generating a
Simplified Chinese localization patch for the Steam macOS edition of Sid
Meier's Civilization V.

This repository contains **code only**. It does not distribute Civilization V
text, 2K/Firaxis/Aspyr assets, Apple fonts, or generated font atlases. The
builder reads files available to the user through their own Steam installation
and generates the patch locally.

中文说明见 [README.zh-CN.md](README.zh-CN.md).

## Status

- Tested on Steam Civ V 1.4.2, Apple Silicon, and macOS 15.7.7.
- Covers the base game, Gods & Kings, and Brave New World.
- Uses OpenCC `t2s` conversion and the Mac port's existing `zh_Hant_HK` slot.
- Generates DXT5 bitmap font atlases from a font installed on the user's Mac.
- This is a macOS-only community project. Windows and Linux are not supported.

## Legal and ownership

You must own Civilization V and any DLC used by the builder. Generated output
is for personal use with that licensed copy. Do not redistribute generated
patches: they contain transformed game text and rasterized glyphs from your
local font. See [LEGAL.md](LEGAL.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Civilization, Sid Meier's Civilization V, Firaxis, 2K, Aspyr, Apple, PingFang,
and Steam are trademarks or properties of their respective owners. This project
is not affiliated with or endorsed by them.

## Requirements

- macOS with the Steam edition of Civilization V installed
- Python 3.11+
- Official Chinese depots downloaded through Steam by the game owner
- A locally installed CJK font

Install Python dependencies in an isolated environment:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Build

Download the required language depots using Steam's console, then point the
builder at Steam's `app_8930` content directory:

```sh
python build_patch.py \
  --steam-root "$HOME/Library/Application Support/Steam/Steam.AppBundle/Steam/Contents/MacOS/steamapps/content/app_8930"
```

The builder looks for depots `235586`, `16870`, and `235580`. The generated
directory is `dist/Civ5_Simplified_Chinese_Mac/` and is intentionally ignored by
Git.

To select a local font explicitly:

```sh
python build_patch.py --steam-root /path/to/app_8930 \
  --font /path/to/local/CJK-font.ttc --font-index 0
```

## Install and restore

Close Civilization V first, then run:

```sh
python install_patch.py
```

The installer backs up every replaced file, `config.ini`, and the localization
cache under:

```text
~/Library/Application Support/Sid Meier's Civilization 5/SimplifiedChineseBackup_TIMESTAMP/
```

Restore the latest backup:

```sh
python uninstall_patch.py
```

Steam game updates or file verification may overwrite the patch. Rebuild and
install again after verifying that the project still supports the game version.

## Development

```sh
python -m unittest discover -s tests
python scripts/release_audit.py
```

Bug reports should not attach generated patches, game files, crash dumps with
personal paths, or Steam account data.
