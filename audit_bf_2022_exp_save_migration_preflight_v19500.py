"""v195 — READ-ONLY DEMO EXP save-migration risk evaluator.

The authenticated 2022 master establishes unit EXP pattern *IDs* and source
max levels. The external DecompFrontier numbers are unverified 2022 curves.
This tool does not alter saves, unit EXP, game assets, APKs, or upgrade logic.
"""
from pathlib import Path
from argparse import ArgumentParser
from bisect import bisect_right
from collections import Counter
import json, hashlib

ROOT=Path(__file__).resolve().parent
SRC=ROOT/"source_data"
CAT=SRC/"bf_global_2022_playable_lord_stat_endpoints_v116.json"
CAPS=SRC/"bf_global_2022_playable_level_caps_v115.json"
EXT=SRC/"bf_global_external_exp_pattern_candidates_v194.json"
ARCHIVE="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
UPSTREAM="c109ff5059f3fad457d95ad196552d601716d4db"
SAMPLES=(0,5,50,330,24255,1000000000000)
MAX_JS_SAFE=9007199254740991

def demo_threshold(level):
    assert type(level) is int and 1<=level<=99
    # Actual v7 demoLevel: while level < 99 and remaining >= 5*level.
    return 5*level*(level-1)//2

def demo_level(exp):
    assert type(exp) is int and 0<=exp<=MAX_JS_SAFE
    return bisect_right([demo_threshold(level) for level in range(1,100)],exp)

def sources():
    catalog=json.loads(CAT.read_text("utf8"))
    caps=json.loads(CAPS.read_text("utf8"))
    candidates=json.loads(EXT.read_text("utf8"))
    assert catalog["schema"]=="bf-global-2022-playable-lord-stat-endpoints-v116"
    assert catalog["source"]["archiveSha256"]==ARCHIVE
    assert catalog["unitCount"]==len(catalog["rows"])==72
    assert caps["schema"]=="bf-global-2022-playable-max-levels-v115"
    assert caps["provenance"]["archiveSha256"]==ARCHIVE
    assert caps["supportedForms"]==72
    assert candidates["schema"]=="bf-global-external-v194-unit-exp-row-candidates"
    assert candidates["source"]["gitBlobSha1"]==UPSTREAM
    assert candidates["source"]["commit"]=="7cc0ebd3be79ca561874f70224c3ed924224583b"
    assert candidates["source"]["experimentalServerVersion"]=="2.19.6.0"
    assert candidates["source"]["rowCount"]==804
    assert candidates["sourcePatternsAll"]=={"10":201,"15":201,"20":201,"25":201}
    assert candidates["notOriginal2022Authenticated"] is True
    assert candidates["native2022ThresholdsVerified"] is False
    assert candidates["changesGame"] is False and candidates["changesPlayerSave"] is False
    assert candidates["savedRowsPerCandidate"]==100
    assert candidates["matches2022CatalogPatternIds"]==[10,15,20]
    assert Counter(row["expPatternId"] for row in catalog["rows"])=={10:42,15:24,20:6}
    assert len({row["unitId"] for row in catalog["rows"]})==72
    assert Counter(row["maxLevel"] for row in catalog["rows"])[100]==12
    for row in catalog["rows"]:
        assert row["maxLevel"] in (12,30,40,60,80,100)
        assert row["expPatternId"] in (10,15,20)
    lookup={str(pid):vals for pid,vals in candidates["candidateFirst100LevelRowValues"].items()}
    assert set(lookup)=={"10","15","20"}
    threshold={}
    for pid,vals in lookup.items():
        assert len(vals)==100 and vals[0]==0
        assert all(type(v) is int and v>=0 for v in vals)
        cumulative=[]
        total=0
        for value in vals:
            total+=value
            cumulative.append(total)
        assert all(a<b for a,b in zip(cumulative,cumulative[1:]))
        assert cumulative[-1]==candidates["candidateSumOfLevelRowValues1To100"][pid]
        threshold[pid]=cumulative
    assert threshold["10"][:5]==[0,10,58,160,328]
    assert threshold["15"][:5]==[0,15,87,240,492]
    assert threshold["20"][:5]==[0,21,117,321,658]
    assert threshold["10"][-1]==1000000
    assert threshold["15"][-1]==1500000
    assert threshold["20"][-1]==1999997
    assert all(catalog["source"]["archiveSha256"]==caps["provenance"]["archiveSha256"] for _ in [0])
    for row in catalog["rows"]:
        unit=row["unitId"]
        element=unit//10000
        suffix=unit%10000
        if 11<=suffix<=15:
            expected=caps["firstStarterCapByElement"][str(element)][suffix-11]
        elif 21<=suffix<=25:
            expected=caps["secondStarterCap"][suffix-21]
        elif 41<=suffix<=42:
            expected=caps["alternateCap"][suffix-41]
        else:
            raise AssertionError(("Unexpected original unit form",unit))
        assert row["maxLevel"]==expected,(unit,expected)
    return catalog,candidates,threshold

def preflight(unit, exp, thresholds):
    assert type(exp) is int and 0<=exp<=MAX_JS_SAFE
    pattern=int(unit["expPatternId"])
    cap=int(unit["maxLevel"])
    assert pattern in (10,15,20) and cap in (12,30,40,60,80,100)
    demo=demo_level(exp)
    old_archive_level=min(demo,cap)
    candidate=thresholds[str(pattern)]
    # ANALYSIS ONLY: hypothetical external values, not original 2022 levels.
    possible=min(cap,bisect_right(candidate[:cap],exp))
    assert 1<=demo<=99 and 1<=possible<=cap
    has_level_excess=demo>=cap or demo>=99
    demo_start=demo_threshold(demo)
    remaining=exp-demo_start
    rate=5*demo
    assert remaining>=0
    preview=None
    if not has_level_excess:
        assert demo<99 and demo<cap and remaining<rate
        step=candidate[demo]-candidate[demo-1]
        assert step>0
        # Hypothetical fraction-preserving estimate, explicitly NOT a
        # player EXP migration recommendation or a 2022-authentic amount.
        preview=candidate[demo-1]+(remaining*step//rate)
        assert candidate[demo-1]<=preview<candidate[demo]
    return {
      "unitId":unit["unitId"],
      "source2022PatternId":pattern,
      "source2022MaxLevel":cap,
      "savedDemoExpSample":exp,
      "existingDemoLevel":demo,
      "existingArchiveBattleCapLevel":old_archive_level,
      "hypotheticalExternalLevelIfReinterpreted":possible,
      "hypotheticalExternalLevelIfReinterpretedDiffers":possible!=old_archive_level,
      "demoProgressRemainder":remaining if not has_level_excess else None,
      "demoNextLevelCost":rate if not has_level_excess else None,
      "hypotheticalFractionMappedExp":preview,
      "requiresSpecialHandlingAtDemoOrSourceCap":has_level_excess,
      "original2022ThresholdsAuthenticated":False,
      "native2022ExpMigrationAllowed":False,
      "writesUserSave":False,
    }

def report():
    catalog,external,thresholds=sources()
    rows=[]
    for unit in sorted(catalog["rows"],key=lambda x:x["unitId"]):
        for exp in SAMPLES:
            rows.append(preflight(unit,exp,thresholds))
    assert len(rows)==72*len(SAMPLES)
    return {
      "schema":"bf-global-save-safe-EXP-migration-PREFLIGHT-v195",
      "sourceYear":2022,
      "sourceArchiveSha256":ARCHIVE,
      "externalCandidateBlobSha1":UPSTREAM,
      "candidateFromExperimentalServer":True,
      "actual2022ExpCurveVerified":False,
      "liveDemoLevelCap":99,
      "originalSourceMaxLevel100Forms":12,
      "currentSaveSchemaVersion":7,
      "currentSaveKey":"bf_global_offline_demo_v7",
      "existingDemoExpThresholdAtLevel99":demo_threshold(99),
      "hypotheticalExternalThresholdAtLevel100":{
        pid:thresholds[pid][99] for pid in ("10","15","20")},
      "syntheticSamplesOnly":True,
      "syntheticSavedExpValues":list(SAMPLES),
      "noUserSaveLoaded":True,
      "noPlayerSaveChanged":True,
      "noGameMechanicsChanged":True,
      "migrationEnabled":False,
      "unitFormsCompared":72,
      "sampledRows":len(rows),
      "rows":rows,
    }

def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,
        help="Optional synthetic report JSON outside repository; NEVER an input save or an APK.")
    args=parser.parse_args()
    data=report()
    if args.output:
        assert not args.output.resolve().is_relative_to(ROOT.resolve()),"No project file writes"
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(data,indent=2)+"\n","utf8")
    else:
        differs=sum(row["hypotheticalExternalLevelIfReinterpretedDiffers"] for row in data["rows"])
        capped=sum(row["requiresSpecialHandlingAtDemoOrSourceCap"] for row in data["rows"])
        print("PASS v195: 72 original-source forms × 6 synthetic DEMO EXP samples =",
              data["sampledRows"])
        print("Hypothetical external reinterpretation differs at",differs,"samples.")
        print("DEMO/source cap ambiguity flagged at",capped,"samples.")
        print("No original 2022 threshold or player-save migration authorized.")

if __name__=="__main__":main()
