"""v196 read-only 2021-to-2022 Mistral mimic-data cross-era comparison.

This compares literal source tokens and historical field values; matching
numbers DO NOT authenticate the field semantics or any enemy spawn/AI/waves.
"""
from pathlib import Path
from argparse import ArgumentParser
from collections import Counter
import hashlib
import json

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"source_data/bf_global_mistral_raw_mission_evidence_v056.json"
HIST=ROOT/"source_data/bf_global_2021_mistral_mimic_history_v196.json"
ZIP2022="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
MISSION2022="d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
BLOB2021="750871aa060478cc674e7d3e02c739f26364ef8e"
COMMIT2021="7be4ee5ade8023580c83563fb306eb4e2b747256"
FIXTURE_SOURCE_GIT_BLOB="87fe678b1fe70a041212fdf9050dfa4003072312"
FIXTURE_HISTORY_GIT_BLOB="321f0f8a2dec81340e23b0069b8f00e5783c9c57"
ZERO2022="0,0,0:0,0:0"
CANDIDATE2022="1,10,100:1000,0:0"
CANDIDATE_2021={
    "group_1_chance":"100",
    "group_1_monster_group":"1000",
    "group_2_chance":"0",
    "group_2_monster_group":"0",
    "spawn_chance_range_maybe":"10.0~34.0"
}

def _git_blob_sha(raw):
    """Anchor in-repository fixtures to their exact reviewed Git bytes."""
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()

def compare():
    source_bytes=SOURCE.read_bytes()
    history_bytes=HIST.read_bytes()
    assert _git_blob_sha(source_bytes)==FIXTURE_SOURCE_GIT_BLOB, "2022 fixture bytes changed"
    assert _git_blob_sha(history_bytes)==FIXTURE_HISTORY_GIT_BLOB, "2021 fixture bytes changed"
    original=json.loads(source_bytes)
    history=json.loads(history_bytes)
    assert original["schema"]=="bf-global-2022-mistral-raw-mission-evidence-v056"
    assert original["source"]["archiveSha256"]==ZIP2022
    assert original["source"]["fileSha256"]==MISSION2022
    assert len(original["rows"])==34
    assert history["schema"]=="bf-global-v196-2021-mistral-34-mission-historical-comparison"
    hs=history["historicalSource"]
    assert (hs["repository"],hs["commit"],hs["blobGitSha1"])==(
        "cheahjs/bravefrontier_data",COMMIT2021,BLOB2021)
    assert hs["commitDate"]=="2021-11-17" and hs["sourceYear"]==2021
    assert hs["file"]=="missions.json"
    assert hs["totalHistoricalMissionIds"]==3146
    ns=history["original2022Source"]
    assert ns["archiveSha256"]==ZIP2022 and ns["missionMasterSha256"]==MISSION2022
    assert ns["sourceRows"]==34 and ns["field"]=="rawMimicInfo"
    assert history["matchedMissionIds"]==34
    assert history["original2022MimicClasses"]=={
        "empty":21,"candidate1000":13}
    assert history["noPlayerSavesRead"] is True and history["noGameChanges"] is True
    limits=history["assumptions"]
    assert len(limits)==6 and all(value is False for value in limits.values())
    older={row["missionId"]:row for row in history["observations"]}
    now={row["missionId"]:row for row in original["rows"]}
    assert len(older)==len(now)==34 and set(older)==set(now)
    expected=(
       1,2,10,11,12,20,21,22,23,30,31,32,33,
       40,41,42,43,50,51,52,53,60,61,62,63,
       70,71,72,73,81,82,83,84,85)
    assert tuple(sorted(older))==expected
    counts=Counter()
    matches=[]
    for id in sorted(now):
        source=now[id]
        old=older[id]
        assert source["missionId"]==old["missionId"]==id
        assert old["old2021Area"]=="Mistral"
        assert isinstance(old["old2021Name"],str) and old["old2021Name"]
        assert isinstance(old["old2021Dungeon"],str) and old["old2021Dungeon"]
        assert type(old["old2021BattleCount"]) is int and old["old2021BattleCount"]>=1
        # MISSION_8f4NYKxb is an opaque 2022 token. We do not reinterpret it.
        assert isinstance(source["rawEncounterRef"],str) and source["rawEncounterRef"]
        assert isinstance(source["rawMimicInfo"],str)
        mimic=old["old2021MimicRaw"]
        if source["rawMimicInfo"]==ZERO2022:
            assert mimic=={},("2021 zero-mimic mismatch",id,mimic)
            cls="empty"
        else:
            assert source["rawMimicInfo"]==CANDIDATE2022,(id,source["rawMimicInfo"])
            assert mimic==CANDIDATE_2021,("Historical source mismatch",id,mimic)
            cls="candidate1000"
        counts[cls]+=1
        matches.append({
          "missionId":id,
          "sourceYear2021":2021,
          "sourceYear2022":2022,
          "crossEraMimicTokenClass":cls,
          "historical2021MimicParsed":old["old2021MimicRaw"],
          "original2022MimicRaw":source["rawMimicInfo"],
          "original2022EncounterRefRaw":source["rawEncounterRef"],
          "original2022EnemyGroupProven":False,
          "original2022MimicSemanticsProven":False,
          "original2022WaveContentsProven":False,
          "nativeEnemyAIProven":False,
          "changesGame":False
        })
    assert dict(counts)=={"empty":21,"candidate1000":13},counts
    return {
      "schema":"bf-global-readonly-mistral-mimic-cross-era-audit-v196",
      "source2021GitBlobSha1":BLOB2021,
      "source2022ArchiveSha256":ZIP2022,
      "source2022MissionMasterSha256":MISSION2022,
      "mistralMissionsCompared":34,
      "literalClassParity":{"empty":21,"candidate1000":13},
      "native2022EnemyGroupsAuthenticated":False,
      "native2022WaveFormationsAuthenticated":False,
      "native2022AIAuthenticated":False,
      "native2022LootAuthenticated":False,
      "readOnly":True,
      "saveChanges":False,
      "gameplayChanges":False,
      "rows":matches
    }

def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,
        help="Optional research report outside project; no APK or user-save writes")
    a=parser.parse_args()
    report=compare()
    if a.output:
        assert not a.output.resolve().is_relative_to(ROOT.resolve()),"Project overwrite blocked"
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2)+"\n","utf8")
    else:
        print("PASS v196: 34 source IDs, 21 zero and 13 candidate mimic-token literal cross-era matches")
        print("Historical 2021 group values are not proof of native 2022 spawn/AI semantics.")
        print("No native enemy groups, wave formations, game or save changes.")
if __name__=="__main__":main()
