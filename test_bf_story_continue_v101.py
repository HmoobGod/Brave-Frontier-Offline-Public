"""v1.01 regression: 106 archived quests, unlock-respecting Continue Story."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
js=(A/'bf101_story_continue.js').read_text('utf-8')
assert js.count('/* BF_GRAND_GAIA_CONTINUE_V101 */')==1
assert 'localStorage' not in js and 'saveProgress(' not in js
assert 'questUnlocked(q)' in js and 'BFQuestAreas.choose(q)' in js
java=(ROOT/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
assert java.index('readPackagedText("bf100_grand_gaia_campaign.js")') < java.index('readPackagedText("bf101_story_continue.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
   const db={};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
      getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
      removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
      get length(){return Object.keys(db).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf-8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7
 assert page.evaluate('QUESTS.length')==106
 assert page.evaluate('BFGrandGaiaContinueV101.snapshot()')=={
    'total':106,'done':0,'mistral':0,'morgan':0,'stlamia':0,'nextMission':1}
 assert page.locator('#bf101-continue').count()==1
 before=page.evaluate("""()=>({p:JSON.stringify(P),
     save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('BFGrandGaiaContinueV101.refresh()')
 after=page.evaluate("""()=>({p:JSON.stringify(P),
     save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'passive refresh must not change save'
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf101-continue').click()
 assert page.evaluate('QUEST.missionId')==1
 assert page.locator('.bf-mistral-map').is_visible()
 page.evaluate('()=>{P.questClears[85]=1;renderQuestList()}')
 assert page.evaluate('BFGrandGaiaContinueV101.nextMission')==1
 page.evaluate('()=>{for(const q of QUESTS.slice(0,34))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGrandGaiaContinueV101.nextMission')==200
 page.locator('#bf101-continue').click()
 assert page.evaluate('QUEST.missionId')==200
 assert page.locator('#bf080-morgan-map').is_visible()
 page.evaluate('()=>{for(const q of QUESTS.slice(0,70))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGrandGaiaContinueV101.nextMission')==300
 page.locator('#bf101-continue').click()
 assert page.evaluate('QUEST.missionId')==300
 assert page.locator('#bf090-stlamia-map').is_visible()
 page.locator('.bf080-region-tabs button').nth(1).click()
 assert page.locator('#bf080-morgan-map').is_visible()
 assert not page.locator('#bf090-stlamia-map').is_visible()
 page.evaluate('()=>{for(const q of QUESTS)P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGrandGaiaContinueV101.snapshot().done')==106
 assert page.evaluate('BFGrandGaiaContinueV101.nextMission') is None
 assert page.locator('#bf101-continue').is_disabled()
 assert '106 archived story missions cleared' in page.locator('#bf101-next').text_content()
 assert page.locator('#bf101-story-continue [aria-valuenow]').get_attribute('aria-valuenow')=='106'
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v1.01 Continue Story across 106 missions, 3 regions, save v7')
