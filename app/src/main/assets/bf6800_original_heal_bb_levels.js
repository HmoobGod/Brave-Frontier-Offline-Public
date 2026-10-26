/* BF_GLOBAL_ORIGINAL_HEAL_BB_LEVELS_V6800 */
(() => {
 'use strict';
 // Source F_SKILL_LEVEL_MST_1_Ver1487 contains ten exact levels of
 // four healing BBs (codes 1500). Selecting a level is a local DEMO
 // comparison, NOT saved BB mastery or original progression.
 if(window.BFGlobalOriginalHealBBLevelsV6800||
    !window.BFGlobalBurstRecipientRecoveryV6700||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const ids=Object.freeze([20041,30041,40041,50041]);
 const levels=Object.freeze(Array.from({length:10},(_,i)=>Object.freeze({
    level:i+1,effectCode:1500,low:600+i*30,high:800+i*30,
    undecoded:Object.freeze([50,50])
 })));
 const source=Object.freeze({
    archive:'mst-decoded.zip',table:'3-mst-translated/F_SKILL_LEVEL_MST_1_Ver1487.json',
    crosscheck:'source_data/bf_global_original_bb_support_v029.json',
    skillIds:ids,levels,
    note:'Exactly archived base ranges. Level selection and REC rounding are DEMO. Healer coefficient remains unknown.'
 });
 const parent=document.getElementById('battle');
 const mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const css=document.createElement('style');css.id='bf6800-style';
 css.textContent='#bf6800-levels{margin:8px 11px;padding:9px;border:1px solid #baa46f;border-radius:6px;background:#263344;color:#f5e6c7;font:12px/1.45 system-ui,sans-serif}'+
    '#bf6800-levels[hidden]{display:none!important}#bf6800-levels label{display:block;font-weight:700}'+
    '#bf6800-levels select{display:block;width:100%;min-height:42px;margin:4px 0 6px;padding:6px;background:#1e354a;color:white;border:1px solid #a8b8c8;border-radius:5px}'+
    '#bf6800-levels small{display:block;color:#d7dfed}';
 document.head.append(css);
 const panel=document.createElement('section');panel.id='bf6800-levels';
 panel.setAttribute('aria-label','Archived healing Brave Burst level preview');
 const heading=document.createElement('strong');
 heading.textContent='ARCHIVED HEALING BB · LEVEL PREVIEW';
 const label=document.createElement('label');label.textContent='Original recorded base-heal level';
 const pick=document.createElement('select');pick.id='bf6800-level';
 pick.setAttribute('aria-label','Preview healing Brave Burst level one through ten');
 for(const item of levels){
    const option=document.createElement('option');option.value=String(item.level);
    option.textContent='Lv.'+item.level+' · '+item.low+'–'+item.high+' base HP';
    pick.append(option);
 }
 label.append(pick);
 const info=document.createElement('small');info.id='bf6800-note';
 panel.append(heading,label,info);
 parent.append(panel);
 let battle=S,level=1;
 function sync(){
    if(battle!==S){
      battle=S;level=1;pick.value='1';
    }
 }
 function sourceFor(skillId,requestedLevel=level){
    if(!ids.includes(skillId)||!Number.isInteger(requestedLevel)||
       requestedLevel<1||requestedLevel>10)return null;
    return levels[requestedLevel-1];
 }
 function snapshot(){
    sync();
    return Object.freeze({level,mode:S.mode,
      range:levels[level-1],skillIds:ids,
      available:S.mode==='archive'&&!S.over});
 }
 function refresh(){
    const state=snapshot();
    panel.hidden=S.mode!=='archive';
    pick.disabled=S.mode!=='archive'||S.busy||S.over;
    if(pick.value!==String(level))pick.value=String(level);
    info.textContent='Source skill IDs '+ids.join(', ')+
      ' · 2022 Lv.'+level+' range '+state.range.low+'–'+state.range.high+
      '. Preview only: no permanent BB leveling, item drops or save changes.';
    return state;
 }
 function selectLevel(next){
    sync();
    if(S.mode!=='archive'||S.busy||S.over||
       !Number.isInteger(next)||next<1||next>10)return false;
    level=next;refresh();return true;
 }
 function baseHeal(base){
    sync();
    if(!Number.isFinite(base)||base<0||S.mode!=='archive'||S.over)return base;
    // All four archived heal BBs share the same +30 low/high step at each
    // level; v67 passes only their already-selected Lv1 base.
    return Math.round(base)+30*(level-1);
 }
 pick.addEventListener('change',()=>{if(!selectLevel(Number(pick.value)))refresh();});
 mode.addEventListener('change',refresh);
 document.getElementById('reset')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden&&S.mode==='archive')refresh()},1000);
 window.BFGlobalOriginalHealBBLevelsV6800=Object.freeze({
    source,snapshot,sourceFor,selectLevel,baseHeal,refresh
 });
 refresh();
})();
