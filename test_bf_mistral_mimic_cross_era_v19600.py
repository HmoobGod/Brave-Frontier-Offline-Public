"""v196 test original 2022 versus historical 2021 source mimic tokens."""
from pathlib import Path
import copy,hashlib,importlib.util,json,subprocess,sys,tempfile

R=Path(__file__).resolve().parent
SCRIPT=R/"audit_bf_mistral_mimic_cross_era_v19600.py"
SRC=R/"source_data/bf_global_mistral_raw_mission_evidence_v056.json"
HISTORY=R/"source_data/bf_global_2021_mistral_mimic_history_v196.json"
APP=R/"app/src/main/assets/index.html"
files=(SCRIPT,SRC,HISTORY,APP)
before={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
spec=importlib.util.spec_from_file_location("v196",SCRIPT)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
d=audit.compare()
assert d["schema"]=="bf-global-readonly-mistral-mimic-cross-era-audit-v196"
assert d["mistralMissionsCompared"]==len(d["rows"])==34
assert d["literalClassParity"]=={"empty":21,"candidate1000":13}
assert d["source2021GitBlobSha1"]=="750871aa060478cc674e7d3e02c739f26364ef8e"
assert d["source2022ArchiveSha256"]=="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
assert d["readOnly"] is True and d["saveChanges"] is False and d["gameplayChanges"] is False
assert all(not d[x] for x in ("native2022EnemyGroupsAuthenticated",
    "native2022WaveFormationsAuthenticated","native2022AIAuthenticated",
    "native2022LootAuthenticated"))
assert len({row["missionId"] for row in d["rows"]})==34
assert len([row for row in d["rows"] if row["crossEraMimicTokenClass"]=="candidate1000"])==13
assert [row["missionId"] for row in d["rows"] if row["crossEraMimicTokenClass"]=="candidate1000"]==[
    60,61,62,63,70,71,72,73,81,82,83,84,85]
assert all(row["original2022EncounterRefRaw"] and
           not row["original2022EnemyGroupProven"] and
           not row["original2022WaveContentsProven"] and
           not row["nativeEnemyAIProven"] and
           not row["changesGame"] for row in d["rows"])
assert d["rows"][0]["missionId"]==1
assert d["rows"][-1]["missionId"]==85
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)
    out=p/"research.json"
    subprocess.run([sys.executable,str(SCRIPT),"--output",str(out)],cwd=R,check=True)
    first=out.read_bytes()
    assert json.loads(first)==d
    subprocess.run([sys.executable,str(SCRIPT),"--output",str(out)],cwd=R,check=True)
    assert out.read_bytes()==first
    summary=subprocess.run([sys.executable,str(SCRIPT)],cwd=R,
        check=True,capture_output=True,text=True)
    assert "34 source IDs, 21 zero and 13 candidate" in summary.stdout
    blocked=R/"source_data"/"DO_NOT_WRITE_v196.json"
    assert not blocked.exists()
    badout=subprocess.run([sys.executable,str(SCRIPT),"--output",str(blocked)],
        cwd=R,capture_output=True,text=True)
    assert badout.returncode!=0 and not blocked.exists()
    def must_reject(which,change):
        path={"hist":HISTORY,"source":SRC}[which]
        original=json.loads(path.read_text("utf8"))
        change(original)
        dest=p/(which+".json")
        dest.write_text(json.dumps(original),"utf8")
        name="HIST" if which=="hist" else "SOURCE"
        old=getattr(audit,name)
        setattr(audit,name,dest)
        try:
            try:audit.compare()
            except (AssertionError,KeyError,TypeError,ValueError):return
            raise AssertionError("Invalid cross-era record accepted")
        finally:setattr(audit,name,old)
    must_reject("hist",lambda v:v["historicalSource"].update(blobGitSha1="0"*40))
    must_reject("hist",lambda v:v["assumptions"].update(native2022AIRecovered=True))
    must_reject("hist",lambda v:v["observations"][0].update(old2021Area="St. Lamia"))
    must_reject("hist",lambda v:v["observations"].pop())
    must_reject("hist",lambda v:next(row for row in v["observations"]
        if row["missionId"]==70)["old2021MimicRaw"].update(group_1_monster_group="9999"))
    must_reject("source",lambda v:v["source"].update(archiveSha256="0"*64))
    must_reject("source",lambda v:next(row for row in v["rows"]
        if row["missionId"]==70).update(rawMimicInfo="1,10,100:9999,0:0"))
    must_reject("source",lambda v:v["rows"].pop())
after={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
assert before==after,"Read-only research modified source or game"
assert "bf_global_offline_demo_v7" in APP.read_text("utf8")
print("PASS v196: 34 2021/2022 Mistral IDs; 21 zero/13 candidate historical mimic matches; eight negative probes; v7 untouched")
