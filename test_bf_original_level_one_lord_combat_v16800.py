"""v168: exact 2022 Global level-one Lord source stats, no guessed EXP progression."""
import json,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent; A=R/'app/src/main/assets'
manifest=json.loads((R/'source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json').read_text('utf8'))
rows={r['unitId']:r for r in manifest['rows']}
assert len(rows)==72
js=(A/'bf16800_original_level_one_lord_combat.js').read_text('utf8')
bridge=(A/'bf11100_original_starter_leader_combat.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert js.count('BF_GLOBAL_ORIGINAL_LEVEL1_LORD_COMBAT_V16800')==1
assert len(js.encode('utf8'))<65536
assert 'BFGlobalOriginalLevelOneLordV16800?.apply?.(unit,i)' in bridge
assert bridge.index('BFGlobalOriginalUnitLevelCapsV11500?.apply?')<bridge.index('BFGlobalOriginalLevelOneLordV16800?.apply?')<bridge.index('return apply(unit,i);')
assert java.index('readPackagedText("bf11600_original_lord_stats_reference.js")')<java.index('readPackagedText("bf16800_original_level_one_lord_combat.js")')
for denied in ('localStorage','saveProgress(', 'P.unitExp=', 'P.roster=', 'P.squad=', 'Math.random','fetch(','XMLHttpRequest','awardDemoRewards('):
 assert denied not in js,denied
assert all(r['maxLevel']>=1 and all(r['base'][k]>0 for k in ['hp','atk','def','rec']) for r in rows.values())
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda err:errors.append(str(err)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
 get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 p.add_script_tag(path=str(A/'bf11000_source_starter_leader_skills.js'))
 p.add_script_tag(path=str(A/'bf11100_original_starter_leader_combat.js'))
 p.add_script_tag(path=str(A/'bf11500_original_unit_level_caps.js'))
 p.add_script_tag(path=str(A/'bf11600_original_lord_stats_data.js'))
 p.add_script_tag(path=str(A/'bf11600_original_lord_stats_reference.js'))
 p.add_script_tag(path=str(A/'bf16800_original_level_one_lord_combat.js'))
 assert p.evaluate('BFGlobalOriginalLevelOneLordV16800.source.qualifiedForms')==72
 for id,ref in rows.items():
  original=p.evaluate(f'BFGlobalOriginalLordStatsV11600.endpoint({id},1)')
  assert original['stats']==ref['base'],(id,original,ref['base'])
  assert p.evaluate(f'BFGlobalOriginalLevelOneLordV16800.source.levelOneOnly')
 assert p.locator('#bf16800-original-level1-combat').count()==1
 def select(unit,exp=0,mode='archive'):
  p.evaluate("""({unit,exp,mode})=>{
    document.getElementById('mode').value=mode;
    if(!P.roster.includes(unit))P.roster.push(unit);
    P.squad=[unit];P.unitExp[unit]=exp;
    reset();
  }""",{'unit':unit,'exp':exp,'mode':mode})
  return p.evaluate('S.party[0]')
 # The twelve level-1 forms are all available in the original playable set.
 # Source-based ATK leader buffs are applied *after* the exact base endpoint.
 for unit in [10011,20011,30011,40011,50011,60011,
              10021,20021,30021,40021,50021,60021,
              10041,20041,30041,40041,50041,60041]:
  actor=select(unit)
  assert actor['unitId']==unit
  ref=rows[unit]['base']
  assert actor['level']==1
  assert actor['maxHp']==actor['hp']==ref['hp'],(unit,actor,ref)
  assert actor['def']==ref['def'] and actor['rec']==ref['rec'],(unit,actor,ref)
  expected_atk=(ref['atk']*125)//100 if unit%10000==11 else ref['atk']
  assert actor['atk']==expected_atk,(unit,actor,ref)
  assert p.evaluate('BFGlobalOriginalLevelOneLordV16800.snapshot().originalLevelOnePartyUnits')==1
  p.evaluate('BFGlobalOriginalLevelOneLordV16800.apply(S.party[0],0)')
  assert p.evaluate('S.party[0].atk')==expected_atk
 assert p.evaluate('BFGlobalOriginalLevelOneLordV16800.snapshot().saveFieldsAdded')==0
 # Any experience means the intermediate original curve is unverified.
 actor=select(10011,12345)
 assert p.evaluate('BFGlobalOriginalLevelOneLordV16800.snapshot().originalLevelOnePartyUnits')==0
 exp_demo=p.evaluate('(()=>{const src=effectiveUnit(10011);const grow=demoLevel(P.unitExp[10011])-1;return {hp:src.stats.hp+grow*30,atk:src.stats.atk+grow*12}})()')
 assert actor['maxHp']==exp_demo['hp']
 assert actor['atk']==exp_demo['atk']*125//100
 # Training and unknown/non-owned roster forms are untouched.
 select(10011,0,'training')
 assert p.evaluate('BFGlobalOriginalLevelOneLordV16800.snapshot().originalLevelOnePartyUnits')==0
 assert p.evaluate('S.party[0].maxHp')==p.evaluate('effectiveUnit(10011).stats.hp')
 # A valid form in a different squad slot does not qualify for this actor.
 select(10041)
 before=p.evaluate("JSON.stringify(P)")
 state=p.evaluate("JSON.stringify(S.party.map(u=>({hp:u.hp,atk:u.atk,def:u.def,rec:u.rec})))")
 p.add_script_tag(path=str(A/'bf16800_original_level_one_lord_combat.js'))
 assert p.locator('#bf16800-original-level1-combat').count()==1
 assert p.evaluate("JSON.stringify(P)")==before
 assert p.evaluate("JSON.stringify(S.party.map(u=>({hp:u.hp,atk:u.atk,def:u.def,rec:u.rec})))")==state
 assert not errors,errors
 b.close()
print('PASS v168 exact 2022 level-one Lord HP/ATK/DEF/REC, source ATK leader stacking, 72 form audit, fail-closed intermediate XP, training, no save mutation')
