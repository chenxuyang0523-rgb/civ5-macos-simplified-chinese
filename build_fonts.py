#!/usr/bin/env python3
"""Generate loose Civ V bitmap font atlases for the translated text."""

from __future__ import annotations

import subprocess
from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFont


FONT_SIZES = (14, 16, 18, 20, 22, 24)
ATLAS_SIZE = 2048
FONT_DIR = Path("Contents/Assets/Assets/UI/Fonts/Tw Cent MT")


def find_pingfang() -> Path:
    try:
        path = subprocess.check_output(
            ["fc-match", "-f", "%{file}\\n", "PingFang SC"],
            text=True,
        ).strip()
        if path:
            return Path(path)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    fallback = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
    if fallback.is_file():
        return fallback
    raise FileNotFoundError("could not locate a macOS CJK font")


def collect_characters(patch_root: Path) -> list[str]:
    characters = {chr(code) for code in range(32, 127)}
    for source in patch_root.rglob("*.xml"):
        root = etree.parse(str(source)).getroot()
        for element in root.iter("Text"):
            if element.text:
                characters.update(element.text)
    credits = patch_root / "Contents/Assets/Assets/Gameplay/XML/NewText/CIV5Credits_ZH_CN.txt"
    if credits.is_file():
        characters.update(credits.read_text(encoding="utf-8", errors="ignore"))
    return sorted(
        char
        for char in characters
        if ord(char) <= 0xFFFF and char not in {"\n", "\r", "\t", "\ufeff"}
    )


def write_dds(image: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGBA").save(destination, format="DDS", pixel_format="DXT5")


def make_ggxml(size: int, glyphs: list[dict[str, int]], destination: Path) -> None:
    texture = f"TwCenMT{size}CJK.dds"
    ascent = max(1, round(size * 0.8))
    descent = max(1, size - ascent)
    lines = [
        '<?xml version="1.0" encoding="UTF-8" ?>',
        "<glyphgen>",
        f'    <textures width="{ATLAS_SIZE}" height="{ATLAS_SIZE}">',
        f'        <texture name="" src="{texture}" allowcolor="1" alloweffects="1" inuse="1" />',
        "    </textures>",
        '    <styles count="6">',
    ]
    for style in ("", "Base", "Shadow", "Stroke", "Soft", "SoftShadow"):
        lines.extend(
            [
                f'        <style name="{style}">',
                '            <layers count="1">',
                '                <layer tex="" />',
                "            </layers>",
                "        </style>",
            ]
        )
    lines.extend(
        [
            "    </styles>",
            f'    <glyphs fudgeadv="0" ascadj="2" spacing="6" count="{len(glyphs)}" height="{size}" ascent="{ascent}" descent="{descent}">',
        ]
    )
    for glyph in glyphs:
        attrs = " ".join(f'{key}="{glyph[key]}"' for key in (
            "ch", "u", "v", "width", "height", "a", "b", "c", "originx", "originy"
        ))
        lines.append(f"        <glyph {attrs} />")
    lines.extend(["    </glyphs>", "    <imports count=\"0\" />", "</glyphgen>", ""])
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8")


def build_font_assets(
    patch_root: Path,
    font_path: Path | None = None,
    font_index: int = 3,
) -> dict[str, object]:
    font_path = (font_path or find_pingfang()).expanduser().resolve()
    if not font_path.is_file():
        raise FileNotFoundError(f"font not found: {font_path}")
    characters = collect_characters(patch_root)
    output_dir = patch_root / FONT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}

    for size in FONT_SIZES:
        font = ImageFont.truetype(str(font_path), size, index=font_index)
        ascent, descent = font.getmetrics()
        cell = size + 8
        columns = ATLAS_SIZE // cell
        rows = (len(characters) + columns - 1) // columns
        if rows > ATLAS_SIZE // cell:
            raise RuntimeError(f"font atlas is too small for {len(characters)} glyphs at size {size}")
        image = Image.new("RGBA", (ATLAS_SIZE, ATLAS_SIZE), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        glyphs = []
        for index, char in enumerate(characters):
            advance = max(1, round(font.getlength(char)))
            if char == " ":
                glyphs.append({"ch": ord(char), "u": 0, "v": 0, "width": 0, "height": 0,
                               "a": 0, "b": advance, "c": 0, "originx": 0, "originy": 0})
                continue
            bbox = font.getbbox(char, anchor="ls")
            column, row = index % columns, index // columns
            cell_x, cell_y = column * cell, row * cell
            pad = 4
            origin_x, origin_y = bbox[0], -bbox[1]
            draw_x = cell_x + pad - bbox[0]
            baseline_y = cell_y + pad - bbox[1]
            draw.text((draw_x, baseline_y), char, font=font, anchor="ls", fill=(255, 255, 255, 255))
            glyphs.append({
                "ch": ord(char),
                "u": cell_x + pad,
                "v": cell_y + pad,
                "width": max(0, bbox[2] - bbox[0]),
                "height": max(0, bbox[3] - bbox[1]),
                "a": origin_x,
                "b": advance,
                "c": 0,
                "originx": origin_x,
                "originy": origin_y,
            })
        write_dds(image, output_dir / f"TwCenMT{size}CJK.dds")
        make_ggxml(size, glyphs, output_dir / f"TwCenMT{size}.ggxml")
        counts[str(size)] = len(glyphs)
    return {
        "font_source": "user-local; not distributed",
        "font_file_name": font_path.name,
        "font_index": font_index,
        "atlas_size": ATLAS_SIZE,
        "glyphs": len(characters),
        "by_size": counts,
    }


if __name__ == "__main__":
    import json
    import sys

    print(json.dumps(build_font_assets(Path(sys.argv[1]).resolve()), ensure_ascii=False, indent=2))
