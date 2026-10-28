"""v148: six original Global 7★ elemental starters in ephemeral, non-saving combat.
Confirms original 2022 hit timelines + CGS data run in DEMO engine; NEVER unlocks 7★.
"""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
raw=json.loads((R/'source_data/bf_global_2022_starter_7_8_source_readiness_v127.json').read_text('utf8'))
assert raw['schema']=='bf-global-2022-7-8-starter-source-readiness-v127'
assert raw['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
rows={x['unitId']:x for x in raw['rows']}
ids=(10016,20016,30016,40016,50016,60016)
assert all(id in rows for id in ids)
hits={10016:10,20016:9,30016:8,40016:1,50016:8,60016:7}
drops={10016:3,20016:4,30016:5,40016:30,50016:6,60016:6}
stats={
 10016:{'hp':4250,'atk':1330,'def':1165,'rec':1100},
 20016:{'hp':4080,'atk':1320,'def':1080,'rec':1360},
 30016:{'hp':4220,'atk':1325,'def':1280,'rec':810},
 40016:{'hp':4250,'atk':1330,'def':1165,'rec':1100},
 50016:{'hp':4030,'atk':1285,'def':1285,'rec':1285},
 60016:{'hp':4750,'atk':1190,'def':1330,'rec':770}
}
for id in ids:
 r=rows[id]
 assert (r['rarity'],r['unitMaxLevel'],r['unitCost'],r['expPatternId'])==(7,120,38,10)
 assert r['base']==stats[id]
 assert r['previousFormId']==id-1
 assert r['animation']['cggSourceFrameCount']>=15
 assert r['animation']['nativeRendererProven'] is False
 assert r['originalEvo']['zel']==1500000 and r['originalEvo']['karma']==0
 assert len(r['originalEvo']['materialSlots'])==5
 assert r['originalEvo']['materialSlots'][-1]['type']==2
 assert r['originalEvo']['materialSlots'][-1]['id']==110100
html=(A/'index.html').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda err:errors.append(str(err)))
 p.evaluate("""() => {
  const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
   removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content(html,wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 assert p.evaluate('UNIT_BY_ID.size')==72
 for id in ids:
  assert p.evaluate('id=>!UNIT_BY_ID.has(id)',id) is True,id
 p.add_script_tag(path=str(A/'bf12500_full_original_normal_hits.js'))
 p.add_script_tag(path=str(A/'bf12800_original_starter_cgg_cgs.js'))
 assert p.evaluate('async()=>await BFGlobalOriginalStarterCggV12800.ready') is True
 p.wait_for_function('()=>!!window.BFGlobalOriginalNormalHitArchiveV12500?.lookup?.(60016)',timeout=30000)
 # All original CGG/CGS attack frames and normal-hit event weights are
 # sourced from authenticated 2022 masters; the DEMO damage is not native.
 overview=p.evaluate("""ids=>ids.map(id=>{
  const c=BFGlobalOriginalStarterCggV12800.lookup(id);
  const h=BFGlobalOriginalNormalHitArchiveV12500.lookup(id);
  return {id,frameCount:c?.cggFrameCount,attack:c?.sequences?.atk||[],
    events:h?.events||[],weights:h?.weightsTotal,
    originalSource:h?.original2022,
    inLiveRoster:UNIT_BY_ID.has(id)};
 })""",list(ids))
 for row in overview:
  id=row['id'];m=rows[id]
  assert row['frameCount']==m['animation']['cggSourceFrameCount'],row
  assert len(row['attack'])>=1 and all(len(v)==4 for v in row['attack']),row
  assert all(0<=v[0]<row['frameCount'] for v in row['attack']),row
  assert len(row['events'])==hits[id] and row['weights']==100,row
  assert all(len(v)==4 for v in row['events']),row
  assert row['originalSource'] is True and row['inLiveRoster'] is False,row
 output=p.evaluate("""async rows=>{
  const prior=JSON.stringify(P);
  const saved=localStorage.getItem('bf_global_offline_demo_v7');
  const values=[];
  for(const row of rows){
    const id=row.id;
    BF_debug.reset();
    const prev=UNIT_BY_ID.get(id-1);
    if(!prev)throw Error('Missing existing 6star source base '+id);
    const temp={...prev,id,rarity:7,name:'TEMP Original 7star #'+id,
      stats:{...row.base},frameCount:row.frameCount,
      animation:{...prev.animation,atk:row.attack}};
    if(UNIT_BY_ID.has(id)||BF_ARCHIVE_NORMAL_HITS[String(id)])
      throw Error('Expected source 7star to be absent from gameplay '+id);
    UNIT_BY_ID.set(id,temp);
    BF_ARCHIVE_NORMAL_HITS[String(id)]={unitId:id,
      weightsTotal:100,events:row.events};
    const actor=S.party[0];actor.active=true;
    actor.unitId=id;actor.name=temp.name;
    actor.hp=row.base.hp;actor.maxHp=row.base.hp;
    actor.atk=row.base.atk;actor.def=row.base.def;actor.rec=row.base.rec;
    actor.bb=0;actor.action={kind:'attack',target:0};
    S.enemies=[{slot:0,name:'Lab dummy',hp:999999,
      maxHp:999999,atk:10,def:0,element:'Water'}];
    S.mode='archive';S.over=false;S.target=0;
    const hp=S.enemies[0].hp;
    wait=()=>Promise.resolve();
    await performUnit(actor,epoch);
    values.push({id,sourceHits:row.events.length,
      sourceTotal:row.events.reduce((n,e)=>n+e[1],0),
      sourceAtkCGSSteps:row.attack.length,
      simulatedDamage:hp-S.enemies[0].hp,
      demoBBGauge:actor.bb,version:P.version});
    // Reset transient battle before unregistering its 7-star sprite data.
    BF_debug.reset();
    await new Promise(resolve => requestAnimationFrame(resolve));
    UNIT_BY_ID.delete(id);
    delete BF_ARCHIVE_NORMAL_HITS[String(id)];
  }
  return {values,
    productionForms:UNIT_BY_ID.size,
    sourceIDsUnregistered:rows.every(r=>!UNIT_BY_ID.has(r.id)),
    pUnchanged:JSON.stringify(P)===prior,
    saveUnchanged:localStorage.getItem('bf_global_offline_demo_v7')===saved};
 }""",[{**{'id':m['id'],'base':stats[m['id']],'frameCount':m['frameCount'],
              'attack':m['attack'],'events':m['events']}} for m in overview])
 assert len(output['values'])==6,output
 for o in output['values']:
  assert o['simulatedDamage']>0 and o['demoBBGauge']>=0,o
  assert o['sourceHits']==hits[o['id']] and o['sourceTotal']==100,o
  assert o['sourceAtkCGSSteps']>=1 and o['version']==7,o
 assert output['productionForms']==72 and output['sourceIDsUnregistered'],output
 assert output['pUnchanged'] and output['saveUnchanged'],output
 assert not errors,errors
 b.close()
print('PASS v148: six exact original 2022 7star normal hit/CGS profiles run ephemeral DEMO attacks (43 source hits), zero roster/save changes')
