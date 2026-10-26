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
