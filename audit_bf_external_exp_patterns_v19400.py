"""v194: independent read-only EXP source crosswalk, NEVER a native 2022 curve.

CI checks the locally pinned numerical excerpt and 2022 pattern distribution.
An optional local --upstream rechecks all 804 exact external JSON rows against
the pinned git-blob SHA-1, without any external network request.
"""
from pathlib import Path
from argparse import ArgumentParser
from collections import Counter
import hashlib
import json

ROOT=Path(__file__).resolve().parent
E=ROOT/"source_data/bf_global_external_exp_pattern_candidates_v194.json"
CAT=ROOT/"source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json"
HIST=ROOT/"source_data/bf_global_2022_cross_era_exp_candidates_v193.json"
UPSTREAM_SHA="c109ff5059f3fad457d95ad196552d601716d4db"
UPSTREAM_COMMIT="7cc0ebd3be79ca561874f70224c3ed924224583b"
ZIP2022="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
def blobsha(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()
def loaded():
    d=json.loads(E.read_text("utf8"))
    cat=json.loads(CAT.read_text("utf8"))
    old=json.loads(HIST.read_text("utf8"))
    assert d["schema"]=="bf-global-external-v194-unit-exp-row-candidates"
    assert d["notOriginal2022Authenticated"] is True
    assert d["native2022ThresholdsVerified"] is False
    assert d["native2022StatGrowthVerified"] is False
    assert d["changesGame"] is False and d["changesPlayerSave"] is False
    assert d["source"]["repository"]=="decompfrontier/server"
    assert d["source"]["commit"]==UPSTREAM_COMMIT
    assert d["source"]["gitBlobSha1"]==UPSTREAM_SHA
    assert d["source"]["path"]=="deploy/system/unit_exp_pattern.json"
    assert d["source"]["experimentalServerVersion"]=="2.19.6.0"
    assert d["source"]["rowCount"]==804
    assert d["sourceFields"]=={
      "collection":"JYFGe9y6","pattern":"5UvTp7q1",
      "level":"D9wXQI2V","value":"grKTq15A"}
    assert d["sourcePatternsAll"]=={"10":201,"15":201,"20":201,"25":201}
    assert cat["source"]["archiveSha256"]==ZIP2022
    assert cat["unitCount"]==len(cat["rows"])==72
    assert Counter(x["expPatternId"] for x in cat["rows"])=={10:42,15:24,20:6}
    assert old["original2022"]["archiveSha256"]==ZIP2022
    assert old["original2022"]["observedPatternIds"]==[10,15,20]
    assert d["matches2022CatalogPatternIds"]==[10,15,20]
    assert d["originalUnitCountReferenced"]==72
    rows=d["candidateFirst100LevelRowValues"]
    assert sorted(rows)==["10","15","20"] and d["savedRowsPerCandidate"]==100
    assert d["candidateLevel2Values"]=={"10":10,"15":15,"20":21}
    assert d["candidateSumOfLevelRowValues1To100"]=={
       "10":1000000,"15":1500000,"20":1999997}
    expectedlv={10:(10,48,102,168,25062),
                15:(15,72,153,252,37592),
                20:(21,96,204,337,50123)}
    for pid,targets in expectedlv.items():
        a=rows[str(pid)]
        assert len(a)==100 and a[0]==0
        assert all(isinstance(n,int) and n>=0 for n in a)
        assert a[1:5]==list(targets[:4])
        assert a[99]==targets[4]
        assert sum(a)==d["candidateSumOfLevelRowValues1To100"][str(pid)]
        assert all(x<y for x,y in zip(a[1:],a[2:])),pid
    # Original public historic first five level CUMULATIVE samples vs this
    # 2.19.6 experimental server's row-values interpreted as increments.
    # This interpretation is a hypothesis, not 2022 proof.
    sample=old["historicalSampleCumulativeExpAtLevels1To5"]
    classes={10:"initial10",15:"initial15",20:"initial21"}
    differences={}
    for pid,name in classes.items():
        observed=[]
        amount=0
        for value in rows[str(pid)][:5]:
            amount+=value
            observed.append(amount)
        historic=sample[name]
        assert len(observed)==len(historic)==5
        differences[str(pid)]=observed[-1]-historic[-1]
        assert differences[str(pid)]==d["discrepancyFromV193HistoricLv5"][str(pid)]
    assert differences=={"10":-1,"15":0,"20":0}
    return d

def scan_upstream(path,d):
    source=path.read_bytes()
    assert blobsha(source)==UPSTREAM_SHA,"External source object hash mismatch"
    parsed=json.loads(source)
    assert list(parsed)==["JYFGe9y6"]
    rows=parsed["JYFGe9y6"]
    assert len(rows)==804
    buckets={str(p):[] for p in (10,15,20,25)}
    for row in rows:
        assert sorted(row)==["5UvTp7q1","D9wXQI2V","grKTq15A"]
        pid=row["5UvTp7q1"]
        assert pid in buckets
        level=int(row["D9wXQI2V"])
        value=int(row["grKTq15A"])
        assert 1<=level<=201 and value>=0
        buckets[pid].append((level,value))
    for pid,bucket in buckets.items():
        assert len(bucket)==201 and [lv for lv,_ in bucket]==list(range(1,202))
        if pid!="25":
            assert [value for _,value in bucket[:100]]==d["candidateFirst100LevelRowValues"][pid]
        else:
            assert all(value==0 for _,value in bucket)
    return buckets

def main():
    ap=ArgumentParser(description=__doc__)
    ap.add_argument("--upstream",type=Path,help="Optional manually fetched pinned external JSON.")
    ap.add_argument("--output",type=Path,help="Optional report path outside repo; no save writes.")
    a=ap.parse_args()
    d=loaded()
    hasUpstream=False
    if a.upstream:
        scan_upstream(a.upstream,d)
        hasUpstream=True
    report={
      "schema":"bf-global-EXP-research-validation-v194",
      "externalSourceCommit":UPSTREAM_COMMIT,
      "externalSourceBlob":UPSTREAM_SHA,
      "externalFull804RowsAuthenticated":hasUpstream,
      "original2022ExpIdsCounted":72,
      "candidateLevel100Sums":d["candidateSumOfLevelRowValues1To100"],
      "candidatePattern20Level2Row":21,
      "historicalPattern10Lv5Mismatch":-1,
      "original2022ExactThresholdsVerified":False,
      "gameplayChanges":False,
      "saveChanges":False}
    if a.output:
        assert not a.output.resolve().is_relative_to(ROOT.resolve()),"No project overwrites"
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2)+"\n","utf8")
    else:
        print("PASS v194: 2022 source IDs 10/15/20 vs external 2.19.6 candidates")
        print("External full 804-row source locally authenticated:",hasUpstream)
        print("Candidate Lv100 cumulative hypotheses:",report["candidateLevel100Sums"])
        print("Pattern20 source row for Lv2=21; original 2022 threshold remains UNVERIFIED")
if __name__=="__main__":
    main()
