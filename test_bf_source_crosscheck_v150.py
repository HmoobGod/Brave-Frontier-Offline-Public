"""v1.50 integration: read-only 2014/2022 ID joins, optional art, offline diagnostics."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
js=(A/'bf150_source_crosscheck.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert js.count('/* BF_GLOBAL_SOURCE_CROSSCHECK_V150 */')==1
assert 'saveProgress(' not in js and 'localStorage' not in js
assert java.index('readPackagedText("bf120_historical_encounters.js")')<java.index('readPackagedText("bf150_source_crosscheck.js")')
assert java.index('evaluateJavascript(catalogScript, null)')<java.index('readPackagedText("bf150_source_crosscheck.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
   const store={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>store[k]??null,setItem:(k,v)=>store[k]=String(v),
     removeItem:k=>{delete store[k]},key:i=>Object.keys(store)[i]??null,
     get length(){return Object.keys(store).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for n in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
           'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
           'bf110_quest_journal.js','bf120_historical_encounters.js',
           'bf_global_unit_archive.js','bf150_source_crosscheck.js'):
  page.add_script_tag(path=str(A/n))
 assert page.evaluate('BFGlobalUnitArchive.count')==2291
 assert page.evaluate('P.version')==7
 s=page.evaluate('BFGlobalSourceCrosscheckV150.snapshot()')
 assert s['pass'],s
 assert s['regions']==[34,36,36]
 assert s['originalQuestCount']==106 and s['originalDungeonCount']==23
 assert s['historicalMissions']==4 and s['historicalWaves']==16
 assert s['historicalEntries']==33 and s['originalUnitCount']==2291
 assert s['actual2022BattleFormationsConfirmed']==0
 assert s['sameIdIn2022Catalog']<=s['distinctHistoricalUnitIds']
 assert s['exactEnglishNameMatches']<=s['sameIdIn2022Catalog']
 assert s['matchingThumbnailCount']<=s['sameIdIn2022Catalog']
 assert page.evaluate('BFGlobalSourceCrosscheckV150.coveredMissions')==[1,2,10,20]
 assert page.evaluate('BFGlobalSourceCrosscheckV150.identity(30030).historicName')=='Mossy'
 assert page.evaluate('BFGlobalSourceCrosscheckV150.identity(9999999)') is None
 before=page.evaluate("""()=>({
    p:JSON.stringify(P),s:JSON.stringify(S),
    save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf150-crosscheck').is_visible()
 page.locator('#bf150-crosscheck summary').click()
 assert page.locator('#bf150-waves .bf150-wave').count()==3
 assert page.locator('#bf150-waves .bf150-unit').count()==4
 page.locator('#bf150-select').select_option('20')
 assert page.locator('#bf150-waves .bf150-wave').count()==5
 assert page.locator('#bf150-waves .bf150-unit').count()==11
 assert page.evaluate('QUEST.missionId')==1,'Preview must not select locked quest'
 page.locator('#bf150-integrity summary').click()
 page.locator('#bf150-refresh').click()
 assert page.locator('#bf150-status').text_content().startswith('PASS')
 after=page.evaluate("""()=>({
    p:JSON.stringify(P),s:JSON.stringify(S),
    save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Cross-check and diagnostics must never write save/combat state'
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v1.50: source IDs, portrait-safe reference, 106 quests, 23 dungeons, 2291 units, save v7')
