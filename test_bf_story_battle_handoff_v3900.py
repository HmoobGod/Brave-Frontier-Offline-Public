"""v39.00 original story intro completion returns to selected demo battle without running it."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf3900_story_battle_handoff.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_STORY_TO_BATTLE_HANDOFF_V3900 */')==1
assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf3800_source_battle_backdrop.js")') < java.index('readPackagedText("bf3900_story_battle_handoff.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
 get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
 'bf100_grand_gaia_campaign.js','bf101_story_continue.js','bf110_quest_journal.js',
 'bf2000_story_battle_hud.js','bf2100_battle_command_tray.js',
 'bf2200_original_event_reader.js','bf2300_morgan_event_dialogue.js',
 'bf2400_st_lamia_event_dialogue.js','bf2500_story_event_prompt.js',
 'bf2600_original_event_portraits.js','bf2700_original_event_stage.js',
 'bf2800_dialogue_speaker_cues.js','bf2900_original_event_expressions.js',
 'bf3000_battle_results.js','bf3100_battle_focus.js',
 'bf3200_combat_journal.js','bf3300_story_playback.js',
 'bf3400_source_scene_placement.js','bf3500_dialogue_timeline.js',
 'bf3600_event_composite.js','bf3700_cinematic_reader.js',
 'bf3800_source_battle_backdrop.js','bf3900_story_battle_handoff.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.evaluate('BFGlobalStoryBattleHandoffV3900.returnToBattle()') is False
 assert page.locator('#bf3900-handoff').is_hidden()
 page.evaluate('()=>{P.questClears[12]=1;renderQuestList()}')
 q=page.evaluate("""()=>{const q=QUESTS.find(q=>q.dungeonId===20&&questUnlocked(q));
   return q&&BFQuestAreas.choose(q)?q.missionId:null}""")
 assert q,q
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 assert page.evaluate('BFGlobalStoryBattleHandoffV3900.refresh().available') is True
 assert page.evaluate('BFGlobalStoryBattleHandoffV3900.snapshot().completed') is False
 assert page.evaluate('BFGlobalStoryBattleHandoffV3900.returnToBattle()') is False
 assert page.evaluate('BFGlobalDialogueTimelineV3500.jump(BFGlobalOriginalEventsV2200.snapshot().lines)') is True
 assert page.evaluate('BFGlobalCinematicReaderV3700.enter()') is True
 assert page.evaluate('BFGlobalStoryBattleHandoffV3900.refresh().completed') is True
 before=page.evaluate("""()=>({save:localStorage.getItem("bf_global_offline_demo_v7"),
    quest:QUEST.missionId,mode:S.mode,round:S.round,wave:S.wave,over:S.over})""")
 assert page.evaluate('BFGlobalStoryBattleHandoffV3900.returnToBattle()') is True
 assert page.evaluate('document.getElementById("bf2200-reader").open') is False
 assert page.evaluate('BFGlobalCinematicReaderV3700.snapshot().focused') is False
 after=page.evaluate("""()=>({save:localStorage.getItem("bf_global_offline_demo_v7"),
    quest:QUEST.missionId,mode:S.mode,round:S.round,wave:S.wave,over:S.over})""")
 assert before==after,(before,after)
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v39.00 original intro end -> active demo battle, no combat execution or save writes')
