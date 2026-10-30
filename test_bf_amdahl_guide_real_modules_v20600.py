"""v206 integration: run real v149 + v151 + v206 scripts together in Chromium.

Validates DOM integration, genuine source rows, and zero save/combat state writes.
A real Android WebView device smoke remains a separate release gate.
"""
from pathlib import Path
import json, shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
Q=json.loads((ROOT/"source_data/bf_global_2022_amdahl_quest_readiness_v147.json").read_text("utf8"))
E=json.loads((ROOT/"source_data/bf_global_original_2022_live_quest_economy_v142.json").read_text("utf8"))
assert len(Q["quests"])==36 and E["total"]==106
assert Q["provenance"]["missionTableSha256"]==E["missionMasterSha256"]
MASTER=E["missionMasterSha256"]
html="""<!doctype html><html><body>
<div id="bf100-campaign"></div>
<details id="bf10800-encounter-ledger"><summary>Sources</summary><p>source</p>
<select id="bf10800-mission"></select><p id="bf10800-raw"></p></details>
</body></html>"""
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which("chromium") or shutil.which("google-chrome") or
   shutil.which("google-chrome-stable"),
  args=["--no-sandbox","--disable-dev-shm-usage"])
 page=browser.new_page(viewport={"width":390,"height":844})
 errors=[]
 page.on("pageerror",lambda error:errors.append(str(error)))
 page.set_content(html,wait_until="load")
 page.evaluate("""data=>{
  const store={'bf_global_offline_demo_v7':'preexisting-data-untouched'};
  let writes=0;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>store[k]??null,
   setItem:(k,v)=>{writes++;store[k]=String(v)},
   removeItem:k=>{writes++;delete store[k]},
   key:i=>Object.keys(store)[i]??null,
   get length(){return Object.keys(store).length;}
  }});
  window.__writes=()=>writes;
  window.P={version:7,roster:[10011],squad:[10011],
   questClears:{365:1},zel:500,karma:10,exp:20,materials:[]};
  window.S={busy:false,party:[{unitId:10011}],enemies:[]};
  window.QUESTS=data.live.map(q=>({missionId:q[0]}));
  window.BFGrandGaiaCampaignV100={summary:{playableMissions:106}};
  const liveMap=new Map(data.live.map(q=>[q[0],{
    missionId:q[0],raw:'3:10100',
    refs:[{opaqueLabel:'3',opaqueRef:'10100'}],
    playable:true
  }]));
  window.BFGlobalEncounterReferencesV10900={
   summary:{archivedMissions:106,sha256:data.master,meaningDecoded:false},
   lookup:id=>liveMap.get(id)||null,
   references:token=>token==='10100'?[1,2]:[]
  };
  const select=document.getElementById('bf10800-mission');
  for(const r of data.live){
   const option=document.createElement('option');
   option.value=String(r[0]);option.textContent=String(r[0]);select.append(option);
  }
 }""",{"live":E["records"],"master":MASTER})
 before=page.evaluate("""()=>({
  p:JSON.stringify(P),s:JSON.stringify(S),quests:JSON.stringify(QUESTS),
  stored:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()
 })""")
 for filename in ("bf14900_original_amdahl_art.js",
                  "bf15100_amdahl_encounter_evidence.js",
                  "bf20600_amdahl_source_quest_guide.js"):
  page.add_script_tag(path=str(ASSETS/filename))
 assert page.evaluate("Boolean(window.BFAmdahlOriginalArtV14900)") is True
 assert page.evaluate("Boolean(window.BFGlobalEncounterReferencesV15100)") is True
 assert page.evaluate("Boolean(window.BFAmdahlSourceQuestGuideV20600)") is True
 assert page.locator("#bf14900-amdahl-art").count()==1
 assert page.locator("#bf20600-amdahl-guide").count()==1
 assert page.locator("#bf10800-mission option").count()==142
 assert page.locator("#bf14900-amdahl-art [data-bf14900-dungeon]").count()==7
 assert page.locator("#bf20600-dungeon option").count()==7
 assert page.locator("#bf20600-quest-list li").count()==5
 assert page.evaluate("QUESTS.length")==106
 assert page.evaluate("BFGlobalEncounterReferencesV15100.summary.saveMutation") is False
 page.locator("#bf14900-amdahl-art > summary").click()
 page.locator("#bf20600-amdahl-guide > summary").click()
 page.locator("#bf14900-amdahl-art [data-bf14900-dungeon='460']").click()
 assert page.locator("#bf20600-dungeon").input_value()=="460"
 assert page.locator("#bf20600-quest-list li").count()==6
 assert page.locator("#bf20600-quest-list li").last.get_attribute("data-mission-id")=="465"
 assert "Malevolent Ceremony" in page.locator("#bf20600-quest-list").inner_text()
 assert "NOT PLAYABLE" in page.locator("#bf20600-quest-list").inner_text()
 page.locator("#bf20600-dungeon").select_option("410")
 assert page.locator("#bf20600-quest-list li").count()==5
 assert "Ghost Ship Legnia" in page.locator("#bf14900-selected").inner_text()
 page.add_script_tag(path=str(ASSETS/"bf20600_amdahl_source_quest_guide.js"))
 assert page.locator("#bf20600-amdahl-guide").count()==1
 after=page.evaluate("""()=>({
  p:JSON.stringify(P),s:JSON.stringify(S),quests:JSON.stringify(QUESTS),
  stored:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()
 })""")
 assert before==after,(before,after)
 assert not errors,errors
 browser.close()
print("PASS v206: real 149→151→206 Amdahl source modules; 142 source, 106 playable, saves untouched")
