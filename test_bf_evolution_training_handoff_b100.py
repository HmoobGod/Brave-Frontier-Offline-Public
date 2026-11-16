"""Native guarded Evolution -> Training handoff, disposable storage only."""
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
  'bf1000_original_evolution_paths.js','bf1400_evolution_material_planner.js','bf10400_qol_evolution_needs.js'):
  page.add_script_tag(path=str(A/name))
 api='BFGlobalQoLEvolutionNeedsV10400'
 page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('evolve')")
 before=page.evaluate("JSON.stringify({P,S,quest:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")
 for width in (320,390,540):
  page.set_viewport_size({'width':width,'height':844})
  page.evaluate("BFInnerScreens.setTab('evolve');document.querySelector('#bf10400-evolution-needs').open=true;BFGlobalQoLEvolutionNeedsV10400.refresh()")
  assert page.locator('#bf10400-training-shortcut').bounding_box()['height']>=44
  page.locator('#bf10400-training-shortcut').click()
  assert page.locator('#traininglist').is_visible()
  assert page.evaluate("document.activeElement.id")=='bf-unit-tab-label'
  assert page.evaluate("JSON.stringify({P,S,quest:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")==before
 blocked=page.evaluate("""()=>{const api=BFGlobalQoLEvolutionNeedsV10400,repeat=window.BFGlobalQoLQuestRepeatV9800;const out=[];
 try{for(const mode of ['busy','auto','repeatTrue','repeatNull','repeatThrows','repeatString','missing']){
 BFInnerScreens.setTab('evolve');S.busy=false;S.auto=false;window.BFGlobalQoLQuestRepeatV9800=repeat;
 let removed=null;if(mode==='busy')S.busy=true;if(mode==='auto')S.auto=true;
 if(mode.startsWith('repeat'))window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>{if(mode==='repeatThrows')throw Error('fixture');return mode==='repeatNull'?null:{active:mode==='repeatString'?'false':true}}};
 if(mode==='missing'){removed=document.querySelector('#traininglist');removed.remove();}
 api.refresh();const disabled=document.querySelector('#bf10400-training-shortcut').disabled;
 out.push(disabled&&api.openTraining()===false&&BFInnerScreens.unitTab==='evolve');
 if(removed)document.body.append(removed);
 }}finally{S.busy=false;S.auto=false;window.BFGlobalQoLQuestRepeatV9800=repeat;api.refresh();}return out;}""")
 assert blocked==[True]*7,blocked
 assert page.evaluate("JSON.stringify({P,S,quest:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")==before
 assert not errors,errors
 browser.close()
print('PASS guarded native Evolution Training navigation, focus, three widths, seven blocked fixtures and complete state invariance')
