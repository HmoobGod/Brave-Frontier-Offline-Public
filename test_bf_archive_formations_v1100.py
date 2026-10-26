"""v11: source-only draft ordering, real browser buttons, undo, and save isolation."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf800_archive_draft.js').read_text('utf8')
assert 'localStorage' not in js and 'saveProgress(' not in js
assert len(js.encode('utf8'))<65536 and 'moveTo' in js
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
  'bf800_archive_draft.js','bf900_optional_labs_hub.js',
  'bf1000_original_evolution_paths.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFArchiveDraftV800.selected')==[]
 for unit in (10011,10012,20011):
  assert page.evaluate('(id)=>BFArchiveDraftV800.add(id)',unit) is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[10011,10012,20011]
 for code in ('BFArchiveDraftV800.move(10011,-1)',
  'BFArchiveDraftV800.move(20011,1)',
  'BFArchiveDraftV800.move(10011,0)',
  'BFArchiveDraftV800.move(999999,1)',
  'BFArchiveDraftV800.moveTo(10012,0)',
  'BFArchiveDraftV800.moveTo(10012,4)'):
  assert page.evaluate(code) is False,code
 assert page.evaluate('BFArchiveDraftV800.move(20011,-1)') is True
 assert page.evaluate('BFArchiveDraftV800.moveTo(10012,1)') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[10012,10011,20011]
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf900-labs > summary').click()
 page.locator('#bf800-draft > summary').click()
 rows=page.locator('#bf800-selected .bf800-entry')
 assert rows.count()==3
 assert 'SLOT 1' in rows.nth(0).inner_text()
 assert 'SLOT 3' in rows.nth(2).inner_text()
 rows.nth(0).locator('button[aria-label^="Move"]').last.click()
 assert page.evaluate('BFArchiveDraftV800.selected')==[10011,10012,20011]
 before=page.evaluate("""()=>({player:JSON.stringify(P),battle:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('#bf800-start').click()
 state=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert state['mode']=='archive-draft'
 assert state['draftUnitIds']==[10011,10012,20011]
 assert [u['unitId'] for u in state['party']]==[10011,10012,20011]
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.undoLastRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot')==state
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 after=page.evaluate("""()=>({player:JSON.stringify(P),battle:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Temporary formation must not affect actual squad or save'
 assert page.evaluate('BFArchiveDraftV800.clear()') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[]
 assert not errors,errors
 browser.close()
print('PASS v11 archive draft ordering, UI, tactical action/undo, unchanged actual save')
