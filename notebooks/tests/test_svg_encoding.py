"""SVG transport encoding regression, not evidence or usability validation."""
import unittest
import xml.etree.ElementTree as ET
from workbench.presentation import workflow_map, View

class SVGEncodingTests(unittest.TestCase):
    def test_ascii_transport_retains_exact_xml_text(self):
        view = workflow_map()
        encoded = view._repr_mimebundle_()["image/svg+xml"]
        self.assertTrue(encoded.isascii())
        self.assertEqual(list(ET.fromstring(view.svg).itertext()),
                         list(ET.fromstring(encoded).itertext()))
        self.assertEqual(view._repr_mimebundle_()["text/plain"], view.text)

    def test_symbols_and_escaping_preserved(self):
        view = View("→ • ↔", svg='<svg xmlns="http://www.w3.org/2000/svg"><text>→ • ↔ &amp; café</text></svg>')
        bundle = view._repr_mimebundle_()
        self.assertEqual(''.join(ET.fromstring(bundle["image/svg+xml"]).itertext()), "→ • ↔ & café")
        self.assertEqual(bundle["text/plain"], "→ • ↔")
