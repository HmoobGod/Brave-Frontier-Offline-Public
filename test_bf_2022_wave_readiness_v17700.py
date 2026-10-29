"""v177: 142 archived missions, genuine source wave counts, no made-up formations."""
import json
import tempfile
from pathlib import Path
import prepare_bf_2022_wave_readiness_v177 as module

report = module.build_report()
assert report["missionCount"] == 142
assert report["playableDemoMissions"] == 106
assert report["sourceOnlyAmdahlMissions"] == 36
assert report["allAuthentic2022WaveDataReady"] is False
assert report["mutatesGameplay"] is False and report["mutatesSaves"] is False
assert report["sourceArchiveSha256"] == module.ZIP_SHA
assert report["sourceMissionMasterSha256"] == module.MISSION_SHA
rows = report["missions"]
assert len(rows) == 142 and len({row["missionId"] for row in rows}) == 142
assert len([row for row in rows if row["playability"] == "playable-demo"]) == 106
assert len([row for row in rows if row["playability"] == "source-only-not-playable"]) == 36
assert {row["missionId"] for row in rows if row["playability"] == "source-only-not-playable"} == set([*range(400, 405), *range(410, 415), *range(420, 425), *range(430, 435), *range(440, 445), *range(450, 455), *range(460, 466)])
assert all(type(row["sourceWaveCount"]) is int and row["sourceWaveCount"] > 0 for row in rows)
assert all(row["opaqueEncounterReference"].count(":") >= 1 for row in rows)
for row in rows:
    for key in ("nativeWaveFormationVerified", "nativeEnemyIdsVerified",
                "nativeAIVerified", "nativeDropsVerified"):
        assert row[key] is False, (row["missionId"], key)
assert report == module.build_report(), "read-only deterministic report changed"

# The scanned reference is an opaque mission *token*, not enemy ID or stage order.
ids = {row["missionId"]: row for row in rows}
assert ids[1]["sourceWaveCount"] == 3
assert ids[400]["sourceWaveCount"] == 8
assert ids[400]["opaqueEncounterReference"] == ids[404]["opaqueEncounterReference"]
assert ids[400]["nativeWaveFormationVerified"] is False
assert ids[1]["nativeWaveFormationVerified"] is False

with tempfile.TemporaryDirectory() as td:
    path = Path(td) / "out.json"
    text = json.dumps(report, sort_keys=True, ensure_ascii=False)
    path.write_text(text, encoding="utf8")
    assert json.loads(path.read_text(encoding="utf8")) == report

# Critical: the validation tool is a data-only report generator, not a patch.
source = (module.ROOT / "prepare_bf_2022_wave_readiness_v177.py").read_text(encoding="utf8")
for forbidden in ("MainActivity.java", "localStorage", "setItem(", "saveProgress(",
                  "awardDemoRewards(", "buildEncounter(", "app/build.gradle",
                  "bf_global_offline_demo_v7"):
    assert forbidden not in source, forbidden
print("PASS v177: 142 exact source missions, 106 DEMO/36 Amdahl separation, wave counts only, no native-formation claims or game mutation")
