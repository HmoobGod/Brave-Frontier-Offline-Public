"""Reveal an inspected owned profile through view filters without marker writes."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
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
  'bf1000_original_evolution_paths.js','bf1400_evolution_material_planner.js'):
  page.add_script_tag(path=str(A/name))
 page.add_script_tag(path=str(A/'bf10200_qol_unit_flags.js'))
 page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box');BFGlobalQoLUnitFlagsV10200.setFilter('favorites')")
 page.locator('#bf-box-search').fill('NO_OWNED_MATCH')
 page.evaluate('BFUnitBox.showDetail(P.roster[1])')
 id=page.evaluate('P.roster[1]')
 passive=page.evaluate("JSON.stringify({P,S,markers:localStorage.getItem(BFGlobalQoLUnitFlagsV10200.key),save:localStorage.getItem('bf_global_offline_demo_v7')})")
 page.locator('.bf-box-reveal-owned').click()
 assert page.locator('#bf-box-search').input_value()==''
 assert page.locator(f'[data-bf-unit-id="{id}"]').is_visible()
 assert page.evaluate('document.activeElement.dataset.bfUnitId')==str(id)
 assert page.evaluate('BFUnitBox.revealOwned(999999999)') is False
 assert page.evaluate("JSON.stringify({P,S,markers:localStorage.getItem(BFGlobalQoLUnitFlagsV10200.key),save:localStorage.getItem('bf_global_offline_demo_v7')})")==passive
 assert not errors,errors
 browser.close()
print('PASS reveal inspected owned profile, actual Favorites filter recovery/focus and marker/v7/state invariance')
