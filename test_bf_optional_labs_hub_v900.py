"""v9.00: preserves original Quest screen while grouping five optional research labs."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
script=(A/'bf900_optional_labs_hub.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert script.count('/* BF_GLOBAL_OPTIONAL_LABS_HUB_V900 */')==1
assert len(script.encode('utf8'))<65536
assert 'localStorage' not in script and 'saveProgress(' not in script
assert java.index('readPackagedText("bf800_archive_draft.js")')<java.index('readPackagedText("bf900_optional_labs_hub.js")')
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
    'bf200_historical_wave_lab.js','bf250_squad_training.js',
    'bf500_source_bb_evidence.js','bf700_original_normal_hits.js',
    'bf300_tactical_rounds.js','bf400_original_battle_dossier.js',
    'bf800_archive_draft.js','bf900_optional_labs_hub.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7 and page.evaluate('QUESTS.length')==106
 assert page.evaluate('BFOptionalLabsHubV900.labCount')==5
 assert page.evaluate('BFOptionalLabsHubV900.open') is False
 assert page.evaluate('BFOptionalLabsHubV900.labIds')==[
  'bf200-trials','bf250-squad','bf300-tactics','bf400-dossier','bf800-draft']
 assert page.locator('#bf900-labs-content > details').count()==5
 assert page.evaluate('BFOptionalLabsHubV900.refresh().total')==106
 assert page.evaluate('BFOptionalLabsHubV900.refresh().archiveForms')==2291
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf900-labs > summary').is_visible()
 assert not page.locator('#bf250-squad').is_visible()
 assert page.locator('#questlist').count()==1
 page.locator('#bf900-labs > summary').click()
 assert page.evaluate('BFOptionalLabsHubV900.open') is True
 assert page.locator('#bf250-squad').is_visible()
 assert '2,291' in page.locator('#bf900-coverage').inner_text()
 page.locator('#bf300-tactics > summary').click()
 assert page.evaluate('BFTacticalRoundsV300.canStart(1)') is True
 assert page.evaluate('BFTacticalRoundsV300.startTrial(1)') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.mode')=='owned'
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 page.locator('#bf800-draft > summary').click()
 assert page.evaluate('BFArchiveDraftV800.add(10012)') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[10012]
 assert page.evaluate('BFOptionalLabsHubV900.closeHub()') is True
 assert not page.locator('#bf250-squad').is_visible()
 assert page.evaluate('BFOptionalLabsHubV900.openHub().labs')==5
 assert page.locator('#bf800-draft').is_visible()
 assert page.evaluate('BFOptionalLabsHubV900.closeHub()') is True
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Optional lab hub must not mutate native game/save state'
 assert not errors,errors
 browser.close()
print('PASS v9.00 Quest screen uncluttered, five labs preserved under one disclosure and full v7 save isolation')
