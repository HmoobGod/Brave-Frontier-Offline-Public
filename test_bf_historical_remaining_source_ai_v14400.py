"""v144: original 2014 Global source AI complete coverage across 21 history missions.
177 slots in the remaining 12 parsed missions; native 2022 AI is NOT claimed.
"""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
D=[json.loads((R/f'source_data/bf_global_historical_remaining_ai_v144_part_{p}.json').read_text('utf8')) for p in ('a','b')]
expected=[{'waves':31,'slots':82,'simple':73,'complex':9},
          {'waves':40,'slots':95,'simple':75,'complex':20}]
for index,data in enumerate(D):
 assert data['schema']==f"bf-original-historical-2014-source-ai-remaining-v144-part-{'ab'[index]}"
 assert data['originalEra']==2014 and data['confirmed2022'] is False
 assert data['totals']==expected[index]
M=[m for d in D for m in d['missions']]
assert {x['id'] for x in M}=={41,42,50,51,52,60,61,70,71,200,202,240}
assert len(M)==12
assert sum(len(m['waves']) for m in M)==71
assert sum(len(w) for m in M for w in m['waves'])==177
assert sum(e['simpleAttack'] for m in M for w in m['waves'] for e in w)==148
assert sum(not e['simpleAttack'] for m in M for w in m['waves'] for e in w)==29
for mission in M:
 origin=json.loads((R/f"source_data/historical_2014_v200/mission_{mission['id']}.json").read_text('utf8'))
 assert (mission['name'],mission['sourcePath'],mission['gitBlobSha']) == (origin['name'],origin['sourcePath'],origin['gitBlobSha'])
 assert len(mission['waves'])==len(origin['waves'])
 for row,previous in zip(mission['waves'],origin['waves']):
  assert len(row)==len(previous['enemies'])
  for e,o in zip(row,previous['enemies']):
   assert [e[k] for k in ('unitId','name','hp','atk','def','aiId')]==[o[k] for k in ('unitId','name','hp','atk','def','aiId')]
   a=e['actions']
   safe=e['actCounts']=='1~1' and len(a)==1 and a[0]=={
     'type':'attack','parameters':'-1','weight':100,
     'targetCondition':'random','targetType':2,'conditionCount':0}
   assert e['simpleAttack'] is safe,(mission['id'],e['name'],e['aiId'])
js=(A/'bf14400_remaining_historical_source_ai.js').read_text('utf8')
lab=(A/'bf200_historical_wave_lab.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert js.count('BF_GLOBAL_HISTORICAL_2014_COMPLETE_SOURCE_AI_V14400')==1
assert 'BFHistoricalRemainingMissionSourceAIV14400' in lab
assert 'UNMODELED COMPLEX AI (synthetic reply)' in lab
assert java.index('readPackagedText("bf14100_mixed_historical_source_ai.js")') < java.index('readPackagedText("bf14400_remaining_historical_source_ai.js")')
for s in (js,lab):
 assert not any(x in s for x in ('saveProgress(', 'localStorage.', 'BFAndroid', 'fetch('))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""() => {
  const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
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
   'bf14000_five_historical_source_ai.js',
   'bf14100_mixed_historical_source_ai.js',
   'bf14400_remaining_historical_source_ai.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFArchiveTrialsV200.missions')==21
 assert p.evaluate('BFHistoricalRemainingMissionSourceAIV14400.source.slots')==177
 assert p.evaluate('BFHistoricalRemainingMissionSourceAIV14400.source.simple')==148
 assert p.evaluate('BFHistoricalRemainingMissionSourceAIV14400.source.complex')==29
 before=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
       save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 results=p.evaluate("""() => {
  const ai=BFHistoricalRemainingMissionSourceAIV14400;
  return [41,42,50,51,52,60,61,70,71,200,202,240].map(id=>{
    const q=BFArchiveTrialsV200.sourceFor(id);
    return {id,source:ai.lookup(id)?.gitBlobSha,
      waves:q.waves.map((w,i)=>{
        const foes=w.enemies.map(e=>({...e,maxHp:e.hp}));
        const list=ai.plan(id,i+1,foes);
        const withKo=foes.map(e=>({...e}));
        withKo[0].hp=0;
        const invalid=foes.map(e=>({...e}));
        invalid[0].unitId=-555;
        return {total:list?.length,
          safe:list?.filter(a=>a.sourceBacked===true&&a.action==='attack'&&a.sourceWeight===100).length,
          complex:list?.filter(a=>a.sourceBacked===false&&a.action==='unmodeled-source-fallback'&&a.sourceWeight===null).length,
          dead:ai.plan(id,i+1,withKo)?.length,
          bad:ai.plan(id,i+1,invalid)===null,
          frozen:Object.isFrozen(list)};
      })};
  });
 }""")
 for observed in results:
  m=next(x for x in M if x['id']==observed['id'])
  assert observed['source']==m['gitBlobSha']
  for row,source in zip(observed['waves'],m['waves']):
   assert row=={'total':len(source),
    'safe':sum(x['simpleAttack'] for x in source),
    'complex':sum(not x['simpleAttack'] for x in source),
    'dead':len(source)-1,'bad':True,'frozen':True},row
 assert p.evaluate('BFHistoricalRemainingMissionSourceAIV14400.plan(1,1,[])') is None
 assert p.evaluate('BFHistoricalRemainingMissionSourceAIV14400.plan(200,0,[])') is None
 assert p.evaluate('BFArchiveTrialsV200.startPractice(1)') is True
 assert p.evaluate('BFArchiveTrialsV200.perform("guard")') is True
 assert any('2014 source AI: Mossy' in x for x in p.evaluate('BFArchiveTrialsV200.practice.recent'))
 p.evaluate('BFArchiveTrialsV200.resetPractice()')
 after=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
       save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'2014 historical source AI cannot mutate normal game or v7 saves'
 assert not errors,errors
 b.close()
print('PASS v144: exact 177 remaining 2014 source AI slots, 148 normal attacks, 29 visibly synthetic complex cases; all 21 historical missions covered; v7 saves unchanged')
