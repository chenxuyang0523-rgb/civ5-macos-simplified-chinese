#!/usr/bin/env python3
"""Build a Mac Civ V Simplified Chinese text patch from official Steam depots."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree
from opencc import OpenCC

from build_fonts import build_font_assets


GAME_RELATIVE = Path("Contents/Assets/Assets")
DEFAULT_STEAM_ROOT = (
    Path.home()
    / "Library/Application Support/Steam/Steam.AppBundle/Steam/Contents/MacOS/steamapps/content/app_8930"
)
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "dist/Civ5_Simplified_Chinese_Mac"
TARGET_LANGUAGE_DIR = "ZH_Hant_HK"
TARGET_LANGUAGE_TYPE = "zh_Hant_HK"
TARGET_LANGUAGE_TABLE = "Language_ZH_HANT_HK"

DEPOT_LAYOUT = (
    (
        "depot_235586",
        Path("Assets/Gameplay/XML/NewText"),
        Path("Gameplay/XML/NewText"),
        "base",
    ),
    (
        "depot_16870",
        Path("Assets/DLC/Expansion/Gameplay/XML/Text"),
        Path("DLC/Expansion/Gameplay/XML/Text"),
        "gods_and_kings",
    ),
    (
        "depot_235580",
        Path("Assets/DLC/Expansion2/Gameplay/XML/Text"),
        Path("DLC/Expansion2/Gameplay/XML/Text"),
        "brave_new_world",
    ),
)


def convert_text(value: str, converter: OpenCC) -> str:
    """Convert only visible text while leaving Civ V control tokens untouched."""
    if not value or not re.search(r"[\u3400-\u9fff]", value):
        return value
    return converter.convert(value)


def rewrite_xml(source: Path, destination: Path, converter: OpenCC) -> int:
    parser = etree.XMLParser(remove_blank_text=False, strip_cdata=False, recover=False)
    tree = etree.parse(str(source), parser)
    converted = 0
    for element in tree.getroot().iter():
        if element.tag == "Text" and element.text:
            new_text = convert_text(element.text, converter)
            if new_text != element.text:
                converted += 1
                element.text = new_text
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree.write(
        str(destination),
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=False,
    )
    return converted


def rewrite_language_definition(source: Path, destination: Path) -> None:
    parser = etree.XMLParser(remove_blank_text=False, strip_cdata=False, recover=False)
    tree = etree.parse(str(source), parser)
    root = tree.getroot()
    for row in root.xpath("./Languages/Row"):
        for tag, value in (
            ("Type", TARGET_LANGUAGE_TYPE),
            ("Name", "简体中文（补丁）"),
            ("TableName", TARGET_LANGUAGE_TABLE),
        ):
            node = row.find(tag)
            if node is not None:
                node.text = value
        extended_font = row.find("UseExtendedFont")
        if extended_font is not None:
            # Reuse the Mac language table without asking for a missing image-font atlas.
            extended_font.text = "0"
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(destination), encoding="utf-8", xml_declaration=True, pretty_print=True)


def rewrite_credits(source: Path, destination: Path, converter: OpenCC) -> None:
    text = source.read_text(encoding="utf-8-sig")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(convert_text(text, converter), encoding="utf-8")


def copy_language_tree(source_root: Path, destination_root: Path, converter: OpenCC) -> tuple[int, int]:
    source_language = source_root / "ZH_Hant_HK"
    if not source_language.is_dir():
        raise FileNotFoundError(f"missing official language directory: {source_language}")
    xml_count = 0
    row_count = 0
    for source in sorted(source_language.rglob("*.xml")):
        destination = destination_root / TARGET_LANGUAGE_DIR / source.relative_to(source_language)
        row_count += rewrite_xml(source, destination, converter)
        xml_count += 1
    return xml_count, row_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--font",
        type=Path,
        help="local CJK font file used to generate private bitmap atlases",
    )
    parser.add_argument("--font-index", type=int, default=3, help="TTC face index (default: 3)")
    args = parser.parse_args()

    steam_root = args.steam_root.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    converter = OpenCC("t2s")
    depot_manifest = []
    total_xml = 0
    total_rows = 0
    for depot_name, relative_source, relative_destination, label in DEPOT_LAYOUT:
        depot = steam_root / depot_name
        if not depot.is_dir():
            raise FileNotFoundError(f"missing downloaded Steam depot: {depot}")
        destination_root = output / GAME_RELATIVE / relative_destination
        count, rows = copy_language_tree(depot / relative_source, destination_root, converter)
        total_xml += count
        total_rows += rows
        depot_manifest.append({"depot": depot_name, "label": label, "xml_files": count, "converted_rows": rows})

    base_xml = steam_root / "depot_235586/Assets/Gameplay/XML/NewText/Chinese.xml"
    rewrite_language_definition(
        base_xml,
        output / GAME_RELATIVE / "Gameplay/XML/NewText/Chinese.xml",
    )
    base_credits = steam_root / "depot_235586/Assets/Gameplay/XML/NewText/CIV5Credits_ZH_Hant_HK.txt"
    rewrite_credits(
        base_credits,
        output / GAME_RELATIVE / "Gameplay/XML/NewText/CIV5Credits_ZH_CN.txt",
        converter,
    )
    font_manifest = build_font_assets(output, args.font, args.font_index)

    manifest = {
        "name": "Civ V Mac Simplified Chinese Text Patch",
        "language": TARGET_LANGUAGE_TYPE,
        "source": "official Steam Chinese depot plus official Traditional Chinese expansion depots",
        "conversion": "OpenCC t2s",
        "font_mode": "custom-bitmap-atlas-dxt5",
        "font_assets": font_manifest,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "xml_files": total_xml,
        "converted_text_nodes": total_rows,
        "depots": depot_manifest,
    }
    (output / "patch-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
