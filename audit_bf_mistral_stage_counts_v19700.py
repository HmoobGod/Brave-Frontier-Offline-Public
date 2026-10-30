"""v197 read-only parity of 2021 Mistral stage counts and original 2022 mission data.

Historical stage-count consistency cannot authenticate 2022 enemy placements,
Mimic spawn rules, original enemy AI, rewards, or any playable battle behavior.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT / "source_data/bf_global_original_2022_live_quest_economy_v142.json"
HISTORICAL = ROOT / "source_data/bf_global_2021_mistral_mimic_history_v196.json"
OPAQUE = ROOT / "source_data/bf_global_mistral_raw_mission_evidence_v056.json"

ORIGINAL_BLOB = "9e9e98791d5a1ba04cdc095cf21fd46dfe5091fe"
HISTORICAL_BLOB = "321f0f8a2dec81340e23b0069b8f00e5783c9c57"
OPAQUE_BLOB = "87fe678b1fe70a041212fdf9050dfa4003072312"
ZIP2022 = "69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
MISSION2022 = "d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
COMMIT2021 = "7be4ee5ade8023580c83563fb306eb4e2b747256"
BLOB2021 = "750871aa060478cc674e7d3e02c739f26364ef8e"
TUPLES2022 = "a1b36659dfc80bc6e1e0e244ba52b3c6d423b239cf684439a5488bf679764a66"
EXPECTED_IDS = (1, 2, 10, 11, 12, 20, 21, 22, 23,
                30, 31, 32, 33, 40, 41, 42, 43, 50, 51, 52, 53,
                60, 61, 62, 63, 70, 71, 72, 73, 81, 82, 83, 84, 85)
COLUMNS = ["missionId", "missionDungeonId", "requiredMissionId",
           "missionBattleCount", "missionEnergyUse", "exp", "zel", "karma"]
ZERO = "0,0,0:0,0:0"
CANDIDATE = "1,10,100:1000,0:0"


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def compare_records(original, historical, opaque):
    """Comparison assumes bytes were pinned by compare(), never authorizes combat."""
    assert original["schema"] == "bf-global-original-2022-live-quest-economy-v142"
    assert original["year"] == 2022 and original["readOnly"] is True
    assert original["sourceArchiveSha256"] == ZIP2022
    assert original["missionMasterSha256"] == MISSION2022
    assert original["canonicalTupleSha256"] == TUPLES2022
    assert original["columns"] == COLUMNS and original["total"] == 106
    assert len(original["records"]) == 106
    now = {}
    for rec in original["records"]:
        assert type(rec) is list and len(rec) == 8
        assert all(type(v) is int and v >= 0 for v in rec)
        assert rec[0] not in now and rec[3] > 0
        now[rec[0]] = rec

    assert historical["schema"] == "bf-global-v196-2021-mistral-34-mission-historical-comparison"
    hs = historical["historicalSource"]
    assert (hs["repository"], hs["commit"], hs["blobGitSha1"], hs["sourceYear"]) == (
        "cheahjs/bravefrontier_data", COMMIT2021, BLOB2021, 2021)
    assert historical["original2022Source"]["archiveSha256"] == ZIP2022
    assert historical["original2022Source"]["missionMasterSha256"] == MISSION2022
    assert historical["matchedMissionIds"] == 34
    assert historical["noGameChanges"] is True
    assert historical["noPlayerSavesRead"] is True

    assert opaque["schema"] == "bf-global-2022-mistral-raw-mission-evidence-v056"
    assert opaque["source"]["archiveSha256"] == ZIP2022
    assert opaque["source"]["fileSha256"] == MISSION2022
    older = {}
    for row in historical["observations"]:
        ident = row["missionId"]
        assert type(ident) is int and ident not in older
        older[ident] = row
    raw = {}
    for row in opaque["rows"]:
        ident = row["missionId"]
        assert type(ident) is int and ident not in raw
        raw[ident] = row
    assert tuple(sorted(older)) == tuple(sorted(raw)) == EXPECTED_IDS

    counts = Counter()
    matches = []
    for ident in EXPECTED_IDS:
        src = now[ident]
        prev = older[ident]
        clue = raw[ident]
        assert prev["old2021Area"] == "Mistral"
        assert type(prev["old2021BattleCount"]) is int and prev["old2021BattleCount"] >= 1
        assert prev["old2021BattleCount"] == src[3], (ident, prev["old2021BattleCount"], src[3])
        assert isinstance(clue["rawEncounterRef"], str) and clue["rawEncounterRef"]
        cls = {ZERO: "empty", CANDIDATE: "candidate1000"}.get(clue["rawMimicInfo"])
        assert cls is not None
        counts[cls] += 1
        matches.append({
            "missionId": ident,
            "original2022BattleStageCount": src[3],
            "historical2021BattleStageCount": prev["old2021BattleCount"],
            "countsMatch": True,
            "raw2022MimicTokenClass": cls,
            "raw2022EncounterToken": clue["rawEncounterRef"],
            "native2022EnemyRosterVerified": False,
            "native2022MimicTimingVerified": False,
            "changesGame": False,
        })
    assert dict(counts) == {"empty": 21, "candidate1000": 13}
    return {
        "schema": "bf-global-v197-readonly-2021-2022-mistral-stage-count-parity",
        "year2021": 2021,
        "year2022": 2022,
        "original2022ArchiveSha256": ZIP2022,
        "original2022MissionMasterSha256": MISSION2022,
        "historical2021SourceCommit": COMMIT2021,
        "historical2021GitBlobSha1": BLOB2021,
        "authenticated2022MissionsInFixture": 106,
        "mistralMissionsCompared": len(matches),
        "stageCountMatches": len(matches),
        "mimicTokenClasses": dict(counts),
        "native2022EnemyFormationsAuthenticated": False,
        "native2022MimicSpawnsAuthenticated": False,
        "native2022EnemyAIAuthenticated": False,
        "native2022DropsAuthenticated": False,
        "modifiesAndroid": False,
        "modifiesSaves": False,
        "rows": matches,
    }


def compare():
    paths = ((ORIGINAL, ORIGINAL_BLOB), (HISTORICAL, HISTORICAL_BLOB),
             (OPAQUE, OPAQUE_BLOB))
    inputs = []
    for path, expected in paths:
        raw = path.read_bytes()
        assert git_blob(raw) == expected, "Pinned source fixture bytes changed: " + path.name
        inputs.append(json.loads(raw))
    return compare_records(*inputs)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Research JSON output outside project")
    args = parser.parse_args()
    result = compare()
    if args.output is None:
        print("PASS v197: 34/34 2021-to-2022 Mistral battle-stage counts match; research only")
        print("No 2022 enemy formations, Mimic timing, AI, loot, APK or save changes.")
        return
    target = args.output.resolve()
    assert not target.is_relative_to(ROOT.resolve()), "Writing inside repository is forbidden"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")


if __name__ == "__main__":
    main()
