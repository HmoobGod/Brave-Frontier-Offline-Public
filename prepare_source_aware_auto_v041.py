"""v0.41 optional source-aware Auto Battle QoL; OFF by default, DEMO thresholds.

Uses only already audited original Global heal / ally ATK support BB types.
The decision threshold/AI is NOT claimed native. Keep combat and v7 saves.
Fail closed against changes to v0.40 source anchors.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
HTML=A/'index.html'
s=HTML.read_text('utf-8')
assert 'bf_global_offline_demo_v7' in s
for oldmark in ('/* BF_GLOBAL_BB_SUPPORT_V029 */','/* BF_GLOBAL_OTHER_SIX_STAR_V038 */',
                '/* BF_EVOLUTION_ROADMAP_V039 */','/* BF_BATTLE_BB_GUIDE_V040 */'):
    assert s.count(oldmark)==1,oldmark
support=json.loads((ROOT/'source_data/bf_global_original_bb_support_v029.json').read_text('utf-8'))
assert support['schema']=='bf-global-original-bb-support-v029'
assert support['skills']['20041']['level1DemoEffect']['type']=='heal_all'
assert support['skills']['40021']['level1DemoEffect']['type']=='atk_buff_all'
other=json.loads((ROOT/'source_data/bf_global_other_six_star_v038.json').read_text('utf-8'))
assert other['records']['40025']['bb']['levels'][0]['params']==[0,94,0,0,0,3,170]
marker='/* BF_SOURCE_AWARE_AUTO_V041 */'
prior="p.action={kind:p.bb>=100?'burst':'attack',target:target.slot}"
next="p.action={kind:window.BF041SmartAuto?.kindFor(p) ?? (p.bb>=100?'burst':'attack'),target:target.slot}"
ui=r"""
<style id="bf041-smart-auto-style">
#bf041-smart-auto-label { display:inline-flex; align-items:center; flex-wrap:wrap;
 gap:5px; padding:3px 6px; border:1px solid #7e6940; border-radius:5px;
 color:#eed8ac; font-size:12px }
#bf041-smart-auto-label input { width:16px; height:16px; margin:0 }
</style>
<script>
/* BF_SOURCE_AWARE_AUTO_V041 */
(() => {
  'use strict';
  // Disabled by default. The 60% heal trigger and decision policy are DEMO QoL.
  // Original 2022 skill class/targets and Lv1 source values are separately audited.
  const toggleId='bf041-smart-auto';
  const enabled=()=>document.getElementById(toggleId)?.checked===true;
  function kindFor(p) {
    const fallback=p && Number(p.bb)>=100?'burst':'attack';
    if(!enabled() || !p || !p.active || p.hp<=0 || fallback==='attack')return fallback;
    const unitId=Number(p.unitId);
    if(!Number.isSafeInteger(unitId) || !UNIT_BY_ID.has(unitId) ||
       typeof originalSupport!=='function' ||
       typeof bfOriginalBB!=='function')return fallback;
    const scope=bfOriginalBB(unitId);
    const support=originalSupport(unitId);
    if(scope?.target!=='support' || !support)return fallback;
    if(support.kind==='heal_all'){
      // DEMO heuristic: do not spend healing BB unless a living ally is <=60% HP.
      return liveParty().some(a=>a.maxHp>0 && a.hp<a.maxHp &&
          a.hp/a.maxHp<=0.60)?'burst':'attack';
    }
    if(support.kind==='atk_buff_all' && Number.isFinite(support.pct)){
      // DEMO heuristic: source ATK buff worth casting if any ally lacks its strength.
      return liveParty().some(a=>currentAtkBoost(a)<support.pct)?'burst':'attack';
    }
    return fallback;
  }
  function mount() {
    const old=document.getElementById(toggleId);
    if(old)return;
    const auto=document.getElementById('auto');
    if(!auto || !auto.parentElement || !auto.parentElement.parentElement)return;
    const label=document.createElement('label');
    label.id='bf041-smart-auto-label';
    const check=document.createElement('input');
    check.type='checkbox';check.id=toggleId;
    check.setAttribute('aria-label','Enable source-aware DEMO Auto Battle');
    const copy=document.createElement('span');
    copy.textContent='Smart support · DEMO (optional)';
    label.title='Source-verified healing/ATK buff BB categories; DEMO 60% heal trigger. Off by default. Not saved.';
    label.append(check,copy);
    auto.parentElement.insertAdjacentElement('afterend',label);
  }
  if(document.readyState==='loading')
    document.addEventListener('DOMContentLoaded',mount,{once:true});
  else mount();
  window.BF041SmartAuto=Object.freeze({kindFor,enabled});
})();
</script>
"""
if s.count(marker)==1:
    # v0.42 replaces only the Auto queue site after v0.41 has been installed.
    # Validate either exact v0.41 site or the strictly checked v0.42 successor.
    upgraded = (s.count('/* BF_COORDINATED_AUTO_V042 */')==1 and
                s.count('window.BF041SmartAuto?.kindFor(p)')==1 and
                s.count('window.BF042AutoCoordination?.plan(liveParty())')==1)
    assert (s.count(next)==1 or upgraded) and s.count('id="bf041-smart-auto-style"')==1
    assert s.count(prior)==0
    print('PASS v0.41 idempotent source-aware Auto Battle patch intact')
else:
    assert s.count(marker)==0
    assert s.count(prior)==1,('Unexpected auto-battle anchor',s.count(prior))
    assert s.count('</body>')==1
    s=s.replace(prior,next,1).replace('</body>',ui+'\n</body>',1)
    assert s.count(marker)==1 and s.count(next)==1
    HTML.write_text(s,'utf-8')
    print('PASS v0.41 optional source-aware Auto Battle; default original DEMO actions and v7 save unchanged')
