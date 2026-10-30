"""v197 Mistral 2021/2022 stage-count parity and strict source isolation."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile

R = Path(__file__).resolve().parent
SCRIPT = R / "audit_bf_mistral_stage_counts_v19700.py"
ORIGINAL = R / "source_data/bf_global_original_2022_live_quest_economy_v142.json"
HISTORY = R / "source_data/bf_global_2021_mistral_mimic_history_v196.json"
OPAQUE = R / "source_data/bf_global_mistral_raw_mission_evidence_v056.json"
APP = R / "app/src/main/assets/index.html"
files = (SCRIPT, ORIGINAL, HISTORY, OPAQUE, APP)
before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
spec = importlib.util.spec_from_file_location("bf_v197", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
result = audit.compare()
assert result["schema"] == "bf-global-v197-readonly-2021-2022-mistral-stage-count-parity"
assert result["authenticated2022MissionsInFixture"] == 106
assert result["mistralMissionsCompared"] == result["stageCountMatches"] == 34
assert result["mimicTokenClasses"] == {"empty": 21, "candidate1000": 13}
assert len(result["rows"]) == 34
assert [r["missionId"] for r in result["rows"]] == list(audit.EXPECTED_IDS)
assert all(r["countsMatch"] and not r["native2022EnemyRosterVerified"]
           and not r["native2022MimicTimingVerified"] and not r["changesGame"]
           for r in result["rows"])
known = {r["missionId"]: r["original2022BattleStageCount"] for r in result["rows"]}
assert {i: known[i] for i in (1, 12, 60, 63, 85)} == {
    1: 3, 12: 6, 60: 6, 63: 7, 85: 8}
assert not any(result[k] for k in (
    "native2022EnemyFormationsAuthenticated", "native2022MimicSpawnsAuthenticated",
    "native2022EnemyAIAuthenticated", "native2022DropsAuthenticated",
    "modifiesAndroid", "modifiesSaves"))
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "stage_counts.json"
    cmd = [sys.executable, str(SCRIPT), "--output", str(out)]
    subprocess.run(cmd, check=True, cwd=R)
    first = out.read_bytes()
    assert json.loads(first) == result
    subprocess.run(cmd, check=True, cwd=R)
    assert out.read_bytes() == first
    summary = subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=R,
                             capture_output=True, text=True)
    assert "34/34" in summary.stdout and "research only" in summary.stdout
    internal = R / "DO_NOT_CREATE_v197.json"
    bad = subprocess.run([sys.executable, str(SCRIPT), "--output", str(internal)],
                         cwd=R, capture_output=True, text=True)
    assert bad.returncode and not internal.exists()
    src = json.loads(ORIGINAL.read_text("utf8"))
    hist = json.loads(HISTORY.read_text("utf8"))
    opaque = json.loads(OPAQUE.read_text("utf8"))
    def reject(index, edit):
        args = [copy.deepcopy(src), copy.deepcopy(hist), copy.deepcopy(opaque)]
        edit(args[index])
        try:
            audit.compare_records(*args)
        except (AssertionError, KeyError, TypeError, ValueError):
            return
        raise AssertionError("Corrupt original or historical data was accepted")
    reject(0, lambda d: next(row for row in d["records"] if row[0] == 85).__setitem__(3, 9))
    reject(0, lambda d: d["records"][1].__setitem__(0, 1))
    reject(0, lambda d: d.update(sourceArchiveSha256="0" * 64))
    reject(0, lambda d: d.update(columns=list(reversed(d["columns"]))))
    reject(1, lambda d: d["observations"][0].update(old2021BattleCount=4))
    reject(1, lambda d: d["observations"][0].update(missionId=2))
    reject(1, lambda d: d["historicalSource"].update(commit="0" * 40))
    reject(1, lambda d: d["observations"][0].update(old2021Area="Other region"))
    reject(2, lambda d: d["rows"][0].update(rawEncounterRef=""))
    reject(2, lambda d: d["rows"][0].update(rawMimicInfo="unproven native group"))
assert before == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
assert "bf_global_offline_demo_v7" in APP.read_text("utf8")
print("PASS v197: 34 exact Mistral stage-count matches, 10 negative data probes; no save or APK edits")
