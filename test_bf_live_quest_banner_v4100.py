"""v41.00 optional read-only mission banner in the existing playable demo battlefield."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf4100_live_quest_banner.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_LIVE_QUEST_BANNER_V4100 */')==1
assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf4000_next_chapter_intro.js")')<java.index('readPackagedText("bf4100_live_quest_banner.js")')
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
 'bf3900_story_battle_handoff.js','bf4000_next_chapter_intro.js',
 'bf4100_live_quest_banner.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.evaluate('P.version')==7
 s=page.evaluate('BFGlobalLiveQuestBannerV4100.snapshot()')
 assert s['available'] and not s['enabled'] and not s['applied'],s
 assert page.evaluate('document.getElementById("bf4100-banner").hidden') is True
 # v409: Home appears only for a live in-memory story battle, never on
 # routine idle Home. Navigating to Quest changes no P/S or canonical save.
 assert page.locator('#bf4100-home-live').count()==1
 assert page.locator('#bf4100-home-live').is_hidden()
 # v409 repair: inspect the REAL initial idle state on visible Home.
 # The engine sets S.round=1 even before an actual player action.
 idle_before=page.evaluate("""()=>({
   round:S.round,wave:S.wave,phase:S.phase,busy:S.busy,
   p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')
 })""")
 assert idle_before['round']==1 and idle_before['wave']==0 and not idle_before['busy'],idle_before
 page.evaluate("BF_homeNav.go('home');BFGlobalLiveQuestBannerV4100.refresh()")
 assert page.evaluate('BF_homeNav.current')=='home'
 assert page.evaluate("document.getElementById('bf4100-home-live').hidden") is True
 assert page.locator('#bf4100-home-return').is_disabled()
 assert page.evaluate("""()=>({
   round:S.round,wave:S.wave,phase:S.phase,busy:S.busy,
   p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')
 })""")==idle_before
 page.evaluate("BF_homeNav.go('quest')")
 saved_round=page.evaluate("""() => ({
   round:S.round,over:S.over,phase:S.phase,auto:S.auto})""")
 page.evaluate("""() => {S.round=2;S.over=false;S.phase='Battle'}""")
 assert page.evaluate('BFGlobalLiveQuestBannerV4100.refresh().available') is True
 page.evaluate("BF_homeNav.go('home')")
 assert page.locator('#bf4100-home-live').is_visible()
 assert 'ACTIVE DEMO STORY' in page.locator('#bf4100-home-message').inner_text()
 page.set_viewport_size({'width':320,'height':844})
 bounds=page.locator('#bf4100-home-return').evaluate("""el => {
   const r=el.getBoundingClientRect(),p=el.parentElement.getBoundingClientRect();
   return {height:r.height,inside:r.left>=p.left-.5&&r.right<=p.right+.5,
     width:document.documentElement.scrollWidth,viewport:innerWidth};
 }""")
 assert bounds['height']>=44 and bounds['inside'] and bounds['width']<=bounds['viewport'],bounds
 on_home=page.evaluate("""() => ({
   player:JSON.stringify(P),round:S.round,over:S.over,phase:S.phase,
   auto:S.auto,wave:S.wave,save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('#bf4100-home-return').click()
 assert page.evaluate('BF_homeNav.current')=='quest'
 assert page.evaluate("""() => ({
   player:JSON.stringify(P),round:S.round,over:S.over,phase:S.phase,
   auto:S.auto,wave:S.wave,save:localStorage.getItem('bf_global_offline_demo_v7')})""")==on_home
 page.evaluate("""s=>{S.round=s.round;S.over=s.over;S.phase=s.phase;S.auto=s.auto;}""",saved_round)
 page.evaluate('BFGlobalLiveQuestBannerV4100.refresh()')
 page.set_viewport_size({'width':390,'height':844})
 before=page.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
    clears:JSON.stringify(P.questClears),round:S.round,wave:S.wave})""")
 assert page.evaluate('BFGlobalLiveQuestBannerV4100.setEnabled(true)') is True
 s=page.evaluate('BFGlobalLiveQuestBannerV4100.refresh()')
 assert s['applied'] and s['missionId']==1 and s['name'],s
 assert page.locator('#bf4100-banner').is_visible()
 assert page.evaluate('document.getElementById("bf4100-banner").parentElement.classList.contains("arena")') is True
 assert page.evaluate('document.getElementById("bf4100-banner").getBoundingClientRect().height>0') is True
 assert s['name'] in page.locator('#bf4100-banner').inner_text()
 assert 'WAVE' in page.locator('#bf4100-banner').inner_text()
 assert page.evaluate('BFGlobalLiveQuestBannerV4100.setEnabled("true")') is False
 page.locator('#mode').select_option('training')
 s=page.evaluate('BFGlobalLiveQuestBannerV4100.refresh()')
 assert s['applied'] is False and s['available'] is False,s
 assert page.evaluate('document.getElementById("bf4100-banner").hidden') is True
 assert page.evaluate('BFGlobalLiveQuestBannerV4100.setEnabled(true)') is False
 page.locator('#mode').select_option('archive')
 assert page.evaluate('BFGlobalLiveQuestBannerV4100.refresh().applied') is True
 assert page.evaluate('BFGlobalLiveQuestBannerV4100.setEnabled(false)') is True
 assert page.evaluate('document.getElementById("bf4100-banner").hidden') is True
 after=page.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
    clears:JSON.stringify(P.questClears),round:S.round,wave:S.wave})""")
 assert before==after,(before,after)
 assert not errors,errors
 browser.close()
print('PASS v41.00 optional archived quest name over live DEMO battlefield without save mutation')
