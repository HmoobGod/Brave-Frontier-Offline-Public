"""v193 read-only: compare authenticated original-2022 unit EXP pattern IDs
with historically documented *candidate* threshold classes (not 2022 proof).
Never mutate the actual game, 72-form source catalog, or canonical v7 saves.
"""
from __future__ import annotations
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parent
SRC=ROOT/"source_data"
CAT=SRC/"bf_global_2022_playable_lord_stat_endpoints_v116.json"
HIST=SRC/"bf_global_2022_cross_era_exp_candidates_v193.json"
SOURCE_HASH="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
M1="1146f09489a07b9187cd3f04bf7dc3ef3bb74e35385869534671af95bf8ea645"
M2="0696ccda59fccf48598c5267eaeb8a306e994618384151cead38cec6a9195b2b"
PREFIX="bf-global-2022-vs-historical-exp-candidates-v193"
def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf8")

def generate():
    a=json.loads(CAT.read_text("utf8"))
    h=json.loads(HIST.read_text("utf8"))
    assert a["schema"]=="bf-global-2022-playable-lord-stat-endpoints-v116"
    assert a["unitCount"]==len(a["rows"])==72
    assert a["source"]["archiveSha256"]==SOURCE_HASH
    assert [x["sha256"] for x in a["source"]["units"]]==[M1,M2]
    assert h["schema"]==PREFIX and h["original2022"]["archiveSha256"]==SOURCE_HASH
    assert [h["original2022"][k] for k in ("unitMaster1Sha256","unitMaster2Sha256")]==[M1,M2]
    assert h["original2022"]["observedPatternIds"]==[10,15,20]
    assert h["original2022"]["patternCounts"]=={"10":42,"15":24,"20":6}
    assert h["native2022CurvesVerified"] is False and h["modifiesPlayerSave"] is False
    assert h["modifiesGame"] is False and h["authorizesXpMigration"] is False
    assert h["original2022"]["xpThresholdsRecovered"] is False
    mapping=h["hypothesesNotEstablished"]
    assert [(x["original2022PatternId"],x["historicalClass"],x["status"]) for x in mapping]==[
       (10,"initial10","unverified-cross-era-candidate"),
       (15,"initial15","unverified-cross-era-candidate"),
       (20,"initial21","unverified-cross-era-candidate-despite-different-number")
    ]
    samples=h["historicalSampleCumulativeExpAtLevels1To5"]
    assert samples=={"initial10":[0,10,58,160,329],
                     "initial15":[0,15,87,240,492],
                     "initial21":[0,21,117,321,658]}
    assert all(all(isinstance(n,int) and n>=0 for n in series) and
               len(series)==5 and all(a<b for a,b in zip(series,series[1:]))
               for series in samples.values())
    assert len(h["historicalNot2022"])==3
    assert all(t["source"].startswith("https://") and
               "2022" in t["description"] for t in h["historicalNot2022"])
    rows=a["rows"];ids=set();out=[]
    for row in rows:
        uid=row["unitId"];p=row["expPatternId"];cap=row["maxLevel"]
        assert isinstance(uid,int) and uid not in ids and 1<=uid<=999999
        ids.add(uid)
        assert p in (10,15,20) and cap in (12,30,40,60,80,100)
        assert row["base"] and row["lordAtMax"]
        candidate=next(v for v in mapping if v["original2022PatternId"]==p)
        out.append({
          "unitId":uid,
          "original2022ExpPatternId":p,
          "original2022MaxLevel":cap,
          "historicalNot2022Candidate":candidate["historicalClass"],
          "historicalFirst5CumulativeExp":samples[candidate["historicalClass"]],
          "native2022ThresholdsVerified":False,
          "safeToApplyToPlayerExp":False
        })
    expected={}
    for element in range(1,7):
        root=element*10000
        expected.update({root+x:10 for x in (11,12,13,14,15,41,42)})
        expected.update({root+x:15 for x in (21,22,23,24)})
        expected[root+25]=20
    assert {x["unitId"]:x["original2022ExpPatternId"] for x in out}==expected
    assert dict(Counter(x["original2022ExpPatternId"] for x in out))=={10:42,15:24,20:6}
    assert len({x["unitId"] for x in out})==72
    assert len({x["unitId"] for x in out if x["original2022MaxLevel"]==100})==12
    return {
       "schema":"bf-global-original-2022-historical-exp-RESEARCH-matrix-v193",
       "original2022ArchiveSha256":SOURCE_HASH,
       "sourceRowsSha256":hashlib.sha256(canonical(a["rows"])).hexdigest(),
       "historicalCandidateManifestSha256":hashlib.sha256(canonical(h)).hexdigest(),
       "currentPlayableUnitForms":72,
       "originalPatternCounts":{"10":42,"15":24,"20":6},
       "historicalClasses":["initial10","initial15","initial21"],
       "allNative2022XpThresholdsVerified":False,
       "changesGame":False,
       "changesSavedExp":False,
       "rows":sorted(out,key=lambda x:x["unitId"])
    }

def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,
        help="Optional local output file; omit to print concise summary (no APK writes).")
    args=parser.parse_args()
    report=generate()
    if args.output:
        assert args.output.resolve() not in (CAT.resolve(),HIST.resolve())
        assert not str(args.output.resolve()).startswith(str((ROOT/"app").resolve())+"/")
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2)+"\n","utf8")
    else:
        print("PASS v193: 72 source-exact 2022 pattern IDs (10:42, 15:24, 20:6).")
        print("Cross-era historical candidates 10/15/21 are NOT verified 2022 thresholds.")
        print("No live EXP, stat, unit, save, Android or summon changes.")

if __name__=="__main__":
    main()
