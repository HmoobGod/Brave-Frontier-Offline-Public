"""v30.00 playable demo battle results/redo/continue/source-clear-event actions."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf3000_battle_results.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_DEMO_BATTLE_RESULTS_V3000 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf2900_original_event_expressions.js")') < java.index('readPackagedText("bf3000_battle_results.js")')
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
       'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
       'bf110_quest_journal.js','bf2000_story_battle_hud.js',
       'bf2100_battle_command_tray.js','bf2200_original_event_reader.js',
       'bf2300_morgan_event_dialogue.js','bf2400_st_lamia_event_dialogue.js',
       'bf2500_story_event_prompt.js','bf2600_original_event_portraits.js',
       'bf2700_original_event_stage.js','bf2800_dialogue_speaker_cues.js',
       'bf2900_original_event_expressions.js','bf3000_battle_results.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFGlobalBattleResultsV3000.snapshot().done') is False
 assert page.locator('#bf3000-result').is_hidden()
 assert page.evaluate('BFGlobalBattleResultsV3000.replayBattle()') is False
 assert page.evaluate('BFGlobalBattleResultsV3000.advance()') is False
 assert page.evaluate('BFGlobalBattleResultsV3000.readScene()') is False
 before=page.evaluate("""()=>({p:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('BFGlobalBattleResultsV3000.refresh()')
 after=page.evaluate("""()=>({p:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'read-only result polling must not mutate save'
 page.evaluate('finish(false)')
 assert page.evaluate('BFGlobalBattleResultsV3000.refresh().done') is True
 assert page.evaluate('BFGlobalBattleResultsV3000.snapshot().victory') is False
 assert page.locator('#bf3000-result').is_visible()
 assert 'DEFEAT' in page.locator('#bf3000-reward').inner_text()
 assert page.locator('#bf3000-next').is_disabled()
 assert page.evaluate('BFGlobalBattleResultsV3000.replayBattle()') is True
 assert page.evaluate('S.over') is False
 assert page.evaluate('QUEST.missionId')==1
 page.evaluate('finish(true)')
 s=page.evaluate('BFGlobalBattleResultsV3000.refresh()')
 assert s['victory'] and s['archive'] and s['clears']==1,s
 assert s['exp']==5 and s['nextId']==2,s
 assert 'SIMULATED' in page.locator('#bf3000-reward').inner_text()
 assert not page.locator('#bf3000-next').is_disabled()
 assert page.evaluate('BFGlobalBattleResultsV3000.readScene()') is False
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalBattleResultsV3000.advance()') is False
 assert page.evaluate('BFGlobalBattleResultsV3000.replayBattle()') is False
 page.evaluate('S.busy=false')
 assert page.evaluate('BFGlobalBattleResultsV3000.advance()') is True
 assert page.evaluate('QUEST.missionId')==2
 assert page.evaluate('S.over') is False
 assert page.evaluate('P.questClears[1]')==1
 assert page.evaluate('JSON.parse(localStorage.getItem("bf_global_offline_demo_v7")).version')==7
 # Source-verified mission clear event gated on real archived progression.
 page.evaluate("""()=>{P.questClears[2]=1;renderQuestList();if(!BFQuestAreas.choose(QUESTS.find(q=>q.missionId===10)))throw Error('No mission 10')}""")
 assert page.evaluate('QUEST.missionId')==10
 page.evaluate('finish(true)')
 assert page.evaluate('BFGlobalBattleResultsV3000.refresh().clearScene') is True
 assert page.evaluate('BFGlobalBattleResultsV3000.readScene()') is True
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().chosen')=='clear:10'
 assert 'Farm' in page.locator('#bf2200-text').inner_text()
 assert page.evaluate('BFGlobalBattleResultsV3000.replayBattle()') is True
 page.locator('#mode').select_option('training')
 page.evaluate('finish(true)')
 s=page.evaluate('BFGlobalBattleResultsV3000.refresh()')
 assert s['archive'] is False and s['nextId'] is None and s['exp']==0,s
 assert 'No rewards' in page.locator('#bf3000-reward').inner_text()
 assert page.evaluate('BFGlobalBattleResultsV3000.advance()') is False
 assert page.evaluate('BFGlobalBattleResultsV3000.readScene()') is False
 assert not errors,errors
 browser.close()
print('PASS v30.00: real demo victory/defeat results, retry and next via engine, original source scene, training isolation')
