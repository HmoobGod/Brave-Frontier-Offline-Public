/* BF_GLOBAL_ELEMENTAL_COMBAT_V6900 */
(() => {
 'use strict';
 // Original Global base-element advantage; only use source-identified
 // element strings. Do not assign unverified elements to DEMO monsters.
 if(window.BFGlobalElementalCombatV6900||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const strong=Object.freeze({
  Fire:'Earth',Earth:'Thunder',Thunder:'Water',Water:'Fire',
  Light:'Dark',Dark:'Light'
 });
 const source=Object.freeze({
  elements:Object.freeze(Object.keys(strong)),
  advantage:1.5,disadvantage:.5,
  reference:'https://bravefrontierglobal.fandom.com/wiki/Damage',
  elementReference:'https://bravefrontiereurope.fandom.com/wiki/Gameplay:Elements',
  interpretation:'original elemental relation; remaining native damage formula and rounding remain DEMO',
  missingElement:'No multiplier without both verified base elements'
 });
 function normalize(v){
  if(typeof v!=='string')return null;
  const s=v.trim().toLowerCase();
  return Object.keys(strong).find(k=>k.toLowerCase()===s)||null;
 }
 function multiplier(attacker,defender){
  if(S.mode!=='archive'||S.over)return 1;
  const a=normalize(attacker),b=normalize(defender);
  if(!a||!b)return 1;
  if(strong[a]===b)return 1.5;
  if(strong[b]===a)return .5;
  return 1;
 }
 function scaleDamage(damage,attacker,defender){
  if(!Number.isFinite(damage)||damage<=0)return damage;
  const factor=multiplier(attacker,defender);
  return factor===1?damage:Math.max(1,Math.round(damage*factor));
 }
 function snapshot(){
  return Object.freeze({mode:S.mode,round:S.round,source,
    knownEnemyElements:Object.freeze((S.enemies||[]).filter(x=>
      x?.hp>0&&normalize(x.element)).map(x=>Object.freeze({
      slot:x.slot,element:normalize(x.element)})))});
 }
 window.BFGlobalElementalCombatV6900=Object.freeze({
  source,normalize,multiplier,scaleDamage,snapshot
 });
})();
