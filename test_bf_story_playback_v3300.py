"""v33.00 opt-in source dialogue auto-paging, pause/skip, offline read-only safety."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf3300_story_playback.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_ORIGINAL_SCENE_PLAYBACK_V3300 */')==1
assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
assert 'expectedStep' in src and 'identity(s)!==scene' in src and 'blocked()' in src
assert 'min-height:44px;min-width:130px' in src
assert java.index('readPackagedText("bf3200_combat_journal.js")')<java.index('readPackagedText("bf3300_story_playback.js")')
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
 'bf3200_combat_journal.js','bf3300_story_playback.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf3300-player').is_hidden()
 assert page.evaluate('BFGlobalStoryPlaybackV3300.start()') is False
 assert page.evaluate('BFGlobalStoryPlaybackV3300.lastPage()') is False
 page.evaluate('()=>{P.questClears[12]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 assert page.locator('#bf3300-player').is_visible()
 before=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 assert page.evaluate('BFGlobalStoryPlaybackV3300.snapshot().step')==1
 for width in (320,390,540):
  page.set_viewport_size({'width':width,'height':844})
  for control in ('#bf3300-speed','#bf3300-play','#bf3300-pause','#bf3300-end'):
   rect=page.locator(control).bounding_box()
   assert rect and rect['height']>=44,(width,control,rect)
 page.set_viewport_size({'width':390,'height':844})
 page.locator('#bf3300-speed').select_option('1500')
 # v444: player Auto / busy combat cannot trigger archived autoplay or
 # manual jump to last page. No actual DEMO battle action is invoked.
 auto_before=page.evaluate('S.auto')
 busy_before=page.evaluate('S.busy')
 page.evaluate('S.auto=true')
 assert page.evaluate('BFGlobalStoryPlaybackV3300.start()') is False
 assert page.evaluate('BFGlobalStoryPlaybackV3300.lastPage()') is False
 assert 'AUTO / BATTLE BUSY' in page.locator('#bf3300-state').inner_text() or page.evaluate('BFGlobalStoryPlaybackV3300.refresh().blocked') is True
 page.evaluate('S.auto=false;S.busy=true')
 assert page.evaluate('BFGlobalStoryPlaybackV3300.start()') is False
 assert page.evaluate('BFGlobalStoryPlaybackV3300.lastPage()') is False
 page.evaluate('S.busy=false')
 # Even a transient programmatic Auto transition must stop a queued timer.
 assert page.evaluate('BFGlobalStoryPlaybackV3300.start()') is True
 page.evaluate('S.auto=true')
 page.wait_for_function('!BFGlobalStoryPlaybackV3300.snapshot().playing',timeout=5000)
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().step')==1
 page.evaluate('S.auto=false')
 # Restarting same selected source while a later page is pending must not
 # allow the old timer to page the new scene (unchanged source filename).
 assert page.evaluate('BFGlobalStoryPlaybackV3300.start()') is True
 page.wait_for_function('BFGlobalOriginalEventsV2200.snapshot().step >= 2',timeout=4000)
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().step')==1
 page.wait_for_function('!BFGlobalStoryPlaybackV3300.snapshot().playing',timeout=5000)
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().step')==1
 # Existing normal opt-in progression still works.
 assert page.evaluate('BFGlobalStoryPlaybackV3300.start()') is True
 page.wait_for_function('BFGlobalOriginalEventsV2200.snapshot().step >= 2',timeout=4000)
 assert page.evaluate('BFGlobalStoryPlaybackV3300.snapshot().playing') is True
 assert page.evaluate('BFGlobalStoryPlaybackV3300.pause()') is True
 held=page.evaluate('BFGlobalOriginalEventsV2200.snapshot().step')
 page.wait_for_timeout(1650)
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().step')==held
 assert page.evaluate('BFGlobalStoryPlaybackV3300.lastPage()') is True
 s=page.evaluate('BFGlobalOriginalEventsV2200.snapshot()')
 assert s['step']==s['lines'] and s['lines']>30,s
 assert page.evaluate('BFGlobalStoryPlaybackV3300.start()') is False
 assert page.evaluate('BFGlobalStoryPlaybackV3300.snapshot().playing') is False
 assert page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==before
 assert page.evaluate('S.auto')==auto_before and page.evaluate('S.busy')==busy_before
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v33.00 original dialogue source paging, opt-in timer, pause/skip, no save writes')
