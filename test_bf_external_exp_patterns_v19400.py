"""v194 CI: full 100-level numeric source candidate excerpt, provenance,
2022 non-equivalence, negative probes; no APK or canonical v7 mutations.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,subprocess,sys,tempfile

R=Path(__file__).resolve().parent
script=R/"audit_bf_external_exp_patterns_v19400.py"
candidate=R/"source_data/bf_global_external_exp_pattern_candidates_v194.json"
original=R/"source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json"
history=R/"source_data/bf_global_2022_cross_era_exp_candidates_v193.json"
app=R/"app/src/main/assets/index.html"
files=(script,candidate,original,history,app)
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
spec=importlib.util.spec_from_file_location("v194",script)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
d=audit.loaded()
assert d["source"]["gitBlobSha1"]=="c109ff5059f3fad457d95ad196552d601716d4db"
assert d["source"]["commit"]=="7cc0ebd3be79ca561874f70224c3ed924224583b"
assert d["notOriginal2022Authenticated"] is True
assert d["native2022ThresholdsVerified"] is False
assert d["changesPlayerSave"] is False and d["changesGame"] is False
assert len(d["candidateFirst100LevelRowValues"])==3
assert {k:len(v) for k,v in d["candidateFirst100LevelRowValues"].items()}=={"10":100,"15":100,"20":100}
assert d["candidateLevel2Values"]=={"10":10,"15":15,"20":21}
assert d["candidateSumOfLevelRowValues1To100"]=={"10":1000000,"15":1500000,"20":1999997}
assert d["discrepancyFromV193HistoricLv5"]=={"10":-1,"15":0,"20":0}
with tempfile.TemporaryDirectory() as t:
    folder=Path(t)
    output=folder/"report.json"
    subprocess.run([sys.executable,str(script),"--output",str(output)],cwd=R,check=True)
    first=output.read_bytes()
    report=json.loads(first)
    assert report["original2022ExactThresholdsVerified"] is False
    assert report["externalFull804RowsAuthenticated"] is False
    assert report["gameplayChanges"] is False and report["saveChanges"] is False
    subprocess.run([sys.executable,str(script),"--output",str(output)],cwd=R,check=True)
    assert first==output.read_bytes()
    no=args=None
    blocked=R/"source_data"/"V194_SHOULD_NOT_WRITE.json"
    assert not blocked.exists()
    p=subprocess.run([sys.executable,str(script),"--output",str(blocked)],
       cwd=R,capture_output=True,text=True)
    assert p.returncode!=0 and not blocked.exists()
    fake=folder/"fake-upstream.json"
    fake.write_text(json.dumps({"JYFGe9y6":[]}),"utf8")
    p=subprocess.run([sys.executable,str(script),"--upstream",str(fake)],
       cwd=R,capture_output=True,text=True)
    assert p.returncode!=0,"Fake external source must fail SHA gate"
    # Mutation tests affect only temporary file, never the user's source.
    edited=folder/"candidate.json"
    def must_reject(change):
        edited.write_text(json.dumps(change),"utf8")
        old=audit.E
        audit.E=edited
        try:
            try:audit.loaded()
            except (AssertionError,ValueError,KeyError,TypeError):return
            raise AssertionError("Corrupt/non-original 2022 source candidate accepted")
        finally:audit.E=old
    mutated=copy.deepcopy(d)
    mutated["native2022ThresholdsVerified"]=True
    must_reject(mutated)
    mutated=copy.deepcopy(d)
    mutated["source"]["gitBlobSha1"]="0"*40
    must_reject(mutated)
    mutated=copy.deepcopy(d)
    mutated["candidateFirst100LevelRowValues"]["20"][1]=20
    must_reject(mutated)
    mutated=copy.deepcopy(d)
    mutated["candidateFirst100LevelRowValues"]["10"][4]=169
    must_reject(mutated)
    mutated=copy.deepcopy(d)
    mutated["changesPlayerSave"]=True
    must_reject(mutated)
    mutated=copy.deepcopy(d)
    mutated["candidateFirst100LevelRowValues"]["15"]=mutated["candidateFirst100LevelRowValues"]["15"][:-1]
    must_reject(mutated)
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
assert before==after
assert "bf_global_offline_demo_v7" in app.read_text("utf8")
print("PASS v194: source ID parity, external numeric 100-level candidate tables, 7 negative gates, no EXP/save/game change")
