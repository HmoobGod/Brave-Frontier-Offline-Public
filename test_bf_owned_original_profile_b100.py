"""Current owned form -> archive link revalidates stale/Auto/Repeat state."""
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
 page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box');BFUnitBox.showDetail(P.roster[0])")
 stable=page.evaluate("JSON.stringify({P,S,mission:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")
 blocked=page.evaluate("""()=>{const old=BFGlobalUnitArchive,repeat=window.BFGlobalQoLQuestRepeatV9800,resolve=window.effectiveUnit,roster=P.roster,button=document.querySelector('.bf-box-original-profile');let calls=0;window.BFGlobalUnitArchive={...old,showDetail:(...args)=>{calls++;return old.showDetail(...args)}};const out=[];
 try{for(const mode of ['busy','auto','repeat','unknown','stale','removed']){S.busy=mode==='busy';S.auto=mode==='auto';window.BFGlobalQoLQuestRepeatV9800=repeat;window.effectiveUnit=resolve;P.roster=roster;
 if(mode==='repeat'||mode==='unknown')window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>mode==='unknown'?null:{active:true}};
 if(mode==='stale')window.effectiveUnit=id=>({...resolve(id),id:10012});if(mode==='removed')P.roster=[];
 const count=calls;button.dispatchEvent(new MouseEvent('click',{bubbles:true}));out.push(calls===count);}
 }finally{S.busy=false;S.auto=false;window.BFGlobalQoLQuestRepeatV9800=repeat;window.effectiveUnit=resolve;P.roster=roster;window.BFGlobalUnitArchive=old;}return out;}""")
 assert blocked==[True]*6,blocked
 page.locator('.bf-box-original-profile').click()
 assert page.locator('#bf-archive-detail').is_visible()
 assert page.evaluate("document.activeElement.matches('#bf-archive-detail h4')")
 assert page.evaluate("JSON.stringify({P,S,mission:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")==stable
 assert not errors,errors
 browser.close()
print('PASS native owned-profile source link, six stale/Auto/Repeat cases, focus and full state invariance')
