"""v209: source-exact Amdahl opaque encounter/music/reward hints, read-only.

Runs a real prepared Grand Gaia HTML and the original v149/v151/v206/v209
source modules. It does not infer real 2022 enemies, loot, AI or audio playback.
"""
from pathlib import Path
import json
import re
import shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
JAVA=(R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
HTML=(A/"index.html").read_text("utf8")
Q=json.loads((R/"source_data/bf_global_2022_amdahl_quest_readiness_v147.json").read_text("utf8"))
E=json.loads((R/"source_data/bf_global_original_2022_live_quest_economy_v142.json").read_text("utf8"))
JS=(A/"bf20900_amdahl_original_opaque_mission_fields.js").read_text("utf8")
MASTER="d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
CANON="f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3"
assert len(Q["quests"])==36 and Q["provenance"]["missionTableSha256"]==MASTER
assert Q["provenance"]["questCanonSha256"]==CANON
assert E["total"]==106 and E["missionMasterSha256"]==MASTER
assert JS.count("BF_AMDAHL_ORIGINAL_OPAQUE_MISSION_FIELDS_V20900")==1
assert JS.count(MASTER)==1 and JS.count(CANON)==1
assert len(JS.encode("utf8"))<65536
assert all(x not in JS for x in ["localStorage.","saveProgress(","QUESTS.push(",
                              "P.questClears=","P.roster=","fetch(","XMLHttpRequest(",
                              "new Audio(","audio.play(","BFAndroid","startQuest("])
assert not re.search(r"\b(?:window\.)?setTimeout\s*\(", JS)
m=re.search(r"const rows=(\[.*?\]);\n const seen=",JS,re.S)
assert m,"Missing exact original mission source rows"
source_rows=[[q[k] for k in ("id","rawEncounterRef","battleMusic","bossMusic",
                            "rawRewards","npcId")] for q in Q["quests"]]
assert json.loads(m.group(1))==source_rows
loadorder=("bf14900_original_amdahl_art.js",
           "bf15100_amdahl_encounter_evidence.js",
           "bf20600_amdahl_source_quest_guide.js",
           "bf20900_amdahl_original_opaque_mission_fields.js",
           "bf17400_original_2022_encounter_crossrefs.js")
assert all(JAVA.count('readPackagedText("'+n+'")')==1 for n in loadorder)
assert [JAVA.index('readPackagedText("'+n+'")') for n in loadorder]==sorted(
    JAVA.index('readPackagedText("'+n+'")') for n in loadorder)

with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which("chromium") or
                      shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
                      args=["--no-sandbox","--disable-dev-shm-usage"])
 page=b.new_page(viewport={"width":390,"height":844})
 errors=[]
 page.on("pageerror",lambda e:errors.append(str(e)))
 page.evaluate("""()=>{
  const m=new Map();let writes=0;
  Object.defineProperty(window,"localStorage",{configurable:true,value:{
   getItem:k=>m.has(k)?m.get(k):null,
   setItem:(k,v)=>{writes++;m.set(k,String(v));},
   removeItem:k=>{writes++;m.delete(k);},
   clear:()=>{writes++;m.clear();},
   key:i=>Array.from(m.keys())[i]??null,
   get length(){return m.size;}
  }});
  window.__writes=()=>writes;
 }""")
 page.set_content(HTML,wait_until="domcontentloaded",timeout=60000)
 assert page.evaluate("P.version")==7
 assert page.evaluate("QUESTS.length")==106
 before=page.evaluate("""()=>({
   player:JSON.stringify(P),quests:JSON.stringify(QUESTS),
   stored:localStorage.getItem("bf_global_offline_demo_v7"),writes:__writes()
 })""")
 chain=("bf_home_nav.js","bf080_morgan_map.js","bf090_st_lamia_map.js",
        "bf100_grand_gaia_campaign.js","bf14900_original_amdahl_art.js",
        "bf10800_2022_encounter_reference_ledger.js","bf10900_stlamia_encounter_refs.js",
        "bf15100_amdahl_encounter_evidence.js","bf20600_amdahl_source_quest_guide.js")
 for filename in chain:page.add_script_tag(path=str(A/filename))
 assert page.evaluate("Boolean(window.BFAmdahlSourceQuestGuideV20600)")
 # Fail closed against malformed source or incompatible v7 state.
 page.evaluate("P.version=8")
 page.add_script_tag(path=str(A/"bf20900_amdahl_original_opaque_mission_fields.js"))
 assert page.locator("#bf20900-raw-mission-fields").count()==0
 page.evaluate("P.version=7")
 page.evaluate("""()=>{window.__priorGuide=BFAmdahlSourceQuestGuideV20600;
   window.BFAmdahlSourceQuestGuideV20600={
    ...window.__priorGuide,source:{...window.__priorGuide.source,saveMutation:true}}}""")
 page.add_script_tag(path=str(A/"bf20900_amdahl_original_opaque_mission_fields.js"))
 assert page.locator("#bf20900-raw-mission-fields").count()==0
 page.evaluate("window.BFAmdahlSourceQuestGuideV20600=window.__priorGuide;delete window.__priorGuide")
 page.add_script_tag(path=str(A/"bf20900_amdahl_original_opaque_mission_fields.js"))
 page.add_script_tag(path=str(A/"bf17400_original_2022_encounter_crossrefs.js"))
 assert not errors,errors
 assert page.evaluate("Boolean(window.BFAmdahlOriginalOpaqueFieldsV20900)")
 assert page.evaluate("Boolean(window.BFGlobalEncounterCrossrefsV17400)")
 assert page.evaluate("BFAmdahlOriginalOpaqueFieldsV20900.source.rewardMeaningDecoded") is False
 assert page.evaluate("BFAmdahlOriginalOpaqueFieldsV20900.source.saveMutation") is False
 assert page.locator("#bf20900-raw-mission-fields").count()==1
 assert page.locator("#bf20900-source-fields li").count()==5
 seen=[]
 for dungeon in Q["dungeons"]:
  did=dungeon["id"]
  page.evaluate("id=>BFAmdahlSourceQuestGuideV20600.preview(id)",did)
  expected=[q for q in Q["quests"] if q["dungeonId"]==did]
  page.wait_for_function("count=>document.querySelectorAll('#bf20900-source-fields li').length===count",len(expected))
  texts=page.locator("#bf20900-source-fields li").all_text_contents()
  assert len(texts)==len(expected)
  for q,t in zip(expected,texts):
   id=q["id"]
   assert "Mission "+str(id) in t
   for value in (q["rawEncounterRef"],q["battleMusic"],q["bossMusic"],
                 q["rawRewards"] or "(empty)","SOURCE ONLY"):
    assert value in t,(id,value)
   assert page.evaluate("id=>BFAmdahlOriginalOpaqueFieldsV20900.lookup(id)",id)==[
    q[k] for k in ("id","rawEncounterRef","battleMusic","bossMusic","rawRewards","npcId")]
   seen.append(id)
 assert seen==[q["id"] for q in Q["quests"]]
 assert sum(bool(q["rawRewards"]) for q in Q["quests"])==7
 # Real map pin uses v206.preview (not only select change); the observer syncs.
 page.locator("#bf14900-amdahl-art > summary").click()
 page.locator("#bf20600-amdahl-guide > summary").click()
 page.locator("#bf14900-amdahl-art [data-bf14900-dungeon='460']").click()
 assert page.locator("#bf20600-dungeon").input_value()=="460"
 page.wait_for_function("()=>document.querySelectorAll('#bf20900-source-fields li').length===6")
 page.add_script_tag(path=str(A/"bf20900_amdahl_original_opaque_mission_fields.js"))
 assert page.locator("#bf20900-raw-mission-fields").count()==1
 after=page.evaluate("""()=>({
   player:JSON.stringify(P),quests:JSON.stringify(QUESTS),
   stored:localStorage.getItem("bf_global_offline_demo_v7"),writes:__writes()
 })""")
 assert before==after,(before,after)
 assert not errors,errors
 b.close()
print("PASS v209: all 36 exact source-only encounter/music/reward rows and all seven areas; no v7 gameplay/save mutation")
