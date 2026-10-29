"""v191: prove source-exact 2022 JPG opt-in only for 29 playable quests."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import base64,gzip,hashlib,json,shutil

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
S=R/"source_data"
b64=(S/"bf_global_2022_mission_cross_table_v152.json.gz.b64").read_text("ascii")
raw=base64.b64decode("".join(b64.split()),validate=True)
assert hashlib.sha256(raw).hexdigest()=="cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a"
source=json.loads(gzip.decompress(raw))
assert source["canonicalRowsSha256"]=="2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284"
source_ids={f"dungeon_battle_{i}.jpg" for i in (10200,10300,10400,10500,10600,10700,10800)}
expected={r[0]:r[2] for r in source["rows"] if r[2] in source_ids}
assert len(expected)==29 and len(set(expected.values()))==7
assert set(expected)=={20,21,22,23,30,31,32,33,40,41,42,43,50,51,52,53,
 60,61,62,63,70,71,72,73,81,82,83,84,85}
js=(A/"bf19100_original_2022_dungeon_backdrops.js").read_text("utf8")
v38=(A/"bf3800_source_battle_backdrop.js").read_text("utf8")
java=(R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert "BF_GLOBAL_2022_MISSION_BACKDROP_SOURCE_V19100" in js
assert "BFGlobalOriginalDungeonBackdropsV19100?.lookup?.(q.missionId)" in v38
assert java.index('readPackagedText("bf3800_source_battle_backdrop.js")')<java.index(
 'readPackagedText("bf17400_original_2022_encounter_crossrefs.js")')<java.index(
 'readPackagedText("bf19100_original_2022_dungeon_backdrops.js")')
for name in (js,v38):
 assert "localStorage" not in name and "saveProgress(" not in name
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
  args=["--no-sandbox","--disable-dev-shm-usage"])
 p=b.new_page(viewport={"width":390,"height":844})
 errors=[];p.on("pageerror",lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};window.__v191Writes=[];
  Object.defineProperty(window,"localStorage",{configurable:true,value:{
   getItem:k=>db[k]??null,
   setItem:(k,v)=>{db[k]=String(v);__v191Writes.push(k)},
   removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content((A/"index.html").read_text("utf8"),wait_until="load",timeout=90000)
 p.add_style_tag(path=str(A/"bf_home_nav.css"))
 for name in ("bf_home_nav.js","bf080_morgan_map.js","bf090_st_lamia_map.js",
 "bf100_grand_gaia_campaign.js","bf101_story_continue.js","bf110_quest_journal.js",
 "bf2000_story_battle_hud.js","bf2100_battle_command_tray.js",
 "bf2200_original_event_reader.js","bf2300_morgan_event_dialogue.js",
 "bf2400_st_lamia_event_dialogue.js","bf2500_story_event_prompt.js",
 "bf2600_original_event_portraits.js","bf2700_original_event_stage.js",
 "bf2800_dialogue_speaker_cues.js","bf2900_original_event_expressions.js",
 "bf3000_battle_results.js","bf3100_battle_focus.js",
 "bf3200_combat_journal.js","bf3300_story_playback.js",
 "bf3400_source_scene_placement.js","bf3500_dialogue_timeline.js",
 "bf3600_event_composite.js","bf3700_cinematic_reader.js",
 "bf3800_source_battle_backdrop.js"):
  p.add_script_tag(path=str(A/name))
 # Substitute only the v174 reference object in this fixture; v191's build
 # already verifies and hashes every real original v152 tuple from source.
 # This does not pretend to decode any original 2022 wave or enemy.
 refs={str(mid):{"missionId":mid,"playable":True,"sourceIsOriginal2022":True,
 "originalDungeonBattleBackground":img,"enemyWavesDecoded":False,
 "enemyAIDecoded":False,"enemyIdsDecoded":False} for mid,img in expected.items()}
 p.evaluate("""data=>{
  window.BFGlobalEncounterCrossrefsV17400=Object.freeze({
   source:Object.freeze({year:2022,
    crossTableRowsSha256:'2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284',
    nativeWavesDecoded:false,nativeEnemyIdsDecoded:false}),
   lookup(id){return data[String(id)]||null}
  });
 }""",refs)
 p.add_script_tag(path=str(A/"bf19100_original_2022_dungeon_backdrops.js"))
 assert p.evaluate("BFGlobalOriginalDungeonBackdropsV19100.source.missionCount")==29
 assert p.evaluate("BFGlobalOriginalDungeonBackdropsV19100.source.jpegCount")==7
 assert not p.locator("#bf3800-toggle").is_checked()
 p.evaluate("""()=>{document.getElementById("mode").value="archive";
   window.questUnlocked=()=>true;}""")
 before=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7'),
  writes:JSON.stringify(__v191Writes)})""")
 for mid,filename in expected.items():
  snap=p.evaluate("""id=>{
   QUEST=QUESTS.find(q=>q.missionId===id);
   return BFGlobalBattleBackdropV3800.refresh();
  }""",mid)
  assert snap["available"] is True and snap["background"]==filename,(mid,snap)
  assert not snap["applied"]
  assert p.evaluate("BFGlobalOriginalDungeonBackdropsV19100.lookup("+str(mid)+").image")==filename
 assert p.evaluate("BFGlobalOriginalDungeonBackdropsV19100.lookup(400)") is None
 assert p.evaluate("BFGlobalOriginalDungeonBackdropsV19100.lookup(999999)") is None
 # Source exceptions 70-73 must use the actual mission background, not an
 # imagined suffix inferred from its FIRST opaque reference.
 p.evaluate("QUEST=QUESTS.find(q=>q.missionId===70)")
 assert p.evaluate("BFGlobalBattleBackdropV3800.setEnabled(true)") is True
 state=p.evaluate("BFGlobalBattleBackdropV3800.refresh()")
 assert state["background"]=="dungeon_battle_10700.jpg" and state["applied"]
 assert "dungeon_battle_10700.jpg" in p.locator("#battle").evaluate("(e)=>e.style.backgroundImage")
 assert p.evaluate("BFGlobalBattleBackdropV3800.setEnabled(false)") is True
 p.locator("#mode").select_option("training")
 assert p.evaluate("BFGlobalBattleBackdropV3800.refresh().available") is False
 p.locator("#mode").select_option("archive")
 assert not p.evaluate("BFGlobalBattleBackdropV3800.refresh().applied")
 p.add_script_tag(path=str(A/"bf19100_original_2022_dungeon_backdrops.js"))
 assert p.evaluate("BFGlobalOriginalDungeonBackdropsV19100.source.missionCount")==29
 after=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7'),
  writes:JSON.stringify(__v191Writes)})""")
 assert before==after,(before,after)
 assert not errors,errors
 b.close()
print("PASS v191: original 2022 seven JPG/29 mission mappings, v38 opt-in CSS only, no save/combat writes")
