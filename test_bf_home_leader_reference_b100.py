"""Home leader description follows the current owned form and source readiness."""
from pathlib import Path
import shutil,json
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
 for name in ('bf11000_source_starter_leader_skills.js','bf11200_all_playable_leader_source.js','bf11400_original_global_leader_english.js'):page.add_script_tag(path=str(A/name))
 row=page.evaluate('BFHomeLeaderReferenceB100.snapshot()')
 assert row and row['unitId']==page.evaluate('effectiveUnit(P.squad[0]).id'),row
 source=json.loads((R/'source_data/bf_global_2022_playable_leader_english_v114.json').read_text())
 oracle=next(x for x in source['records'] if x['leaderSkillId']==row['leaderId'])
 assert row['name']==oracle['originalEnglishName'] and row['description']==oracle['originalEnglishDescription']
 assert row['appliesEffects'] is False
 assert row['name'] in page.locator('#bf-home-leader-text').text_content() # readiness event refreshed first Home
 stable=page.evaluate("JSON.stringify({P,S,save:localStorage.getItem('bf_global_offline_demo_v7')})")
 proof=page.evaluate("""()=>{const squad=P.squad,provider=window.BFGlobalOriginalLeaderEnglishV11400;const out=[];try{P.squad=[squad[0],squad[0]];out.push(BFHomeLeaderReferenceB100.refresh()===null);P.squad=squad;window.BFGlobalOriginalLeaderEnglishV11400={source:provider.source,forUnit:()=>{throw Error('fixture')}};out.push(BFHomeLeaderReferenceB100.refresh()===null);}finally{P.squad=squad;window.BFGlobalOriginalLeaderEnglishV11400=provider;BFHomeLeaderReferenceB100.refresh();}return out;}""")
 assert proof==[True]*2,proof
 assert page.evaluate("JSON.stringify({P,S,save:localStorage.getItem('bf_global_offline_demo_v7')})")==stable
 assert not errors,errors
 browser.close()
print('PASS Home exact original leader text, source-ready event, ambiguous/provider failure and full state invariance')
