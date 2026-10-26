"""v6.00: all 300 original Brave Burst skill levels, selectable offline practice."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
original=(A/'bf500_source_bb_evidence.js').read_text('utf8')
trial=(A/'bf300_tactical_rounds.js').read_text('utf8')
assert len(original.encode('utf8'))<65536 and len(trial.encode('utf8'))<65536
assert 'localStorage' not in original+trial and 'saveProgress(' not in original+trial
assert 'getAtLevel' in original and 'setSkillLevel' in trial
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf500_source_bb_evidence.js")')<java.index('readPackagedText("bf300_tactical_rounds.js")')
power=json.loads((R/'source_data/bf_global_original_bb_power_v030.json').read_text('utf8'))
support=json.loads((R/'source_data/bf_global_original_bb_support_v029.json').read_text('utf8'))
assert len(power['skills'])==24 and len(support['skills'])==6
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
 for n in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
  'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
  'bf110_quest_journal.js','bf120_historical_encounters.js',
  'bf_global_unit_archive.js','bf150_source_crosscheck.js',
  'bf200_historical_wave_lab.js','bf250_squad_training.js',
  'bf500_source_bb_evidence.js','bf300_tactical_rounds.js',
  'bf400_original_battle_dossier.js'):
  page.add_script_tag(path=str(A/n))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFOriginalBBV500.count')==30
 assert page.evaluate('BFOriginalBBV500.levelCount')==10
 assert page.evaluate('BFOriginalBBV500.sourceLevelEntries')==300
 assert page.evaluate('BFOriginalBBV500.getAtLevel(10011,0)') is None
 assert page.evaluate('BFOriginalBBV500.getAtLevel(10011,11)') is None
 assert page.evaluate('BFOriginalBBV500.getAtLevel(999999,1)') is None
 assert page.evaluate('BFOriginalBBV500.getAtLevel(10011,1.5)') is None
 total=0
 for id,item in power['skills'].items():
  for lv in item['levels']:
   actual=page.evaluate('([id,n])=>BFOriginalBBV500.getAtLevel(id,n)',[int(id),lv['level']])
   assert actual['kind']=='attack' and actual['name']==item['name'],id
   assert actual['target']==item['target'],id
   assert actual['level']==lv['level'],id
   assert actual['pct']==lv['damageModifierPct'],id
   assert actual['effectCode']==lv['effectCode'],id
   total+=1
 for id,item in support['skills'].items():
  for lv in item['levels']:
   actual=page.evaluate('([id,n])=>BFOriginalBBV500.getAtLevel(id,n)',[int(id),lv['level']])
   assert actual['name']==item['name'] and actual['level']==lv['level'],id
   assert actual['effectCode']==lv['effectCode'],id
   if item['level1DemoEffect']['type']=='heal_all':
    assert actual['low']==lv['params'][0] and actual['high']==lv['params'][1],id
   else:
    assert actual['pct']==lv['params'][1] and actual['rounds']==lv['params'][5],id
   total+=1
 assert total==300
 page.evaluate('BFOriginalBBV500.getAtLevel(10011,10).pct=999')
 assert page.evaluate('BFOriginalBBV500.getAtLevel(10011,10).pct')==75
 assert page.evaluate('BFOriginalBBV500.get(10011).pct')==30
 assert page.evaluate('BFOriginalBBV500.getAtLevel(20041,10).low')==870
 assert page.evaluate('BFOriginalBBV500.getAtLevel(40021,10).pct')==40
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf300-tactics > summary').click()
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('BFTacticalRoundsV300.startTrial(1)') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.sourceBBLevels')==10
 assert page.evaluate('BFTacticalRoundsV300.snapshot.party[0].bbLevel')==1
 assert page.evaluate('BFTacticalRoundsV300.setSkillLevel(10011,0)') is False
 assert page.evaluate('BFTacticalRoundsV300.setSkillLevel(10011,11)') is False
 assert page.evaluate('BFTacticalRoundsV300.setSkillLevel(99999,10)') is False
 assert page.evaluate('BFTacticalRoundsV300.setSkillLevel(10011,1.5)') is False
 # Use actual first unit's browser-visible Source Level dropdown.
 level_select=page.locator('#bf300-planner .bf300-planner').first.locator('select').first
 assert level_select.locator('option').count()==10
 level_select.select_option('10')
 assert page.evaluate('BFTacticalRoundsV300.snapshot.party[0].bbLevel')==10
 assert '75% first damage modifier' in page.locator('#bf300-planner .bf300-planner').first.inner_text()
 # Two normal rounds charge Vargas while other five allies guard.
 for _ in range(2):
  snap=page.evaluate('BFTacticalRoundsV300.snapshot')
  for u in snap['party'][1:]:
   assert page.evaluate('(id)=>BFTacticalRoundsV300.plan(id,"guard",0,id)',u['sourceId']) is True
  assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.party[0].burst')==2
 assert page.evaluate('BFTacticalRoundsV300.plan(10011,"sourcebb",0,10011)') is True
 before_burst=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert before_burst['party'][0]['bbLevel']==10
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 after_burst=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert any('Flare Ride' in line and 'Lv10 modifier 75%' in line
   for line in after_burst['recent']),after_burst['recent']
 assert after_burst['party'][0]['burst']==0
 assert page.evaluate('BFTacticalRoundsV300.undoLastRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot')==before_burst
 # Switch levels without changing the charged gauge or actual character.
 assert page.evaluate('BFTacticalRoundsV300.setSkillLevel(10011,1)') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.party[0].bbLevel')==1
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 assert any('Flare Ride' in line and 'Lv1 modifier 30%' in line
   for line in page.evaluate('BFTacticalRoundsV300.snapshot.recent'))
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Source level preview and simulation must not change original save'
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 assert not errors,errors
 browser.close()
print('PASS v6.00: 300 original source level values, BB levels 1-10, interactive level selector, undo and save isolation')
