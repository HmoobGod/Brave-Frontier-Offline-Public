"""Regression guards for player-only unit box visibility filters."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "app/src/main/assets/bf10200_qol_unit_flags.js"

class UnitBoxFilterSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_filters_are_explicit_and_reversible(self):
        s = self.source
        self.assertIn("let filterMode='all'", s)
        self.assertIn("['all','favorites','locked'].includes(mode)", s)
        self.assertIn("filterMode==='favorites'?'all':'favorites'", s)
        self.assertIn("filterMode==='locked'?'all':'locked'", s)

    def test_visibility_is_only_a_view_change(self):
        s = self.source
        self.assertIn("card.hidden=!visible", s)
        self.assertIn("card.style.display=visible?'':'none'", s)
        self.assertIn("flags.favorites.includes(id)", s)
        self.assertIn("flags.locked.includes(id)", s)
        self.assertIn("filterInfo.textContent=shown+' of '+total", s)
        segment=s.split("function setFilter(mode){",1)[1].split("showFavorites.addEventListener",1)[0]
        self.assertNotIn("saveProgress(",segment)
        self.assertNotIn("localStorage.setItem(",segment)
        self.assertNotIn("P.roster=",segment)

    def test_favorite_and_lock_persistence_uses_both_arrays(self):
        s = self.source
        self.assertIn("bf_global_offline_qol_unit_flags_v102",s)
        self.assertIn("function change(id,kind,on)",s)
        self.assertIn("if(!write(next.favorites,next.locked))return false",s)
        self.assertNotIn("write(next.favorites,next.lock)",s)
        self.assertNotIn("bf_global_offline_demo_v7",s)

if __name__ == "__main__":
    unittest.main()
