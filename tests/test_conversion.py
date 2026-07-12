import tempfile
import unittest
from pathlib import Path

from lxml import etree
from opencc import OpenCC

from build_patch import convert_text, rewrite_xml


class ConversionTests(unittest.TestCase):
    def test_converts_traditional_text_and_preserves_tokens(self):
        value = "建立[COLOR_POSITIVE_TEXT]城市[ENDCOLOR]"
        converted = convert_text(value, OpenCC("t2s"))
        self.assertEqual(converted, "建立[COLOR_POSITIVE_TEXT]城市[ENDCOLOR]")

    def test_rewrites_only_text_elements(self):
        source_xml = """<?xml version=\"1.0\"?><GameData><Rows><Row><Tag>城市</Tag><Text>選擇城市</Text></Row></Rows></GameData>"""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.xml"
            destination = Path(directory) / "destination.xml"
            source.write_text(source_xml, encoding="utf-8")
            count = rewrite_xml(source, destination, OpenCC("t2s"))
            root = etree.parse(str(destination)).getroot()
            self.assertEqual(count, 1)
            self.assertEqual(root.findtext(".//Tag"), "城市")
            self.assertEqual(root.findtext(".//Text"), "选择城市")


if __name__ == "__main__":
    unittest.main()
