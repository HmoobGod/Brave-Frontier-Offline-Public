"""v195: regression and adverse data probes for the read-only EXP preflight.

Synthetic values only, never a user save. Existing DEMO EXP remains untouched.
"""
from pathlib import Path
from collections import Counter
import hashlib,importlib.util,json,subprocess,sys,tempfile

R=Path(__file__).resolve().parent
script=R/"audit_bf_2022_exp_save_migration_preflight_v19500.py"
catalog=R/"source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json"
caps=R/"source_data/bf_global_2022_playable_level_caps_v115.json"
external=R/"source_data/bf_global_external_exp_pattern_candidates_v194.json"
game=R/"app/src/main/assets/index.html"
files=(script,catalog,caps,external,game)
before={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
spec=importlib.util.spec_from_file_location("v195",script)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

assert m.demo_threshold(1)==0
assert m.demo_threshold(2)==5
assert m.demo_threshold(5)==50
assert m.demo_threshold(12)==330
assert m.demo_threshold(30)==2175
assert m.demo_threshold(40)==3900
assert m.demo_threshold(60)==8850
assert m.demo_threshold(80)==15800
assert m.demo_threshold(99)==24255
assert [m.demo_level(x) for x in (0,4,5,49,50,329,330,24254,24255,1000000000000)]==[
    1,1,2,4,5,11,12,98,99,99]

c,ext,curves=m.sources()
assert c["unitCount"]==72
assert Counter(r["expPatternId"] for r in c["rows"])=={10:42,15:24,20:6}
assert Counter(r["maxLevel"] for r in c["rows"])[100]==12
assert curves["10"][:5]==[0,10,58,160,328]
assert curves["15"][:5]==[0,15,87,240,492]
assert curves["20"][:5]==[0,21,117,321,658]
assert [curves[k][99] for k in ("10","15","20")]==[1000000,1500000,1999997]

report=m.report()
assert report["schema"]=="bf-global-save-safe-EXP-migration-PREFLIGHT-v195"
assert report["sampledRows"]==432
assert report["unitFormsCompared"]==72
assert report["syntheticSamplesOnly"] is True
assert report["noUserSaveLoaded"] is True and report["noPlayerSaveChanged"] is True
assert report["noGameMechanicsChanged"] is True and report["migrationEnabled"] is False
assert report["existingDemoExpThresholdAtLevel99"]==24255
assert report["originalSourceMaxLevel100Forms"]==12
assert report["currentSaveSchemaVersion"]==7
assert report["currentSaveKey"]=="bf_global_offline_demo_v7"
assert report["actual2022ExpCurveVerified"] is False

rows=report["rows"]
assert len({(r["unitId"],r["savedDemoExpSample"]) for r in rows})==432
assert not any(r["writesUserSave"] or r["native2022ExpMigrationAllowed"]
   or r["original2022ThresholdsAuthenticated"] for r in rows)
assert all(r["source2022PatternId"] in (10,15,20) for r in rows)
assert all(r["source2022MaxLevel"] in (12,30,40,60,80,100) for r in rows)
assert all(r["existingArchiveBattleCapLevel"]<=r["source2022MaxLevel"] for r in rows)
assert all(r["hypotheticalExternalLevelIfReinterpreted"]<=r["source2022MaxLevel"] for r in rows)
assert all(r["hypotheticalFractionMappedExp"] is None
   if r["requiresSpecialHandlingAtDemoOrSourceCap"] else
   isinstance(r["hypotheticalFractionMappedExp"],int) for r in rows)
unit10011=next(r for r in c["rows"] if r["unitId"]==10011)
unit10025=next(r for r in c["rows"] if r["unitId"]==10025)
assert m.preflight(unit10011,330,curves)["requiresSpecialHandlingAtDemoOrSourceCap"] is True
assert m.preflight(unit10025,24255,curves)["requiresSpecialHandlingAtDemoOrSourceCap"] is True
assert m.preflight(unit10025,50,curves)["hypotheticalFractionMappedExp"]==658
fraction=m.preflight(unit10025,53,curves)
assert fraction["existingDemoLevel"]==5
assert fraction["demoProgressRemainder"]==3
assert fraction["demoNextLevelCost"]==25
assert curves["20"][4]<=fraction["hypotheticalFractionMappedExp"]<curves["20"][5]

with tempfile.TemporaryDirectory() as td:
    temp=Path(td)
    path=temp/"synthetic.json"
    subprocess.run([sys.executable,str(script),"--output",str(path)],cwd=R,check=True)
    data=path.read_bytes()
    assert json.loads(data)==report
    subprocess.run([sys.executable,str(script),"--output",str(path)],cwd=R,check=True)
    assert path.read_bytes()==data
    result=subprocess.run([sys.executable,str(script)],cwd=R,
       capture_output=True,text=True,check=True)
    assert "432" in result.stdout and "No original 2022" in result.stdout
    blocked=R/"source_data"/"DO_NOT_WRITE_V195.json"
    assert not blocked.exists()
    denial=subprocess.run([sys.executable,str(script),"--output",str(blocked)],
       cwd=R,capture_output=True,text=True)
    assert denial.returncode!=0 and not blocked.exists()

    def must_reject(which,mutation):
        src={"cat":catalog,"caps":caps,"ext":external}[which]
        parsed=json.loads(src.read_text("utf8"))
        mutation(parsed)
        altered=temp/(which+".json")
        altered.write_text(json.dumps(parsed),"utf8")
        key={"cat":"CAT","caps":"CAPS","ext":"EXT"}[which]
        original=getattr(m,key)
        setattr(m,key,altered)
        try:
            try:m.sources()
            except (AssertionError,KeyError,ValueError,TypeError):return
            raise AssertionError("Invalid source/EXP candidate passed")
        finally:setattr(m,key,original)
    must_reject("cat",lambda a:a["rows"][0].update(expPatternId=21))
    must_reject("cat",lambda a:a["rows"][0].update(maxLevel=100))
    must_reject("caps",lambda a:a["firstStarterCapByElement"]["1"].__setitem__(0,30))
    must_reject("ext",lambda a:a.update(native2022ThresholdsVerified=True))
    must_reject("ext",lambda a:a.update(changesPlayerSave=True))
    must_reject("ext",lambda a:a["candidateFirst100LevelRowValues"]["20"].__setitem__(1,20))
    must_reject("ext",lambda a:a["candidateFirst100LevelRowValues"]["10"].pop())
    must_reject("ext",lambda a:a["source"].update(gitBlobSha1="0"*40))

after={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
assert before==after,"Research mutated repo source or game"
assert "bf_global_offline_demo_v7" in game.read_text("utf8")
print("PASS v195: 432 synthetic save-risk rows; 72 forms, DEMO and external curves separate; eight corruptions rejected; no user save writes")
