"""v141: original 2014 source action evidence in four mixed historical missions.

Only 40 of 46 enemies have fully authenticated one-attack behavior;
six complex original 2014 AIs are isolated as DEMO fallback, never invented.
"""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_historical_mixed_ai_v141.json').read_text('utf8'))
assert M['schema']=='bf-global-historical-2014-four-mixed-mission-ai-v141'
assert M['era']==2014 and M['confirmed2022'] is False
assert M['totals']=={'missions':4,'waves':20,'slots':46,'simple':40,'complex':6}
assert {x['id'] for x in M['missions']}=={20,21,30,31}
orig=json.loads((R/'source_data/bf_global_historical_encounters_v120.json').read_text('utf8'))['missions']
orig += [json.loads((R/f'source_data/historical_2014_v200/mission_{id}.json').read_text('utf8')) for id in (21,30,31)]
simple=complex=0
for m in M['missions']:
 q=next(x for x in orig if x['id']==m['id'])
 assert (m['name'],m['gitBlobSha'],m['sourcePath'])==(q['name'],q['gitBlobSha'],q['sourcePath'])
 assert len(m['waves'])==len(q['waves'])
 for oldwave,newwave in zip(q['waves'],m['waves']):
  assert len(oldwave['enemies'])==len(newwave)
  for e,old in zip(newwave,oldwave['enemies']):
   assert [e[k] for k in ('unitId','name','hp','atk','def','aiId')]==[old[k] for k in ('unitId','name','hp','atk','def','aiId')]
   assert len(e['actions'])>=1
   if e['simpleAttack']:
    simple+=1
    assert e['actCounts']=='1~1' and len(e['actions'])==1
    assert e['actions'][0]=={'type':'attack','parameters':'-1','weight':100,
      'targetCondition':'random','targetType':2,'conditionCount':0}
   else:complex+=1
assert (simple,complex)==(40,6)
assert [(m['id'],wi+1,e['name'],e['actCounts']) for m in M['missions']
  for wi,w in enumerate(m['waves']) for e in w if not e['simpleAttack']]==[
 (20,2,'Fire Nymph','1~2'),(20,4,'Thief Leon','1~1'),
 (21,5,'Warlock Liza','1~2'),(30,2,'Pirate Verica','1~1'),
 (31,3,'Water Nymph','1~2'),(31,5,'Healer Merith','1~2')]
js=(A/'bf14100_mixed_historical_source_ai.js').read_text('utf8')
lab=(A/'bf200_historical_wave_lab.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert js.count('BF_GLOBAL_2014_MIXED_MISSION_SOURCE_AI_V14100')==1
assert 'UNMODELED COMPLEX AI (synthetic reply)' in lab
assert 'BFHistoricalMixedMissionSourceAIV14100' in lab
assert java.index('readPackagedText("bf14000_five_historical_source_ai.js")')<java.index('readPackagedText("bf14100_mixed_historical_source_ai.js")')
for s in (js,lab):assert not any(x in s for x in ('saveProgress(', 'localStorage.', 'BFAndroid', 'fetch('))
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
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
   'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
   'bf110_quest_journal.js','bf120_historical_encounters.js',
   'bf_global_unit_archive.js','bf150_source_crosscheck.js',
   'bf200_historical_wave_lab.js','bf8700_original_basics_ai_reference.js',
   'bf14000_five_historical_source_ai.js','bf14100_mixed_historical_source_ai.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFHistoricalMixedMissionSourceAIV14100.source.slots')==46
 assert p.evaluate('BFHistoricalMixedMissionSourceAIV14100.source.simple')==40
 assert p.evaluate('BFHistoricalMixedMissionSourceAIV14100.source.complex')==6
 before=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
     save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 actual=p.evaluate("""() => {
  const ai=BFHistoricalMixedMissionSourceAIV14100;
  return [20,21,30,31].map(id=>{
    const quest=BFArchiveTrialsV200.sourceFor(id);
    const decisions=quest.waves.map((w,i)=>{
      const enemies=w.enemies.map(e=>({...e,maxHp:e.hp}));
      const actions=ai.plan(id,i+1,enemies);
      const dead=enemies.map(e=>({...e}));dead[0].hp=0;
      const without=ai.plan(id,i+1,dead);
      const invalid=enemies.map(e=>({...e}));
      invalid[0].aiId=9999;
      return {total:actions?.length,valid:Array.isArray(actions)&&Object.isFrozen(actions),
        safe:actions?.filter(a=>a.sourceBacked&&a.action==='attack'&&a.sourceWeight===100).length,
        fallback:actions?.filter(a=>!a.sourceBacked&&a.action==='unmodeled-source-fallback'&&a.sourceWeight===null).length,
        afterKo:without?.length,bad:ai.plan(id,i+1,invalid)===null};
    });
    return {id,decisions};
  });
 }""")
 for row in actual:
  m=next(x for x in M['missions'] if x['id']==row['id'])
  for decision,sourcewave in zip(row['decisions'],m['waves']):
   assert decision=={'total':len(sourcewave),'valid':True,
     'safe':sum(x['simpleAttack'] for x in sourcewave),
     'fallback':sum(not x['simpleAttack'] for x in sourcewave),
     'afterKo':len(sourcewave)-1,'bad':True},decision
 assert p.evaluate('BFHistoricalMixedMissionSourceAIV14100.plan(99,1,[])') is None
 assert p.evaluate('BFHistoricalMixedMissionSourceAIV14100.plan(20,0,[])') is None
 assert p.evaluate('BFArchiveTrialsV200.startPractice(1)') is True
 assert p.evaluate('BFArchiveTrialsV200.perform("guard")') is True
 assert any('2014 source AI: Mossy' in s for s in p.evaluate('BFArchiveTrialsV200.practice.recent'))
 p.evaluate('BFArchiveTrialsV200.resetPractice()')
 after=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
     save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after, 'historical source AI must not alter the owner game or save'
 assert not errors,errors
 b.close()
print('PASS v141: 46 2014 source original AI records, 40 safely modeled attack decisions, 6 complex DEMO fallbacks, all 20 waves, save isolated')
