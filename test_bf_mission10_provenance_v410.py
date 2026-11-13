"""Mission #10 provenance and strictly isolated 2014 practice-data regression."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import unittest

import audit_bf_mission10_provenance_v410 as m

ROOT = Path(__file__).resolve().parent


class Mission10ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.docs = [
            json.loads((ROOT / m.SOURCES[k]).read_text(encoding="utf-8"))
            for k in ("historical", "economy", "english", "manifest", "donor")
        ]

    def audit(self):
        return m.build_snapshot(*self.docs)

    def test_baseline_exact_sources_and_separate_practice(self):
        result = self.audit()
        audit, adapter = result["audit"], result["practiceAdapter"]
        self.assertEqual((audit["missionId"], audit["historical"]["waves"],
                          audit["historical"]["enemySlots"]), (10, 5, 11))
        self.assertEqual(audit["historical"]["name"], "Start of Adventure")
        self.assertEqual(audit["donor"]["sourceMethod"], "captured")
        self.assertFalse(audit["donor"]["isSameCaptureAsOurs"])
        self.assertFalse(audit["donor"]["fullMissionRecordInspected"])
        self.assertFalse(audit["donor"]["waveEnemyStatParityEstablished"])
        self.assertTrue(audit["original2022"]["battleCountVerified"])
        for key in ("orderedFormationsVerified", "enemyAiVerified", "dropsVerified"):
            self.assertIs(audit["original2022"][key], False)
        self.assertFalse(audit["native2022CampaignUseAuthorized"])
        self.assertEqual(adapter["scope"], "historical-2014-practice-only")
        self.assertTrue(adapter["notOriginal2022"])
        self.assertFalse(adapter["runtimeConnected"])
        self.assertEqual(len(adapter["waves"]), 5)
        self.assertEqual([len(w["enemies"]) for w in adapter["waves"]], [2, 3, 2, 3, 1])
        self.assertEqual(adapter["waves"][-1]["enemies"][0]["name"], "King Sparky")
        for forbidden in ("mayStartCanonicalQuest", "mayGrantRewards",
                          "mayWriteV7Save", "mayModifyEnemyOrPartnerAI"):
            self.assertFalse(adapter[forbidden])
        self.assertNotIn("questClears", json.dumps(adapter))
        self.assertNotIn("bf_global_offline_demo_v7", json.dumps(adapter))

    def test_bad_2014_capture_identity_fails_closed(self):
        self.docs[0]["missions"][2]["gitBlobSha"] = "0" * 40
        with self.assertRaises(m.ProvenanceError):
            self.audit()

    def test_2022_wave_count_divergence_fails_closed(self):
        self.docs[1]["records"][2][3] = 4
        with self.assertRaises(m.ProvenanceError):
            self.audit()

    def test_2022_reward_drift_fails_closed(self):
        self.docs[3]["quests"][2]["zel"] += 1
        with self.assertRaises(m.ProvenanceError):
            self.audit()

    def test_2022_english_name_drift_fails_closed(self):
        self.docs[2]["missions"][2]["name"] = "Unverified Mission"
        with self.assertRaises(m.ProvenanceError):
            self.audit()

    def test_mismatched_donor_capture_rejected(self):
        self.docs[4]["mission10"]["source"] = "Start of Adventure_2022.json"
        with self.assertRaises(m.ProvenanceError):
            self.audit()

    def test_missing_historical_enemy_rejected(self):
        self.docs[0]["missions"][2]["waves"][0]["enemies"] = []
        with self.assertRaises(m.ProvenanceError):
            self.audit()

    def test_invalid_enemy_hp_rejected(self):
        self.docs[0]["missions"][2]["waves"][0]["enemies"][0]["hp"] = 0
        with self.assertRaises(m.ProvenanceError):
            self.audit()

    def test_no_mutation_even_if_adapter_is_modified(self):
        baseline = deepcopy(self.docs)
        a = self.audit()
        a["practiceAdapter"]["waves"][0]["enemies"][0]["hp"] = 1
        self.assertEqual(self.docs, baseline)
        self.assertEqual(self.audit()["practiceAdapter"]["waves"][0]
                         ["enemies"][0]["hp"], 830)

    def test_existing_practice_separate_from_campaign(self):
        src = (ROOT / "app/src/main/assets/bf200_historical_wave_lab.js").read_text("utf-8")
        self.assertIn("START SEPARATE PRACTICE", src)
        self.assertIn("No quest clears, drops, summons, EXP, Zel or save changes.", src)
        self.assertIn("PRACTICE COMPLETE. No game progress or rewards granted.", src)
        self.assertIn("function startPractice(", src)
        self.assertNotIn("localStorage", (ROOT / "audit_bf_mission10_provenance_v410.py").read_text("utf-8"))
        self.assertNotIn("saveProgress(", (ROOT / "audit_bf_mission10_provenance_v410.py").read_text("utf-8"))

    def test_cli_prints_report_without_writing(self):
        paths = [ROOT / p for p in m.SOURCES.values()]
        before = {str(p): p.read_bytes() for p in paths}
        completed = subprocess.run(
            [sys.executable, str(ROOT / "audit_bf_mission10_provenance_v410.py")],
            cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads(completed.stdout)
        self.assertFalse(report["audit"]["native2022CampaignUseAuthorized"])
        self.assertEqual(before, {str(p): p.read_bytes() for p in paths})


if __name__ == "__main__":
    unittest.main()
