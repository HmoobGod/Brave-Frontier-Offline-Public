#!/usr/bin/env python3
"""v415 original 2022 quest Energy discovery — source-backed, no stamina use."""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "app/src/main/assets/bf14300_original_quest_energy.js"
MASTER = ROOT / "source_data/bf_global_original_2022_live_quest_economy_v142.json"

class QuestEnergyFilterV415(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.master = json.loads(MASTER.read_text(encoding="utf-8"))
        start = cls.source.index("const records=") + len("const records=")
        cls.records, _ = json.JSONDecoder().raw_decode(cls.source[start:])

    def test_original_campaign_identity_and_coverage(self):
        s = self.source
        self.assertEqual(self.master["year"], 2022)
        self.assertEqual(self.master["total"], 106)
        self.assertIn(self.master["canonicalTupleSha256"], s)
        self.assertEqual(self.records, self.master["records"])
        self.assertEqual(len(self.records), 106)
        self.assertEqual(len({r[0] for r in self.records}), 106)
        self.assertTrue(all(len(r) == 8 and all(type(v) is int and v >= 0 for v in r)
                            for r in self.records))
        self.assertIn("records.length!==106", s)
        self.assertIn("indexed.size!==106||known.size!==106", s)
        self.assertIn("staminaEnforced:false,saveMutation:false", s)

    def test_filter_ranges_cover_106_records_without_overlap(self):
        s = self.source
        for token in ("case '0':return cost===0",
                      "case '1-3':return cost>=1&&cost<=3",
                      "case '4-6':return cost>=4&&cost<=6",
                      "case '7+':return cost>=7",
                      "default:return true"):
            self.assertIn(token, s)
        groups = [
            [r for r in self.records if r[4] == 0],
            [r for r in self.records if 1 <= r[4] <= 3],
            [r for r in self.records if 4 <= r[4] <= 6],
            [r for r in self.records if r[4] >= 7],
        ]
        self.assertEqual(sum(map(len, groups)), 106)
        self.assertTrue(all(group for group in groups))

    def test_clear_accessibility_and_no_stamina_logic(self):
        s = self.source
        self.assertIn("range.value='all';decorate();range.focus();", s)
        self.assertIn("button.hidden=!matchesEnergy(r[4])", s)
        self.assertIn("button.questcard[hidden]{display:none!important}", s)
        self.assertIn("min-height:44px", s)
        self.assertIn("font-size:16px", s)
        self.assertIn("aria-live','polite", s)
        self.assertNotRegex(s, r"\b(?:P|S)\.[A-Za-z_$][\w$]*\s*=")
        self.assertNotIn("localStorage", s)
        self.assertNotIn("saveProgress(", s)

if __name__ == "__main__":
    unittest.main()
