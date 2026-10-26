"""v2.00: deterministic 2014 archive research, 21-mission practice and save isolation."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
d=json.loads((R/'source_data/bf_global_historical_wave_lab_v200.json').read_text('utf8'))
assert d['schema']=='bf-global-2014-historical-wave-lab-v200'
assert len(d['missions'])==d['totals']['missions']==21
assert sum(len(x['waves']) for x in d['missions'])==d['totals']['waves']==112
assert sum(len(w['enemies']) for m in d['missions'] for w in m['waves'])==d['totals']['entries']==264
assert len({e['unitId'] for m in d['missions'] for w in m['waves'] for e in w['enemies']})==d['totals']['units']==42
assert len({m['id'] for m in d['missions']})==21
assert all(len(m['gitBlobSha'])==40 and m['sourcePath'].startswith('missions_parsed/') for m in d['missions'])
js=(A/'bf200_historical_wave_lab.js').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert js.count('/* BF_GLOBAL_ARCHIVE_TRIALS_V200 */')==1
assert '/* BF200_DATA_READY */' in js and 'BF200_DATA_PLACEHOLDER' not in js
assert 'localStorage' not in js and 'saveProgress(' not in js and 'BFAndroid' not in js
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf150_source_crosscheck.js")')<java.index('readPackagedText("bf200_historical_wave_lab.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
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
              'bf110_quest_journal.js','bf120_historical_encounters.js',
              'bf_global_unit_archive.js','bf150_source_crosscheck.js',
              'bf200_historical_wave_lab.js'):
   page.add_script_tag(path=str(A/name))
 assert page.evaluate('QUESTS.length')==106
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFGlobalUnitArchive.count')==2291
 assert page.evaluate('BFArchiveTrialsV200.missions')==21
 assert page.evaluate('BFArchiveTrialsV200.historicalWaves')==112
 assert page.evaluate('BFArchiveTrialsV200.historicalEntries')==264
 assert page.evaluate('BFArchiveTrialsV200.distinctUnitIds')==42
 assert page.evaluate('BFArchiveTrialsV200.sourceFor(200).waves.length')==7
 assert page.evaluate('BFArchiveTrialsV200.sourceFor(240).waves.length')==7
 assert page.evaluate('BFArchiveTrialsV200.sourceFor(9999)') is None
 assert page.evaluate('BFArchiveTrialsV200.startPractice(200)') is False
 assert page.evaluate('BFArchiveTrialsV200.startPractice(1)') is True
 assert page.evaluate('BFArchiveTrialsV200.practice.enemies[0].name')=='Mossy'
 assert page.evaluate('BFArchiveTrialsV200.perform("burst")') is False
 assert page.evaluate('BFArchiveTrialsV200.perform("attack")') is True
 assert page.evaluate('BFArchiveTrialsV200.practice.wave')==2
 assert page.evaluate('BFArchiveTrialsV200.perform("guard")') is True
 assert page.evaluate('BFArchiveTrialsV200.perform("heal")') is True
 before=page.evaluate("""()=>({
    state:JSON.stringify(P),session:JSON.stringify(S),
    save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 outcome=page.evaluate("""() => {
   for(let i=0;i<120&&BFArchiveTrialsV200.practice.state==='running';i++){
     if(BFArchiveTrialsV200.practice.burst>=2)BFArchiveTrialsV200.perform('burst');
     else BFArchiveTrialsV200.perform('attack');
   }
   return BFArchiveTrialsV200.practice;
 }""")
 assert outcome['state']=='won',outcome
 assert outcome['wave']==3
 assert 'No game progress or rewards' in ' '.join(outcome['recent'])
 after=page.evaluate("""()=>({
    state:JSON.stringify(P),session:JSON.stringify(S),
    save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Practice must not mutate original battle, game state or save'
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf200-trials summary').click()
 assert page.locator('#bf200-trials').is_visible()
 assert page.locator('#bf200-mission option').count()==21
 page.locator('#bf200-mission').select_option('200')
 assert page.locator('#bf200-start').is_disabled()
 assert page.locator('#bf200-reference .bf200-wave').count()==7
 assert 'NOT native 2022' in page.locator('.bf200-alert').first.text_content()
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v2.00: 21 historical missions, 112 waves, 264 enemies, independent no-save practice')
