"""v12.00 source-stat lineup presets, original added order and save isolation."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf800_archive_draft.js').read_text('utf8')
assert len(js.encode('utf8'))<65536 and 'sortBy' in js
assert 'localStorage' not in js and 'saveProgress(' not in js
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
 for id in (10011,20011,30011,40011):
  assert page.evaluate('(id)=>BFArchiveDraftV800.add(id)',id) is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[10011,20011,30011,40011]
 for exp in ('BFArchiveDraftV800.sortBy("junk")',
             'BFArchiveDraftV800.sortBy(5)',
             'BFArchiveDraftV800.moveTo(10011,0)'):
  assert page.evaluate(exp) is False,exp
 def sort_expected(stat,initial):
  records=page.evaluate("""(ids)=>ids.map(id=>({
    id,atk:BFGlobalUnitArchive.find(id).unitBaseAtk,
    def:BFGlobalUnitArchive.find(id).unitBaseDef,
    rec:BFGlobalUnitArchive.find(id).unitBaseRec
  }))""",initial)
  return [x['id'] for x in sorted(records,key=lambda x:-x[stat])]
 # Same input original order for each stat ensures source-sort accuracy.
 for key in ('atk','def','rec'):
  assert page.evaluate('(k)=>BFArchiveDraftV800.sortBy(k)',key) is True
  assert page.evaluate('BFArchiveDraftV800.selected')==sort_expected(key,[10011,20011,30011,40011])
  assert page.evaluate('BFArchiveDraftV800.sortBy("original")') is True
  assert page.evaluate('BFArchiveDraftV800.selected')==[10011,20011,30011,40011]
 assert page.evaluate('BFArchiveDraftV800.moveTo(30011,1)') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[30011,10011,20011,40011]
 assert page.evaluate('BFArchiveDraftV800.sortBy("original")') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[10011,20011,30011,40011]
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf900-labs > summary').click()
 page.locator('#bf800-draft > summary').click()
 controls=page.locator('#bf1200-presets')
 assert controls.locator('button').count()==4
 controls.locator('button[data-bf1200-sort="atk"]').click()
 assert page.evaluate('BFArchiveDraftV800.selected')==sort_expected('atk',[10011,20011,30011,40011])
 controls.locator('button[data-bf1200-sort="original"]').click()
 assert page.evaluate('BFArchiveDraftV800.selected')==[10011,20011,30011,40011]
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('#bf800-start').click()
 state=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert state['mode']=='archive-draft'
 assert state['draftUnitIds']==[10011,20011,30011,40011]
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.undoLastRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot')==state
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Sorting the archive cannot modify the real game'
 assert page.evaluate('BFArchiveDraftV800.clear()') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[]
 assert not errors,errors
 browser.close()
print('PASS v12: original source base ATK/DEF/REC sorting, UI presets, action order, undo and save isolation')
