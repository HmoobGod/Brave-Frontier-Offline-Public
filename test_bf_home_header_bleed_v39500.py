"""Static regression guard for the original Global Home header narrow-width bleed.

Run: python -m unittest test_bf_home_header_bleed_v39500.py
This is a source guard only, NOT a Chromium viewport or Android acceptance test.
"""
from pathlib import Path
import re
import unittest

CSS = Path(__file__).with_name("app").joinpath("src/main/assets/bf_home_nav.css")

class HomeHeaderBleedSourceTest(unittest.TestCase):
    def test_original_art_preserved_and_margin_reduced(self):
        css = CSS.read_text(encoding="utf-8")
        matches = re.findall(r"\.bf-shell-head\s*\{([^}]*)\}", css, flags=re.S)
        self.assertGreaterEqual(len(matches), 2)
        original_art = next((rule for rule in matches if "header_ui3.png" in rule), "")
        self.assertTrue(original_art, "original recovered header art must remain")
        self.assertIn("aspect-ratio:644/206", original_art)
        self.assertIn("box-sizing:border-box", original_art)
        self.assertIn("margin:0 -7px 7px", original_art)
        self.assertNotIn("margin:0 -8px 7px", original_art)
        self.assertIn('content/header/header_ui3.png', original_art)

if __name__ == "__main__":
    unittest.main()
