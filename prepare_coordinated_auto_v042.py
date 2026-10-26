"""v0.42: coordinate source-audited support BBs in optional demo Auto Battle.

Original Global BB targets and buff strengths are read from audited v0.29/v0.38
records; targeting policy itself is clearly optional DEMO. Legacy Auto Battle
unchanged when Smart Support is OFF. Save v7 / assets / damage unchanged.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
HTML=ROOT/'app/src/main/assets/index.html'
s=HTML.read_text('utf-8')
assert s.count('/* BF_SOURCE_AWARE_AUTO_V041 */')==1
assert s.count('/* BF_BATTLE_BB_GUIDE_V040 */')==1
assert s.count('/* BF_GLOBAL_OTHER_SIX_STAR_V038 */')==1
assert 'bf_global_offline_demo_v7' in s
support=json.loads((ROOT/'source_data/bf_global_original_bb_support_v029.json').read_text('utf8'))
assert support['skills']['40021']['level1DemoEffect']=={'type':'atk_buff_all','pctAtLv1':30,'roundsAtLv1':3}
other=json.loads((ROOT/'source_data/bf_global_other_six_star_v038.json').read_text('utf8'))
assert other['records']['40025']['bb']['target']=='support'
assert other['records']['40025']['bb']['levels'][0]['params']==[0,94,0,0,0,3,170]

MARK='/* BF_COORDINATED_AUTO_V042 */'
old="const target=livingEnemies().sort((a,b)=>a.hp-b.hp)[0];if(!target)return;for(const p of liveParty()){p.action={kind:window.BF041SmartAuto?.kindFor(p) ?? (p.bb>=100?'burst':'attack'),target:target.slot}}update();execute()"
new="const target=window.BF042AutoCoordination?.chooseTarget(livingEnemies()) ?? livingEnemies().sort((a,b)=>a.hp-b.hp)[0];if(!target)return;const plan=window.BF042AutoCoordination?.plan(liveParty());for(const p of liveParty()){p.action={kind:plan?.get(p) ?? (window.BF041SmartAuto?.kindFor(p) ?? (p.bb>=100?'burst':'attack')),target:target.slot}}if(window.BF041SmartAuto?.enabled())S.target=target.slot;update();execute()"
JS=r"""
<script>
/* BF_COORDINATED_AUTO_V042 */
(() => {
  'use strict';
  // Optional DEMO QoL; original Global targeting AI is NOT decoded.
  // Backed by original Global target-area and Lv1 support record audit.
  const enabled=()=>window.BF041SmartAuto?.enabled()===true;
  function chooseTarget(enemies) {
    if(!enabled() || !Array.isArray(enemies))return null;
    const valid=enemies.filter(e=>e && Number.isFinite(e.hp) && e.hp>0 &&
      Number.isFinite(e.maxHp) && e.maxHp>0 && Number.isSafeInteger(e.slot));
    valid.sort((a,b)=>a.hp/a.maxHp-b.hp/b.maxHp || a.hp-b.hp || a.slot-b.slot);
    return valid[0]||null;
  }
  function plan(party) {
    if(!enabled() || !Array.isArray(party))return null;
    const actions=new Map();
    const buffs=[];
    for(const p of party){
      if(!p || !p.active || !(p.hp>0))continue;
      const kind=window.BF041SmartAuto.kindFor(p);
      actions.set(p,kind);
      if(kind!=='burst' || typeof bfOriginalBB!=='function' ||
         typeof originalSupport!=='function')continue;
      if(bfOriginalBB(p.unitId)?.target!=='support')continue;
      const source=originalSupport(p.unitId);
      if(source?.kind!=='atk_buff_all' || !Number.isFinite(source.pct))continue;
      buffs.push({p,pct:source.pct});
    }
    // Do not spend several BBs on overlapping party-wide ATK buffs.
    // Retain strongest source-recorded Lv1 buff; tie -> earlier squad slot.
    buffs.sort((a,b)=>b.pct-a.pct || a.p.id-b.p.id);
    for(const entry of buffs.slice(1))actions.set(entry.p,'attack');
    return actions;
  }
  window.BF042AutoCoordination=Object.freeze({chooseTarget,plan,enabled});
  function describe() {
    const label=document.getElementById('bf041-smart-auto-label');
    if(label && !label.dataset.bf042){
      label.dataset.bf042='1';
      label.title+=' In v0.42: prioritize lowest enemy HP percentage and select one strongest ready ATK buff per round.';
    }
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',describe,{once:true});
  else describe();
})();
</script>
"""
if MARK in s:
    assert s.count(MARK)==1 and s.count(new)==1 and s.count(old)==0
    assert s.count('window.BF041SmartAuto?.kindFor(p)')==1
    print('PASS existing v0.42 coordinated source-aware Auto Battle patch unchanged')
else:
    assert s.count(old)==1,('Auto queue site missing or duplicated',s.count(old))
    assert s.count('</body>')==1
    s=s.replace(old,new,1).replace('</body>',JS+'\n</body>',1)
    assert s.count(MARK)==1 and s.count(new)==1
    HTML.write_text(s,'utf-8')
    print('PASS v0.42 coordinated source-aware Auto Battle; legacy Auto, v7 unchanged')
