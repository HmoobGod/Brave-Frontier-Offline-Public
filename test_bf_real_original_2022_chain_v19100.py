"""v191 C2: actual prepared HTML -> real v108/109/151/174/191 source chain.

No stand-in reference APIs. Tests the browser chain, independently from the
synthetic fixture in test_bf_2022_dungeon_backdrops_v19100.py.
"""
from pathlib import Path
import base64,gzip,hashlib,json,re,shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
S=R/"source_data"
html=(A/"index.html").read_text("utf8")
master="d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
original_archive="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
for var,keys in (
 ("BF_MORGAN_QUEST_DATA_V080",{"mastersZipSha256":original_archive,"missionMasterSha256":master}),
 ("BF_STLAMIA_QUEST_DATA_V090",{"missionMasterSha256":master}),
):
 m=re.search(r"window\."+var+r"=Object\.freeze\((\{.*?\})\);",html,re.S)
 assert m,var
 data=json.loads(m.group(1))
 assert data["provenance"]==keys,(var,data.get("provenance"))
 assert data["schema"].startswith("bf-global-")
 assert len(data["quests"])==36

raw=base64.b64decode("".join((S/"bf_global_2022_mission_cross_table_v152.json.gz.b64").read_text("ascii").split()),validate=True)
assert hashlib.sha256(raw).hexdigest()=="cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a"
data=json.loads(gzip.decompress(raw))
assert data["canonicalRowsSha256"]=="2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284"
images={f"dungeon_battle_{num}.jpg" for num in (10200,10300,10400,10500,10600,10700,10800)}
expected={r[0]:r[2] for r in data["rows"] if r[2] in images}
assert len(expected)==29

java=(R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
ordered=["bf14900_original_amdahl_art.js","bf10800_2022_encounter_reference_ledger.js",
 "bf10900_stlamia_encounter_refs.js","bf15100_amdahl_encounter_evidence.js",
 "bf17400_original_2022_encounter_crossrefs.js","bf19100_original_2022_dungeon_backdrops.js"]
assert all(java.index('readPackagedText("'+a+'")')<java.index('readPackagedText("'+b+'")')
 for a,b in zip(ordered,ordered[1:]))

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
  args=["--no-sandbox","--disable-dev-shm-usage"])
 p=browser.new_page(viewport={"width":390,"height":844})
 errors=[];p.on("pageerror",lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
   const db={},writes=[];
   window.__v191RealWrites=writes;
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>db[k]??null,
     setItem:(k,v)=>{db[k]=String(v);writes.push(k)},
     removeItem:k=>delete db[k],
     key:i=>Object.keys(db)[i]??null,
     get length(){return Object.keys(db).length}
   }});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content(html,wait_until="domcontentloaded",timeout=90000)
 assert p.evaluate("P.version")==7
 assert p.evaluate("QUESTS.length")==106
 assert p.evaluate("BFOriginalMissionEvidence.count")==34
 assert p.evaluate("BF_MORGAN_QUEST_DATA_V080.provenance.mastersZipSha256")==original_archive
 assert p.evaluate("BF_STLAMIA_QUEST_DATA_V090.provenance.missionMasterSha256")==master
 for name in ("bf_home_nav.js","bf080_morgan_map.js","bf090_st_lamia_map.js",
   "bf100_grand_gaia_campaign.js","bf14900_original_amdahl_art.js"):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate("Boolean(window.BFAmdahlOriginalArtV14900)")
 before=p.evaluate("""()=>({
   p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7'),
   writes:[...__v191RealWrites]
 })""")
 for file,global_name,count in (
  ("bf10800_2022_encounter_reference_ledger.js","BFGlobalEncounterReferencesV10800",70),
  ("bf10900_stlamia_encounter_refs.js","BFGlobalEncounterReferencesV10900",106),
  ("bf15100_amdahl_encounter_evidence.js","BFGlobalEncounterReferencesV15100",142),
  ("bf17400_original_2022_encounter_crossrefs.js","BFGlobalEncounterCrossrefsV17400",142),
  ("bf19100_original_2022_dungeon_backdrops.js","BFGlobalOriginalDungeonBackdropsV19100",29)):
  p.add_script_tag(path=str(A/file))
  summary=p.evaluate("""name=>{
    const v=window[name];
    if(!v)return null;
    return v.summary?.archivedMissions??v.source?.total??v.source?.missionCount??null;
  }""",global_name)
  assert summary==count,(global_name,summary,count)
 assert p.locator("#bf10800-mission option").count()==142
 assert p.evaluate("BFGlobalEncounterCrossrefsV17400.source.nativeEnemyIdsDecoded") is False
 assert p.evaluate("BFGlobalOriginalDungeonBackdropsV19100.source.nativeEnemyWavesDecoded") is False
 for id,image in expected.items():
  result=p.evaluate("id=>BFGlobalOriginalDungeonBackdropsV19100.lookup(id)",id)
  assert result and result["missionId"]==id and result["image"]==image,(id,result)
  source=p.evaluate("id=>BFGlobalEncounterCrossrefsV17400.lookup(id)",id)
  assert source and source["originalDungeonBattleBackground"]==image,(id,source)
 for id in (400,465,999999):
  assert p.evaluate("id=>BFGlobalOriginalDungeonBackdropsV19100.lookup(id)",id) is None
 # The old original 2022 source lookup remains read-only on second injection.
 for file in ("bf10800_2022_encounter_reference_ledger.js",
              "bf10900_stlamia_encounter_refs.js",
              "bf15100_amdahl_encounter_evidence.js",
              "bf17400_original_2022_encounter_crossrefs.js",
              "bf19100_original_2022_dungeon_backdrops.js"):
  p.add_script_tag(path=str(A/file))
 assert p.locator("#bf10800-mission option").count()==142
 after=p.evaluate("""()=>({
   p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7'),
   writes:[...__v191RealWrites]
 })""")
 assert before==after,(before,after)
 assert not errors,errors
 browser.close()
print("PASS v191 real browser chain: 2022 source v108=70 -> v109=106 -> v151=142 -> v174=142 -> v191=29, no mocks or save writes")
