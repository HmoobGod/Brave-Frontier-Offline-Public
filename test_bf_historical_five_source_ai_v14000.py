"""v140: five authentic 2014 historical Global archives (41 source AI slots).
2014-only source action selection inside isolated playable Archive Trials.
"""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_historical_five_mission_ai_v140.json').read_text('utf8'))
assert M['schema']=='bf-global-historical-2014-five-mission-attack-ai-source-v140'
assert M['archiveEra']==2014 and M['confirmed2022'] is False
assert M['totals']=={'missions':5,'waves':21,'slots':41}
assert {x['id'] for x in M['missions']}=={1,2,10,11,40}
assert sum(len(w) for m in M['missions'] for w in m['waves'])==41
assert sum(len(m['waves']) for m in M['missions'])==21
assert M['enemyAction']=={'type':'attack','actCount':1,'percent':100,
                           'parameters':'-1','targetCondition':'random',
                           'targetType':2,'conditions':0}
local=json.loads((R/'source_data/bf_global_historical_encounters_v120.json').read_text('utf8'))['missions']
local += [json.loads((R/f'source_data/historical_2014_v200/mission_{id}.json').read_text('utf8')) for id in (11,40)]
for m in M['missions']:
 expected=next(x for x in local if x['id']==m['id'])
 assert (m['sourcePath'],m['gitBlobSha'],m['name'])==(expected['sourcePath'],expected['gitBlobSha'],expected['name'])
 assert len(m['waves'])==len(expected['waves'])
 for expected_wave,rows in zip(expected['waves'],m['waves']):
  assert [[e['unitId'],e['name'],e['hp'],e['atk'],e['def'],e['aiId']] for e in expected_wave['enemies']]==rows
js=(A/'bf14000_five_historical_source_ai.js').read_text('utf8')
lab=(A/'bf200_historical_wave_lab.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert len(js.encode())<65536 and js.count('BF_GLOBAL_2014_FIVE_MISSION_SOURCE_AI_V14000')==1
assert 'function sourceEnemyPlan2014(foes)' in lab
assert 'BFHistoricalFiveMissionSourceAIV14000' in lab
assert java.index('readPackagedText("bf8700_original_basics_ai_reference.js")') < java.index('readPackagedText("bf14000_five_historical_source_ai.js")')
for text in (js,lab):
 assert 'saveProgress(' not in text and 'localStorage.' not in text and 'BFAndroid' not in text
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""() => {
  const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
   removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
              'bf110_quest_journal.js','bf120_historical_encounters.js',
              'bf_global_unit_archive.js','bf150_source_crosscheck.js',
              'bf200_historical_wave_lab.js','bf8700_original_basics_ai_reference.js',
              'bf14000_five_historical_source_ai.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFArchiveTrialsV200.missions')==21
 assert p.evaluate('BFHistoricalFiveMissionSourceAIV14000.source.missions')==5
 assert p.evaluate('BFHistoricalFiveMissionSourceAIV14000.source.slots')==41
 before=p.evaluate("""() => ({
  p:JSON.stringify(P),s:JSON.stringify(S),
  key:localStorage.getItem('bf_global_offline_demo_v7')
 })""")
 results=p.evaluate("""() => {
  const adapter=BFHistoricalFiveMissionSourceAIV14000;
  return [1,2,10,11,40].map(id=>{
    const src=BFArchiveTrialsV200.sourceFor(id);
    const decisions=src.waves.map((wave,i)=>{
       const roster=wave.enemies.map(e=>({...e,maxHp:e.hp}));
       const list=adapter.plan(id,i+1,roster);
       const noDead=[...roster];noDead[0].hp=0;
       const rest=adapter.plan(id,i+1,noDead);
       const invalid=[...roster];invalid[0]={...invalid[0],unitId:-123};
       return {wave:i+1,planned:list?.length,remaining:rest?.length,
         action:list?.every(a=>a.action==='attack' && a.sourceWeight===100 &&
                    a.nativeRandomTargetImplemented===false && a.syntheticHarm>0),
         frozen:Object.isFrozen(list),reject:adapter.plan(id,i+1,invalid)===null};
    });
    return {id,source:adapter.lookup(id)?.gitBlobSha,decisions};
  });
 }""")
 for row in results:
  m=next(x for x in M['missions'] if x['id']==row['id'])
  assert row['source']==m['gitBlobSha']
  assert len(row['decisions'])==len(m['waves'])
  for actual,refwave in zip(row['decisions'],m['waves']):
   assert actual=={'wave':actual['wave'],'planned':len(refwave),
                   'remaining':len(refwave)-1,'action':True,
                   'frozen':True,'reject':True},actual
 assert p.evaluate('BFHistoricalFiveMissionSourceAIV14000.plan(200,1,[])') is None
 assert p.evaluate('BFHistoricalFiveMissionSourceAIV14000.plan(1,0,[])') is None
 assert p.evaluate('BFArchiveTrialsV200.startPractice(1)') is True
 assert p.evaluate('BFArchiveTrialsV200.perform("guard")') is True
 live=p.evaluate('BFArchiveTrialsV200.practice')
 assert any('2014 source AI: Mossy #30030 ATTACK 100% (1 action)' in q for q in live['recent'])
 assert any('random target NOT simulated' in q for q in live['recent'])
 p.evaluate('BFArchiveTrialsV200.resetPractice()')
 after=p.evaluate("""() => ({
  p:JSON.stringify(P),s:JSON.stringify(S),
  key:localStorage.getItem('bf_global_offline_demo_v7')
 })""")
 assert before==after,'2014 mission AI selector must never mutate main combat/player/save'
 assert not errors,errors
 b.close()
print('PASS v140: 41 exact 2014 AI source enemy slots, 21 waves, 5 historical missions, executable practice decisions, KO/mismatch guards and save isolation')
