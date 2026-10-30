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
 # v210 / Claude N1: guard-negative probes run BEFORE any successful v209
 # initialization; thus the existing DOM/API cannot mask a bad guard.
 page.evaluate("""()=>{window.__v210Guide=BFAmdahlSourceQuestGuideV20600;
                       window.__v210Refs=BFGlobalEncounterReferencesV15100;}""")
 def blocked(label):
  page.add_script_tag(path=str(A/"bf20900_amdahl_original_opaque_mission_fields.js"))
  assert page.locator("#bf20900-raw-mission-fields").count()==0,label
  assert page.evaluate("window.BFAmdahlOriginalOpaqueFieldsV20900===undefined"),label
 for field,bad in (("masterSha256","bad-master"),
                   ("canonicalQuestSha256","bad-quest"),
                   ("playable",True),("missions",35)):
  page.evaluate("""([key,value])=>{
   const g=window.__v210Guide;
   window.BFAmdahlSourceQuestGuideV20600={
     ...g,source:{...g.source,[key]:value}};
  }""",[field,bad])
  blocked("v206-source-"+field)
  page.evaluate("window.BFAmdahlSourceQuestGuideV20600=window.__v210Guide")
 for field,bad in (("sha256","bad-master"),
                   ("meaningDecoded",True),
                   ("amdahlSourceOnlyMissions",35),
                   ("playableMissions",105)):
  page.evaluate("""([key,value])=>{
   const r=window.__v210Refs;
   window.BFGlobalEncounterReferencesV15100={
     ...r,summary:{...r.summary,[key]:value}};
  }""",[field,bad])
  blocked("v151-summary-"+field)
  page.evaluate("window.BFGlobalEncounterReferencesV15100=window.__v210Refs")
 for field,mission,bad in (("raw",404,"0:99999"),
                           ("dungeonId",465,400),
                           ("playable",430,True),
                           ("missing",401,None)):
  page.evaluate("""([field,mid,bad])=>{
   const r=window.__v210Refs;
   window.BFGlobalEncounterReferencesV15100={
    ...r,lookup:id=>id!==mid?r.lookup(id):field==="missing"?
      null:{...r.lookup(id),[field]:bad}};
  }""",[field,mission,bad])
  blocked("v151-row-"+field+"-"+str(mission))
  page.evaluate("window.BFGlobalEncounterReferencesV15100=window.__v210Refs")
 page.evaluate("""()=>{
  const g=window.__v210Guide;
  window.BFAmdahlSourceQuestGuideV20600={
    ...g,lookup:id=>{const x=g.lookup(id);
      return id===441?[x[0],999,...x.slice(2)]:x;}};
 }""")
 blocked("v206-wrong-dungeon-441")
 page.evaluate("window.BFAmdahlSourceQuestGuideV20600=window.__v210Guide")
 page.evaluate("QUESTS.push({missionId:999})")
 blocked("107-playable-quests")
 page.evaluate("QUESTS.pop()")
 page.evaluate("delete window.BFAmdahlSourceQuestGuideV20600")
 blocked("missing-v206-api")
 page.evaluate("window.BFAmdahlSourceQuestGuideV20600=window.__v210Guide")
 page.evaluate("delete window.BFGlobalEncounterReferencesV15100")
 blocked("missing-v151-api")
 page.evaluate("window.BFGlobalEncounterReferencesV15100=window.__v210Refs")
 page.evaluate("""()=>{window.__v210Option=
   document.querySelector("#bf20600-dungeon").lastElementChild;
   window.__v210Option.remove();}""")
 blocked("wrong-dungeon-option-count")
 page.evaluate("""()=>{document.querySelector("#bf20600-dungeon")
   .append(window.__v210Option);delete window.__v210Option;}""")
 for id in ("bf20600-dungeon","bf20600-quest-list","bf20600-amdahl-guide"):
  page.evaluate("""id=>{
   const el=document.getElementById(id);
   window.__v210Removed=el;
   window.__v210Parent=el.parentElement;
   window.__v210Next=el.nextSibling;
   el.remove();
  }""",id)
  blocked("missing-dom-"+id)
  page.evaluate("""()=>{
   window.__v210Parent.insertBefore(window.__v210Removed,window.__v210Next);
   delete window.__v210Removed;
   delete window.__v210Parent;
   delete window.__v210Next;
  }""")
 assert not errors,errors
 page.evaluate("delete window.__v210Guide;delete window.__v210Refs")
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
  page.wait_for_function("count=>document.querySelectorAll('#bf20900-source-fields li').length===count",arg=len(expected))
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
