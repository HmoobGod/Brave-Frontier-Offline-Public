"""v0.40: optional battle BB reference; original names/targets, demo gauge disclosed.

Reads only previously verified original Global source tables, never touches P,
the v7 save, actions, damage, the BB gauge or unit progression. Fail closed.
"""
from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parent
HTML=ROOT/'app/src/main/assets/index.html'
html=HTML.read_text('utf-8')
for marker in ('/* BF_GLOBAL_OTHER_SIX_STAR_V038 */','/* BF_EVOLUTION_ROADMAP_V039 */','/* BF_GLOBAL_BB_TARGETING_V028 */'):
    assert html.count(marker)==1,marker
assert 'bf_global_offline_demo_v7' in html
match=re.search(r'window\.BF_ARCHIVE_BB_HITS=(\{.*?\});',html,re.S)
assert match, 'Expected audited original BB event table'
events=json.loads(match.group(1))
assert len(events)==72, 'Expected 72 original sourced playable BB records'
assert all(int(k)==v['bbId'] for k,v in events.items())
marker='/* BF_BATTLE_BB_GUIDE_V040 */'
snippet=r"""
<style id="bf040-bb-guide-style">
#bf040-bb-guide { box-sizing:border-box; grid-column:1/-1; flex-basis:100%;
 width:100%; max-width:100%; margin:5px 0 9px; padding:6px 9px;
 border:1px solid #8a7349; border-radius:6px; background:#211e1a; color:#f7e7bd;
 font-size:12px; line-height:1.35 }
#bf040-bb-guide summary { cursor:pointer; font-weight:750; color:#ffd68d }
#bf040-bb-guide .bf040-body { padding-top:6px }
#bf040-bb-guide p { margin:4px 0 7px }
</style>
<script>
/* BF_BATTLE_BB_GUIDE_V040 */
(() => {
  'use strict';
  // Reference-only UX: current gameplay math and BC/BB charging are still DEMO.
  const id='bf040-bb-guide';
  let queued=false;
  const scopeName={all_enemies:'All enemies',single_enemy:'Single enemy',support:'Allies / support'};
  function infoFor(unitId) {
    const idNum=Number(unitId);
    if(!Number.isSafeInteger(idNum) || idNum<=0 ||
       typeof UNIT_BY_ID==='undefined' || !UNIT_BY_ID.has(idNum) ||
       typeof bfOriginalBB!=='function')return null;
    const skill=bfOriginalBB(idNum);
    const hit=window.BF_ARCHIVE_BB_HITS && window.BF_ARCHIVE_BB_HITS[String(idNum)];
    if(!skill || !hit || Number(hit.bbId)!==idNum ||
       !Object.hasOwn(scopeName,skill.target))return null;
    const power=typeof bfOriginalBBPower==='function'?bfOriginalBBPower(idNum):null;
    const support=typeof originalSupport==='function'?originalSupport(idNum):null;
    return {unitId:idNum,unit:UNIT_BY_ID.get(idNum).name,name:skill.name,
      target:skill.target,scope:scopeName[skill.target],
      lv1Power:power?power.base:null,
      support:support?{kind:support.kind,pct:support.pct??null,
        rounds:support.rounds??null,low:support.low??null,high:support.high??null}:null};
  }
  function activeInfo() {
    if(typeof S==='undefined' || !Array.isArray(S.party))return null;
    const index=Number(S.selected);
    const p=Number.isSafeInteger(index)?S.party[index]:null;
    return p && p.active!==false?infoFor(p.unitId):null;
  }
  function renderLines(info) {
    if(!info)return ['No verified playable unit selected.'];
    const out=[info.unit+' — '+info.name,'Original Global BB target: '+info.scope+'.'];
    if(info.lv1Power!==null)
      out.push('Source BB Lv1 modifier: +'+info.lv1Power+'% (applied inside DEMO damage formula).');
    else if(info.support && info.support.kind==='atk_buff_all' && Number.isFinite(info.support.pct))
      out.push('Source Lv1 ATK boost: +'+info.support.pct+'% / '+info.support.rounds+' turns; DEMO stacking.');
    else if(info.support && info.support.kind==='heal_all')
      out.push('Source Lv1 heal base range: '+info.support.low+'–'+info.support.high+' HP; REC formula not decoded.');
    else out.push('Original native BB effect formula is not decoded; combat uses a DEMO fallback.');
    out.push('BB charging (+34 per normal attack), damage and Brave Crystal drops are DEMO, not verified Global rules.');
    return out;
  }
  function refresh() {
    const root=document.getElementById(id);
    if(!root || !root.open)return;
    const body=root.querySelector('.bf040-body');
    if(!body)return;
    const lines=renderLines(activeInfo());
    const key=JSON.stringify(lines);
    if(body.dataset.key===key)return;
    body.dataset.key=key;
    body.replaceChildren(...lines.map(line=>{
      const p=document.createElement('p');p.textContent=line;return p;
    }));
  }
  function mount() {
    const burst=document.querySelector('#burst');
    if(!burst || !burst.parentElement)return;
    let root=document.getElementById(id);
    if(root && root.previousElementSibling===burst)return;
    if(root)root.remove();
    root=document.createElement('details');root.id=id;
    const summary=document.createElement('summary');
    summary.textContent='BB SOURCE INFO · OPTIONAL';
    root.append(summary);
    const body=document.createElement('div');body.className='bf040-body';
    root.append(body);
    root.addEventListener('toggle',refresh);
    burst.insertAdjacentElement('afterend',root);
  }
  function schedule() {
    if(queued)return;
    queued=true;
    queueMicrotask(()=>{queued=false;mount();refresh();});
  }
  function initialize() {
    mount();
    document.body.addEventListener('click',schedule,true);
    document.body.addEventListener('change',schedule,true);
    const observer=new MutationObserver(schedule);
    observer.observe(document.body,{childList:true,subtree:true});
  }
  if(document.readyState==='loading')
    document.addEventListener('DOMContentLoaded',initialize,{once:true});
  else initialize();
  window.BFGlobalBBGuideV040=Object.freeze({infoFor,refresh});
})();
</script>
"""
if html.count(marker)==1:
    assert html.count('id="bf040-bb-guide-style"')==1
    print('PASS v0.40 existing optional guide already staged')
else:
    assert marker not in html and html.count('</body>')==1
    HTML.write_text(html.replace('</body>',snippet+'\n</body>',1),'utf-8')
    print('PASS v0.40 battle BB reference injected; 72 source skills, save v7 unchanged')
