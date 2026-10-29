"""v177: original-source 2022 mission readiness ledger; never decode native waves.

Read-only: source-pinned quest count, opaque encounter reference, and verification
gaps. This does not create monsters, grant rewards, or change an Android build.
"""
from pathlib import Path
import argparse
import json

from audit_bf_original_2022_wave_sources_v17500 import pinned_refs, ZIP_SHA, MISSION_SHA

ROOT = Path(__file__).resolve().parent
ECONOMY = ROOT / "source_data/bf_global_original_2022_live_quest_economy_v142.json"
AMDAHL = ROOT / "source_data/bf_global_2022_amdahl_quest_readiness_v147.json"

def build_report(root=ROOT):
    root = Path(root)
    refs = pinned_refs(root)
    economy = json.loads((root / "source_data/bf_global_original_2022_live_quest_economy_v142.json").read_text(encoding="utf-8"))
    amdahl = json.loads((root / "source_data/bf_global_2022_amdahl_quest_readiness_v147.json").read_text(encoding="utf-8"))
    if not (economy.get("readOnly") is True and economy.get("year") == 2022
            and economy.get("sourceArchiveSha256") == ZIP_SHA
            and economy.get("missionMasterSha256") == MISSION_SHA
            and economy.get("total") == 106):
        raise ValueError("v142 source provenance/count mismatch")
    ap = amdahl.get("provenance", {})
    if not (ap.get("mstZipSha256") == ZIP_SHA
            and ap.get("missionTableSha256") == MISSION_SHA
            and amdahl.get("area", {}).get("playableNow") is False
            and amdahl.get("area", {}).get("originalEnemyWavesDecoded") is False
            and amdahl.get("area", {}).get("missionCount") == 36):
        raise ValueError("v147 Amdahl source provenance/state mismatch")
    if economy.get("columns") != [
            "missionId", "missionDungeonId", "requiredMissionId",
            "missionBattleCount", "missionEnergyUse", "exp", "zel", "karma"]:
        raise ValueError("unexpected v142 mission tuple schema")
    wave_counts = {}
    for row in economy["records"]:
        if (not isinstance(row, list) or len(row) != 8
                or not isinstance(row[0], int) or isinstance(row[0], bool)
                or not isinstance(row[3], int) or isinstance(row[3], bool)
                or row[3] < 1 or row[0] in wave_counts):
            raise ValueError("duplicate/malformed playable mission")
        wave_counts[row[0]] = {"waveCount": row[3], "status": "playable-demo"}
    if len(wave_counts) != 106:
        raise ValueError("expected exactly 106 playable original missions")
    for q in amdahl["quests"]:
        if (not isinstance(q, dict) or type(q.get("id")) is not int
                or type(q.get("waveCount")) is not int
                or q["waveCount"] < 1 or q["id"] in wave_counts):
            raise ValueError("duplicate/malformed Amdahl source mission")
        if refs.get(q["id"]) != q.get("rawEncounterRef"):
            raise ValueError("Amdahl opaque encounter ref differs from pinned v152")
        wave_counts[q["id"]] = {
            "waveCount": q["waveCount"], "status": "source-only-not-playable"}
    if (len(amdahl["quests"]) != 36 or len(wave_counts) != 142
            or set(wave_counts) != set(refs)):
        raise ValueError("142 mission roster does not match pinned v152 refs")
    rows = []
    for mid in sorted(refs):
        entry = wave_counts[mid]
        rows.append({"missionId": mid, "sourceWaveCount": entry["waveCount"],
                     "opaqueEncounterReference": refs[mid],
                     "playability": entry["status"],
                     "nativeWaveFormationVerified": False,
                     "nativeEnemyIdsVerified": False,
                     "nativeAIVerified": False,
                     "nativeDropsVerified": False})
    return {
        "schema": "bf-global-2022-mission-wave-readiness-v177",
        "scope": "source-backed wave counts ONLY; no original ordered wave contents",
        "sourceArchiveSha256": ZIP_SHA,
        "sourceMissionMasterSha256": MISSION_SHA,
        "missionCount": 142, "playableDemoMissions": 106,
        "sourceOnlyAmdahlMissions": 36,
        "original2022FormationCountVerified": 0,
        "original2022AIProfilesVerified": 0,
        "original2022DropsVerified": 0,
        "allAuthentic2022WaveDataReady": False,
        "mutatesGameplay": False, "mutatesSaves": False,
        "missions": rows,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional local JSON output path")
    args = parser.parse_args()
    report = build_report()
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                               encoding="utf-8")
        print("Source-only 142-mission readiness report:", args.output)
    else:
        print(json.dumps({k: v for k, v in report.items() if k != "missions"},
                         sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
