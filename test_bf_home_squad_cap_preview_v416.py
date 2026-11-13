#!/usr/bin/env python3
"""Static safety and source-backed Home squad cap preview regression."""
from pathlib import Path
import unittest

SOURCE=Path(__file__).resolve().parent/"app/src/main/assets/bf11500_original_unit_level_caps.js"

class SquadCapPreview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=SOURCE.read_text(encoding="utf-8")
    def test_ownership_and_slots(self):
        for token in ("Math.min(6,P.squad.length)","P.roster.includes(baseId)","effectiveUnit(baseId)","lookup(unit.id)","demoLevel(P.unitExp?.[baseId])"):
            self.assertIn(token,self.s)
    def test_read_only_and_original_provenance(self):
        for token in ("original 2022 max-level field","No EXP, training, roster or save changes","unitMaxLevel","original cap"):
            self.assertIn(token,self.s)
        self.assertNotIn("P.unitExp[baseId]=",self.s)
    def test_mobile_accessible_preview(self):
        for token in ("bf11300-squad-cap-preview","aria-label','Current squad original level caps","squadPreview.replaceChildren()","No eligible owned squad forms"):
            self.assertIn(token,self.s)

if __name__=="__main__":
    unittest.main()
