"""v1.20: read-only 2014 Global historical enemy wave research."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
d=json.loads((R/'source_data/bf_global_historical_encounters_v120.json').read_text('utf8'))
assert d['schema']=='bf-global-historical-encounters-2014-v120'
assert [q['id'] for q in d['missions']]==[1,2,10,20]
assert sum(len(q['waves']) for q in d['missions'])==16
assert sum(len(w['enemies']) for q in d['missions'] for w in q['waves'])==33
assert all(len(q['gitBlobSha'])==40 for q in d['missions'])
js=(A/'bf120_historical_encounters.js').read_text('utf8')
assert js.count('/* BF_HISTORICAL_GLOBAL_ENCOUNTERS_V120 */')==1
assert 'localStorage' not in js and 'saveProgress(' not in js
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf110_quest_journal.js")')<java.index('readPackagedText("bf120_historical_encounters.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
 page.evaluate("""() => {
   const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
     removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
     get length(){return Object.keys(db).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
              'bf110_quest_journal.js','bf120_historical_encounters.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFHistoricalEncountersV120.ids')==[1,2,10,20]
 assert page.evaluate('BFHistoricalEncountersV120.waves')==16
 assert page.evaluate('BFHistoricalEncountersV120.enemySlots')==33
 assert page.evaluate('BFHistoricalEncountersV120.lookup(200)') is None
 assert page.evaluate('BFHistoricalEncountersV120.lookup(1).waves[0].enemies[0].name')=='Mossy'
 assert page.evaluate('BFHistoricalEncountersV120.lookup(2).waves[2].enemies[0].name')=='Skeleton'
 assert page.evaluate('BFHistoricalEncountersV120.lookup(20).waves[4].enemies.length')==2
 old=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
    save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('BFHistoricalEncountersV120.refresh()')
 new=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
    save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert old==new,'read-only inspector mutated saved state'
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf120-historical-battles').is_visible()
 page.locator('#bf120-historical-battles summary').click()
 assert page.locator('#bf120-historical-waves section').count()==3
 assert 'King Mossy' in page.locator('#bf120-historical-waves').text_content()
 assert 'NOT confirmed' in page.locator('#bf120-historical-note').text_content()
 assert not errs,errs
 browser.close()
print('PASS v1.20 four historical missions, 16 groups, 33 enemies, no save edits')
