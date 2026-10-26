/* BF_GLOBAL_ORIGINAL_ATK_BB_LEVELS_V7100 */
(() => {
 'use strict';
 // 2022 F_SKILL_LEVEL_MST_1_Ver1487 original ten-level party-ATK BB data.
 // Reuse the optional battle-only v68 level preview; never write mastery.
 const levelPreview=window.BFGlobalOriginalHealBBLevelsV6800;
 if(window.BFGlobalOriginalAtkBBLevelsV7100||!levelPreview||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const tables=Object.freeze({
   40021:Object.freeze([30,31,32,33,34,35,36,37,38,40]),
   40022:Object.freeze([40,41,42,43,44,45,46,47,48,50])
 });
 const names=Object.freeze({40021:"Thunder's Command",40022:"Thunder's Rage"});
 const source=Object.freeze({
   archive:'mst-decoded.zip',
   table:'3-mst-translated/F_SKILL_LEVEL_MST_1_Ver1487.json',
   crosscheck:'source_data/bf_global_original_bb_support_v029.json',
   skillIds:Object.freeze([40021,40022]),
   effectCodes:Object.freeze({40021:1300,40022:1600}),
   rounds:3,values:tables,
   note:'Original ATK percentages; level selection is DEMO, not saved BB mastery.'
 });
 function level(){
   const n=levelPreview.snapshot().level;
   return Number.isInteger(n)&&n>=1&&n<=10?n:1;
 }
 function sourceFor(skillId,requestedLevel=level()){
   const values=tables[skillId];
   if(!values||!Number.isInteger(requestedLevel)||requestedLevel<1||requestedLevel>10)return null;
   return Object.freeze({skillId,level:requestedLevel,code:source.effectCodes[skillId],
     pct:values[requestedLevel-1],rounds:3,name:names[skillId]});
 }
 function boostFor(skillId){
   if(S.mode!=='archive'||S.over)return null;
   return sourceFor(skillId)?.pct??null;
 }
 function snapshot(){
   const current=level();
   return Object.freeze({mode:S.mode,round:S.round,level:current,
      boosts:Object.freeze([40021,40022].map(id=>sourceFor(id,current)))});
 }
 const panel=document.getElementById('bf6800-levels');
 const selector=document.getElementById('bf6800-level');
 const note=document.createElement('small');
 note.id='bf7100-atk-preview';
 if(panel)panel.append(note);
 function refresh(){
   const st=snapshot();
   if(note.isConnected)note.textContent=
     'Original Lv.'+st.level+' source support BBs: '+names[40021]+
     ' ATK +'+st.boosts[0].pct+'%, '+names[40022]+
     ' ATK +'+st.boosts[1].pct+
     '%, archived duration 3 turns. Skill level is a DEMO preview, not saved mastery.';
   return st;
 }
 selector?.addEventListener('change',refresh);
 document.getElementById('mode')?.addEventListener('change',refresh);
 document.getElementById('reset')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden&&S.mode==='archive')refresh()},900);
 window.BFGlobalOriginalAtkBBLevelsV7100=Object.freeze({
   source,sourceFor,boostFor,snapshot,refresh
 });
 refresh();
})();
