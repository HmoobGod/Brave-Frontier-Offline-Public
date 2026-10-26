"""v40.00: only after a real demo victory, move to next unlocked original dungeon scene."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf4000_next_chapter_intro.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_NEXT_CHAPTER_INTRO_V4000 */')==1
assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf3900_story_battle_handoff.js")')<java.index('readPackagedText("bf4000_next_chapter_intro.js")')
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
 'bf3000_battle_results.js','bf3100_battle_focus.js','bf3200_combat_journal.js',
 'bf3300_story_playback.js','bf3400_source_scene_placement.js',
 'bf3500_dialogue_timeline.js','bf3600_event_composite.js',
 'bf3700_cinematic_reader.js','bf3800_source_battle_backdrop.js',
 'bf3900_story_battle_handoff.js','bf4000_next_chapter_intro.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.evaluate('BFGlobalNextChapterIntroV4000.continueStory()') is False
 assert page.locator('#bf4000-next-intro').is_hidden()
 page.evaluate('finish(true)')
 assert page.evaluate('BFGlobalBattleResultsV3000.refresh().nextId')==2
 assert page.evaluate('BFGlobalNextChapterIntroV4000.refresh().available') is False
 assert page.evaluate('BFGlobalNextChapterIntroV4000.continueStory()') is False
 assert page.evaluate('QUEST.missionId')==1
 # Find the real dungeon boundary so an original script exists for the upcoming quest.
 srcMission=page.evaluate("""()=>{const idx=QUESTS.findIndex(q=>q.dungeonId===20);
   if(idx<1)throw Error('Cave of Flames not found');
   const prev=QUESTS[idx-1];
   QUESTS.slice(0,idx-1).forEach(q=>P.questClears[q.missionId]=1);
   renderQuestList();
   if(!BFQuestAreas.choose(prev))throw Error('Previous mission unavailable');
   return {prev:prev.missionId,next:QUESTS[idx].missionId}}""")
 page.evaluate('finish(true)')
 state=page.evaluate('BFGlobalNextChapterIntroV4000.refresh()')
 assert state['available'] and state['nextId']==srcMission['next'],state
 assert state['dungeonId']==20 and 'map1-dungeon1.txt' in state['source'],state
 before=page.evaluate("""()=>({clears:JSON.stringify(P.questClears),
   level:P.level,round:S.round,wave:S.wave,quest:QUEST.missionId})""")
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalNextChapterIntroV4000.continueStory()') is False
 assert page.evaluate('()=>{S.busy=false;return !S.busy}') is True
 assert page.evaluate('BFGlobalNextChapterIntroV4000.continueStory()') is True
 after=page.evaluate("""()=>({clears:JSON.stringify(P.questClears),
   level:P.level,round:S.round,wave:S.wave,quest:QUEST.missionId})""")
 assert before['clears']==after['clears']
 assert before['level']==after['level']
 assert after['quest']==srcMission['next']
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().chosen')=='dungeon:20'
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().step')==1
 assert page.evaluate('document.getElementById("bf2200-reader").open') is True
 assert page.evaluate('S.over') is False
 assert page.evaluate('BFGlobalNextChapterIntroV4000.continueStory()') is False
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v40.00 DEMO victory -> source-gated next chapter intro; no free rewards or quest skips')
