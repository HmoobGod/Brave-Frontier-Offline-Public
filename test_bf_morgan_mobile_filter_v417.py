"""Morgan Home/Quest map mobile and read-only completion filter regression."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "app/src/main/assets/bf080_morgan_map.js"

class MorganMobileFilterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js = SOURCE.read_text(encoding="utf-8")

    def test_mobile_pin_touch_target(self):
        self.assertIn("min-width:44px;min-height:44px", self.js)
        self.assertIn("@media(max-width:360px)", self.js)

    def test_toggle_has_accessible_state(self):
        self.assertIn("filterButton.setAttribute('aria-pressed','false')", self.js)
        self.assertIn("filterButton.setAttribute('aria-pressed',String(unclearedOnly))", self.js)
        self.assertIn("filterCount.setAttribute('aria-live','polite')", self.js)

    def test_filter_uses_real_clears_and_retains_locked_unfinished(self):
        self.assertIn("(P.questClears?.[q.missionId]||0)>0", self.js)
        self.assertIn("const show=!unclearedOnly || cleared<total", self.js)
        self.assertIn("pin.hidden=!show", self.js)
        self.assertIn("button.hidden=!show", self.js)
        self.assertIn("filterCount.textContent=visible+", self.js)

    def test_original_selection_still_uses_existing_quest_router(self):
        self.assertIn("BFQuestAreas.choose(target)", self.js)
        self.assertIn("questUnlocked(q)", self.js)

    def test_filter_does_not_mutate_save_or_economy(self):
        import re
        self.assertIsNone(re.search(r"\\b(?:P\\.(?:questClears|zel|karma|gems)\\s*=|saveGame\\s*\\(|localStorage\\.setItem\\s*\\()", self.js))

if __name__ == "__main__":
    unittest.main()
