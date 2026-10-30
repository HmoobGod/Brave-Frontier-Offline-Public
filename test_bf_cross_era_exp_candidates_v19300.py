"""v193: deterministic research matrix + fail-closed 2022/source-era separation."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile

ROOT=Path(__file__).resolve().parent
script=ROOT/"audit_bf_2022_cross_era_exp_v19300.py"
evidence=ROOT/"source_data/bf_global_2022_cross_era_exp_candidates_v193.json"
original=ROOT/"source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json"
app=ROOT/"app/src/main/assets/index.html"
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (script,evidence,original,app)}
spec=importlib.util.spec_from_file_location("bf193audit",script)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
r=module.generate()
assert r["schema"]=="bf-global-original-2022-historical-exp-RESEARCH-matrix-v193"
assert r["currentPlayableUnitForms"]==len(r["rows"])==72
assert r["originalPatternCounts"]=={"10":42,"15":24,"20":6}
assert r["historicalClasses"]==["initial10","initial15","initial21"]
assert r["allNative2022XpThresholdsVerified"] is False
assert r["changesGame"] is False and r["changesSavedExp"] is False
rows={x["unitId"]:x for x in r["rows"]}
assert len(rows)==72
for uid,p,typ in [(10011,10,"initial10"),(10021,15,"initial15"),
                  (10025,20,"initial21"),(50025,20,"initial21"),
                  (60041,10,"initial10")]:
    x=rows[uid]
    assert x["original2022ExpPatternId"]==p,(uid,x)
    assert x["historicalNot2022Candidate"]==typ,(uid,x)
    assert x["native2022ThresholdsVerified"] is False
    assert x["safeToApplyToPlayerExp"] is False
assert rows[10025]["historicalFirst5CumulativeExp"]==[0,21,117,321,658]
assert rows[10011]["historicalFirst5CumulativeExp"]==[0,10,58,160,329]
assert rows[10021]["historicalFirst5CumulativeExp"]==[0,15,87,240,492]
assert len({x["unitId"] for x in r["rows"] if x["original2022MaxLevel"]==100})==12

with tempfile.TemporaryDirectory() as temp:
    p=Path(temp)/"cross-era.json"
    first=subprocess.run([sys.executable,str(script),"--output",str(p)],
       cwd=str(ROOT),text=True,capture_output=True,check=True)
    assert first.returncode==0 and p.exists()
    data=p.read_bytes()
    assert json.loads(data)==r
    subprocess.run([sys.executable,str(script),"--output",str(p)],
       cwd=str(ROOT),text=True,capture_output=True,check=True)
    assert data==p.read_bytes(),"Report not deterministic"
    out=subprocess.run([sys.executable,str(script)],cwd=str(ROOT),check=True,
       text=True,capture_output=True)
    assert "72 source-exact 2022" in out.stdout
    assert "NOT verified 2022 thresholds" in out.stdout

    # Negative probes operate in temp files only; never change project sources.
    history=json.loads(evidence.read_text("utf8"))
    h=Path(temp)/"h.json"
    def must_fail(changed):
        h.write_text(json.dumps(changed),"utf8")
        saved=module.HIST
        module.HIST=h
        try:
            try:module.generate()
            except (AssertionError,KeyError,ValueError):return
            raise AssertionError("Invalid historical cross-era evidence accepted")
        finally:module.HIST=saved

    bad=json.loads(json.dumps(history))
    bad["native2022CurvesVerified"]=True
    must_fail(bad)
    bad=json.loads(json.dumps(history))
    bad["hypothesesNotEstablished"][2]["historicalClass"]="initial20"
    must_fail(bad)
    bad=json.loads(json.dumps(history))
    bad["historicalSampleCumulativeExpAtLevels1To5"]["initial21"][1]=20
    must_fail(bad)
    bad=json.loads(json.dumps(history))
    bad["original2022"]["unitMaster2Sha256"]="0"*64
    must_fail(bad)
    bad=json.loads(json.dumps(history))
    bad["modifiesPlayerSave"]=True
    must_fail(bad)

    a=json.loads(original.read_text("utf8"))
    a["rows"][0]["expPatternId"]=21
    p2=Path(temp)/"catalog.json"
    p2.write_text(json.dumps(a),"utf8")
    saved=module.CAT
    module.CAT=p2
    try:
        try:module.generate()
        except (AssertionError,KeyError):pass
        else:raise AssertionError("Invalid 2022 source pattern accepted")
    finally:module.CAT=saved

after={str(p):hashlib.sha256(p.read_bytes()).hexdigest()
       for p in (script,evidence,original,app)}
assert before==after,"Research mutated original source or game"
assert "bf_global_offline_demo_v7" in app.read_text("utf8")
print("PASS v193: 72 read-only 2022 EXP IDs; cross-era 10/15/21 NOT native-proven; six negative probes; v7 untouched")
