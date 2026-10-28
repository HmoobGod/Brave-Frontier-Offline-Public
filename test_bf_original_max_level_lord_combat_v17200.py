"""v172: verify 2022 Lord max-level stat endpoints applied to new battle party."""
import json,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
rows={x['unitId']:x for x in json.loads((R/'source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json').read_text('utf8'))['rows']}
assert len(rows)==72
script=(A/'bf17200_original_max_level_lord_combat.js').read_text('utf8')
bridge=(A/'bf11100_original_starter_leader_combat.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert script.count('BF_GLOBAL_ORIGINAL_MAX_LEVEL_LORD_COMBAT_V17200')==1
assert len(script.encode())<65536
assert 'BFGlobalOriginalMaxLevelLordV17200?.apply?.(unit,i)' in bridge
assert bridge.index('BFGlobalOriginalUnitLevelCapsV11500?.apply?.(unit,i)')<bridge.index(
 'BFGlobalOriginalLevelOneLordV16800?.apply?.(unit,i)')<bridge.index(
 'BFGlobalOriginalMaxLevelLordV17200?.apply?.(unit,i)')<bridge.index(
 'BFGlobalOptionalImpsV16900?.apply?.(unit,i)')<bridge.index('return apply(unit,i);')
assert java.index('readPackagedText("bf11600_original_lord_stats_reference.js")')<java.index(
 'readPackagedText("bf16800_original_level_one_lord_combat.js")')<java.index(
 'readPackagedText("bf17200_original_max_level_lord_combat.js")')<java.index(
 'readPackagedText("bf16900_optional_imp_fusion.js")')
for denied in ('localStorage','saveProgress(', 'P.unitExp=', 'P.roster=', 'P.squad=', 'Math.random','fetch(', 'XMLHttpRequest','awardDemoRewards('):
 assert denied not in script,denied
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
    removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
    get length(){return Object.keys(db).length}
   }});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 for name in ('bf11000_source_starter_leader_skills.js',
 'bf11100_original_starter_leader_combat.js',
 'bf11200_all_playable_leader_source.js',
 'bf11500_original_unit_level_caps.js',
 'bf11600_original_lord_stats_data.js',
 'bf11600_original_lord_stats_reference.js',
 'bf16800_original_level_one_lord_combat.js',
 'bf17200_original_max_level_lord_combat.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('BFGlobalOriginalMaxLevelLordV17200.source.qualifiedForms')==72
 assert p.locator('#bf17200-original-max-lord').count()==1
 for id,r in rows.items():
  endpoint=p.evaluate(f'BFGlobalOriginalLordStatsV11600.endpoint({id},{r["maxLevel"]})')
  assert endpoint and endpoint['exactOriginalLordEndpoint'] is True
  assert endpoint['stats']==r['lordAtMax'],(id,endpoint,r)
  assert p.evaluate(f'BFGlobalOriginalUnitLevelCapsV11500.lookup({id})')==r['maxLevel']
 # Reached via existing DEMO EXP thresholds; never fabricate a native curve.
 for id in (10011,20011,50011,10021,20021,10041,60041):
  cap=rows[id]['maxLevel']
  a=p.evaluate("""({id,cap})=>{
   let exp=1;
   while(demoLevel(exp)<cap && exp<1000000000000)exp*=2;
   if(demoLevel(exp)<cap)throw Error('DEMO EXP does not reach cap');
   document.getElementById('mode').value='archive';
   if(!P.roster.includes(id))P.roster.push(id);
   P.squad=[id];P.unitExp[id]=exp;reset();
   return {unit:S.party[0],exp,level:demoLevel(exp),
    bonus:BFGlobalStarterLeaderCombatV11100.fromSource(id,id)};
  }""",{'id':id,'cap':cap})
  unit=a['unit']
  assert unit['unitId']==id and unit['level']==cap,(id,unit,cap)
  ref=rows[id]['lordAtMax']
  bonus=a['bonus'] or {'atkPercent':0,'hpPercent':0}
  assert unit['maxHp']==unit['hp']==ref['hp']*(100+bonus['hpPercent'])//100,(id,unit,ref,bonus)
  assert unit['atk']==ref['atk']*(100+bonus['atkPercent'])//100,(id,unit,ref,bonus)
  assert unit['def']==ref['def'] and unit['rec']==ref['rec'],(id,unit,ref)
  assert p.evaluate('BFGlobalOriginalMaxLevelLordV17200.snapshot().exactLordMaxPartyUnits')==1
  before=p.evaluate('JSON.stringify(S.party[0])')
  p.evaluate('BFGlobalOriginalMaxLevelLordV17200.apply(S.party[0],0)')
  assert p.evaluate('JSON.stringify(S.party[0])')==before
 # Under-level progression stays DEMO, and 2022 level-one stats still work.
 p.evaluate("""()=>{P.squad=[10011];P.unitExp[10011]=123;reset();}""")
 assert p.evaluate('BFGlobalOriginalMaxLevelLordV17200.snapshot().exactLordMaxPartyUnits')==0
 p.evaluate("""()=>{P.unitExp[10011]=0;reset();}""")
 assert p.evaluate('S.party[0].maxHp')==rows[10011]['base']['hp']
 assert p.evaluate('BFGlobalOriginalLevelOneLordV16800.snapshot().originalLevelOnePartyUnits')==1
 assert p.evaluate('BFGlobalOriginalMaxLevelLordV17200.snapshot().exactLordMaxPartyUnits')==0
 p.evaluate("""()=>{document.getElementById('mode').value='training';P.unitExp[10011]=1000000;reset();}""")
 assert p.evaluate('BFGlobalOriginalMaxLevelLordV17200.snapshot().exactLordMaxPartyUnits')==0
 prior=p.evaluate('JSON.stringify(P)')
 p.add_script_tag(path=str(A/'bf17200_original_max_level_lord_combat.js'))
 assert p.locator('#bf17200-original-max-lord').count()==1
 assert p.evaluate('JSON.stringify(P)')==prior
 assert not errors,errors
 b.close()
print('PASS v172: 72 original max Lord endpoint records, qualified owned battle source stats, leader stacking, Lv1/training fail closed and v7 save isolation')
