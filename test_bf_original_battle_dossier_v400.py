"""v4.00: authentic 2022 owned skill dossier and historically scoped enemy records."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf400_original_battle_dossier.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert js.count('/* BF_GLOBAL_ORIGINAL_BATTLE_DOSSIER_V400 */')==1
assert len(js.encode('utf8'))<65536
assert 'localStorage' not in js and 'saveProgress(' not in js and 'BFAndroid' not in js
assert java.index('readPackagedText("bf300_tactical_rounds.js")')<java.index('readPackagedText("bf400_original_battle_dossier.js")')
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
  'bf300_tactical_rounds.js','bf400_original_battle_dossier.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('QUESTS.length')==106
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFGlobalBattleDossierV400.missionCount')==21
 assert page.evaluate('BFGlobalBattleDossierV400.sourceYear')==2014
 assert page.evaluate('BFGlobalBattleDossierV400.originalUnitCount')==2291
 owned=page.evaluate('BFGlobalBattleDossierV400.squad')
 assert len(owned)==6
 assert [x['sourceId'] for x in owned]==page.evaluate('P.squad')
 assert owned[0]['formId']==10011
 assert owned[0]['originalSkillAvailable'] is True
 assert page.evaluate('BFGlobalBattleDossierV400.showUnit(10011).skillNames.includes("Flare Ride")')
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf400-dossier > summary').click()
 assert page.locator('#bf400-dossier').is_visible()
 assert page.locator('#bf400-unit option').count()==6
 assert 'Flare Ride' in page.locator('#bf400-unit-skills').inner_text()
 assert 'NOT simulated' in page.locator('#bf400-unit-skills').inner_text()
 assert page.locator('#bf400-mission option').count()==21
 assert page.evaluate('BFGlobalBattleDossierV400.showMission(1)') is True
 assert page.locator('#bf400-wave option').count()==3
 foe=page.evaluate('BFGlobalBattleDossierV400.waveEntries')
 assert len(foe)==1 and foe[0]['name']=='Mossy'
 assert foe[0]['hp']==300 and foe[0]['unitId']==30030
 assert foe[0]['sourceYear']==2014
 assert page.evaluate('BFGlobalBattleDossierV400.showWave(2)') is True
 foe=page.evaluate('BFGlobalBattleDossierV400.waveEntries')
 assert [x['name'] for x in foe]==['Sparky','Mossy']
 assert page.evaluate('BFGlobalBattleDossierV400.showWave(99)') is False
 assert page.locator('#bf400-wave-foes .bf400-row').count()==2
 assert 'Verified native 2022 formations: 0' in page.locator('#bf400-integrity').inner_text()
 assert page.evaluate('BFGlobalBattleDossierV400.showMission(200)') is True
 assert page.locator('#bf400-wave option').count()==7
 page.locator('#bf400-unit').select_option('20011')
 assert 'Selena' in page.locator('#bf400-unit-card').inner_text()
 page.evaluate('BFGlobalBattleDossierV400.refreshSquad()')
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Research UI must never mutate original player, battle or v7 save'
 assert not errors,errors
 browser.close()
print('PASS v4.00: 2022 owned unit skill intel, 21 historic 2014 mission dossiers, provenance and no save edits')
