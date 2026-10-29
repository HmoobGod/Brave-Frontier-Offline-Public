"""v189 compiled APK gate: independently compare all 67 original-byte BF1 battle PNGs.

Inspect the actual APK after assembleDebug, not only the staging directory.
Authentic historic source bytes do NOT certify 2022 opponent assignments.
"""
from pathlib import Path
import base64, hashlib, io, json, re, struct, zipfile

R=Path(__file__).resolve().parent
APK=R/"app/build/outputs/apk/debug/app-debug.apk"
ASSETS=R/"app/src/main/assets"
EXPECTED184="1c450f3487cbb4ec4c6a7103d35ec5b6680d575de4094c6fc39f0ff4084d9914"
EXPECTED185="81136fa4ba29f7d8a58da3d5583ea10536c6d2ba48d383338d94dfa6b9e5dd3a"
EARLY13={10022,10030,10031,10040,10041,10050,10051,10061,10071,
         10081,10082,10102,10103}
def sha(b):return hashlib.sha256(b).hexdigest()
def src(name,expected):
    data=base64.b64decode("".join((R/name).read_text("ascii").split()),validate=True)
    assert sha(data)==expected
    return zipfile.ZipFile(io.BytesIO(data))
art={}
def claim(z,e):
    uid=e["unitId"]
    path=f"content/unit/img/unit_ills_battle_{uid}.png"
    if e["path"]!=path:return
    assert uid not in art
    data=z.read(path)
    assert len(data)==e["bytes"] and sha(data)==e["sha256"]
    assert data[:8]==bytes([137,80,78,71,13,10,26,10])
    assert struct.unpack(">II",data[16:24])==(108,108)
    art[uid]=data
with src("source_assets/bf1/BF1_Global_54_Historical_Battle_Visuals_v184.zip.b64",EXPECTED184) as outer:
    assert outer.testzip() is None
    for n in (1,2,3):
        inner=outer.read(f"BF1_Global_18_Archived_Enemy_Battle_Visuals_Part{n}_v184.zip")
        with zipfile.ZipFile(io.BytesIO(inner)) as z:
            assert z.testzip() is None
            m=json.loads(z.read(f"BF1_Battle_Visuals_Part{n}_Provenance_v184.json"))
            assert m["native2022EnemyFormationVerified"] is False
            assert m["native2022BattleSpriteAssignmentVerified"] is False
            for e in m["entries"]:claim(z,e)
assert len(art)==54 and not set(art)&EARLY13
with src("source_assets/bf1/BF1_Global_13_Historical_Battle_Visuals_v185.zip.b64",EXPECTED185) as z:
    assert z.testzip() is None
    ledger=json.loads(z.read("BF1_13_Enemy_Visuals_Provenance_v185.json"))
    assert ledger["native2022EnemyFormationVerified"] is False
    assert ledger["native2022BattleSpriteAssignmentVerified"] is False
    assert set(ledger["unitIds"])==EARLY13
    for row in ledger["files"]:claim(z,row)
assert len(art)==67 and EARLY13<=set(art)
with zipfile.ZipFile(APK) as apk:
    assert apk.testzip() is None
    names=set(apk.namelist())
    prefix="assets/content/unit_historical_battle_archive/"
    actual={p for p in names if p.startswith(prefix)}
    expected={prefix+f"unit_ills_battle_{uid}.png" for uid in art}
    assert actual==expected,{"missing":sorted(expected-actual),"unexpected":sorted(actual-expected)}
    for uid,raw in art.items():
        packed=apk.read(prefix+f"unit_ills_battle_{uid}.png")
        assert packed==raw,f"Packaged historical art modified for {uid}"
    js=apk.read("assets/bf_global_unit_archive.js").decode("utf8")
    css=apk.read("assets/bf_global_unit_archive.css").decode("utf8")
    assert js==(ASSETS/"bf_global_unit_archive.js").read_text("utf8")
    assert css==(ASSETS/"bf_global_unit_archive.css").read_text("utf8")
    # The runtime allowlists must EXACTLY match the source-provenanced 54+13 IDs.
    # The source image count alone does not reject a wrong or extra JS asset ID.
    original_ids=re.search(r"historicalArtIds\\s*=\\s*new Set\\(\\[([0-9,\\s]+)\\]\\)",js)
    extra_ids=re.search(r"historicalBattleArtIds\\s*=\\s*new Set\\(\\[\\.\\.\\.historicalArtIds,([0-9,\\s]+)\\]\\)",js)
    assert original_ids and extra_ids, "Expected explicit source-bound static allowlists"
    original_list=[int(v.strip()) for v in original_ids.group(1).split(",")]
    extra_list=[int(v.strip()) for v in extra_ids.group(1).split(",")]
    assert len(original_list)==len(set(original_list))==54
    assert len(extra_list)==len(set(extra_list))==13
    assert set(original_list)==set(art)-EARLY13
    assert set(extra_list)==EARLY13
    assert set(original_list).isdisjoint(extra_list)
    assert set(original_list)|set(extra_list)==set(art)
    assert "historicalBattleArtIds=new Set([...historicalArtIds," in js
    assert js.count("bf-v189-historical-battle-art")==2
    assert 'id="bf-v189-historical-battle-art" type="checkbox" />' in js
    assert "exact 2022 Global battlefield assignment unverified" in js
    assert "content/unit_historical_battle_archive/unit_ills_battle_" in js
    assert "localStorage.setItem(" not in js and "saveProgress(" not in js
    assert "bf-v189-battle-preview" in css
    assert "bf_global_offline_demo_v7" in apk.read("assets/index.html").decode("utf8")
    # v188 original 54 archived thumbs and 127 curated remain present.
    assert len([p for p in names if p.startswith("assets/content/unit_historical_archive/")])==54
    assert len([p for p in names if p.startswith("assets/content/unit_archive/unit_ills_thum_")])==127
print("PASS v189 APK: 67 source-byte perfect battle illustrations, independent default-off checkbox, 127+54 portraits retained, v7 unchanged")
