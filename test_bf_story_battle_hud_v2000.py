"""v20.00 real playable quest HUD, source stages, post-victory next-mission and save safety."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
src=(A/'bf2000_story_battle_hud.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_STORY_BATTLE_HUD_V2000 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf110_quest_journal.js")')<java.index('readPackagedText("bf2000_story_battle_hud.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
  const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
   removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
              'bf110_quest_journal.js','bf2000_story_battle_hud.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf2000-run').is_visible()
 s=page.evaluate('BFGlobalStoryBattleV2000.snapshot()')
 assert s['missionId']==1 and s['archive'] and s['total']==3,s
 assert s['current']==1 and s['completed']==0 and s['nextId'] is None,s
 assert 'DEMO' in page.locator('#bf2000-foot').inner_text()
 assert page.locator('#bf2000-waves span').count()==3
 assert page.locator('#bf2000-next').is_disabled()
 before=page.evaluate("""()=>({p:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('()=>{S.wave=1;BFGlobalStoryBattleV2000.refresh()}')
 assert page.evaluate('BFGlobalStoryBattleV2000.snapshot().current')==2
 assert page.locator('#bf2000-waves span[data-completed="true"]').count()==1
 page.evaluate('()=>{S.wave=0;BFGlobalStoryBattleV2000.refresh()}')
 after=page.evaluate("""()=>({p:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Passive quest HUD must not touch persisted progress'
 assert page.evaluate('BFGlobalStoryBattleV2000.advance()') is False
 # Actual reward handler is reused. Bypassing combat here is a smoke fixture, not a
 # measured full-play victory; full native demo combat has separate regression gates.
 page.evaluate("""()=>{finish(true);S.over=true;S.phase='Victory';
   BFGlobalStoryBattleV2000.refresh()}""")
 s=page.evaluate('BFGlobalStoryBattleV2000.snapshot()')
 assert s['won'] and s['clears']>=1 and s['nextId']==2,s
 assert page.locator('#bf2000-next').is_enabled()
 assert page.locator('#bf2000-waves span[data-completed="true"]').count()==3
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalStoryBattleV2000.advance()') is False
 page.evaluate('S.busy=false')
 page.locator('#bf2000-next').click()
 assert page.evaluate('QUEST.missionId')==2
 assert page.evaluate('P.questClears[1]')>=1
 assert page.evaluate('P.version')==7
 assert page.evaluate('JSON.parse(localStorage.getItem("bf_global_offline_demo_v7")).version')==7
 assert page.evaluate('BFGlobalStoryBattleV2000.snapshot().total')==page.evaluate('QUEST.battles')
 page.locator('#mode').select_option('training')
 assert page.evaluate('BFGlobalStoryBattleV2000.refresh().archive') is False
 assert 'training mode' in page.locator('#bf2000-details').inner_text()
 assert page.evaluate('BFGlobalStoryBattleV2000.advance()') is False
 assert not errors,errors
 browser.close()
print('PASS v20.00: actual quest battle wave HUD, 2022 archive labels, live state, victory advance, training isolation, save v7')
