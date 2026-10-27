/* BF_GLOBAL_ORIGINAL_LEADER_ENGLISH_V11400 */
(() => {
 'use strict';
 // Original Global English names and descriptions recovered from 2022
 // BF1_sgtext source. Localization only: no new active leader mechanics.
 const prior=window.BFGlobalPlayableLeadersV11200;
 if(window.BFGlobalOriginalLeaderEnglishV11400||
    !prior||typeof prior.lookup!=='function'||
    typeof P==='undefined'||P.version!==7)return;
 const host=document.getElementById('bf11200-playable-leaders');
 const select=document.getElementById('bf11200-form');
 if(!host||!select||select.options.length!==72)return;
 const freeze=Object.freeze;
 const originalRows=[[100,"Fire Spirit's Power","25% boost to Atk Power of Fire Types"],[101,"Fire God's Power","50% boost to Atk Power of Fire Types"],[102,"Fire Creator's Power","50% boost to Atk power and 10% increase in HP of Fire types"],[110,"Water Spirit's Power","25% boost to Atk Power of Water Types"],[111,"Water God's Power","50% boost to Atk Power of Water Types"],[112,"Water Creator's Power","50% boost to Atk power and 10% increase in HP of Water types"],[120,"Earth Spirit's Power","25% boost to Atk Power of Earth Types"],[121,"Earth God's Power","50% boost to Atk Power of Earth Types"],[122,"Earth Creator's Power","50% boost to Atk power and 10% increase in HP of Earth types"],[130,"Thunder Spirit's Power","25% boost to Atk Power of Thunder Types"],[131,"Thunder God's Power","50% boost to Atk Power of Thunder Types"],[132,"Thunder Creator's Power","50% boost to Atk power and 10% increase in HP of Thunder types"],[140,"Light Spirit's Power","25% boost to Atk Power of Light Types"],[141,"Light God's Power","50% boost to Atk Power of Light Types"],[142,"Light Creator's Power","50% boost to Atk power and 10% increase in HP of Light types"],[150,"Dark Spirit's Power","25% boost to Atk Power of Dark Types"],[151,"Dark God's Power","50% boost to Atk Power of Dark Types"],[152,"Dark Creator's Power","50% boost to Atk power and 10% increase in HP of Dark types"],[500,"Fire's Protection","10% reduction in damage from Fire Types"],[502,"Water's Protection","10% reduction in damage from Water Types"],[504,"Earth's Protection","10% reduction in damage from Earth Types"],[506,"Thunder's Protection","10% reduction in damage from Thunder Types"],[508,"Light's Protection","10% reduction in damage from Light Types"],[510,"Dark Protection","10% reduction in damage from Dark Types"],[1300,"Intense Light","Small boost in damage dealt during Spark"],[1301,"Intense Flash","Boost in damage dealt during Spark"],[1302,"Intense Strobe","Large boost in damage dealt during Spark"],[1303,"Blinding Light","Huge boost in damage dealt during Spark"],[1313,"Intense Edge","Huge boost to damage produced during Spark & slight boost to critical hit damage"],[1314,"Ruin God's Epidemic","Huge boost to damage produced during Spark & adds chance of ignoring an opponent's Def when attacking"],[1400,"Fighting Light","Small boost in Battle Crystals produced during Spark"],[1401,"Fighting Flash","Boost in Battle Crystals produced during Spark"],[1402,"Fighting Strobe","Large boost in Battle Crystals produced during Spark"],[1410,"Combat Magic","Small reduction in BB gauge required for BB & large boost to drop rate of BC produced during Spark"],[1411,"Combat Ambition","Small reduction in BB gauge amount consumed during BB & large boost to drop rate of BC produced during Spark"],[1412,"Combat Wave","Small boost in the BB gauge fill rate & large boost to drop rate of BC produced during Spark"]];
 const byLeader=new Map();
 for(const row of originalRows){
   if(!Array.isArray(row)||row.length!==3||
      !Number.isSafeInteger(row[0])||row[0]<1||
      typeof row[1]!=='string'||row[1].length<2||
      typeof row[2]!=='string'||row[2].length<5||
      byLeader.has(row[0]))return;
   byLeader.set(row[0],freeze({
     lsId:row[0],originalEnglishName:row[1],
     originalEnglishDescription:row[2],gameplayActivated:false}));
 }
 if(byLeader.size!==36||
    byLeader.get(500)?.originalEnglishDescription!==
      '10% reduction in damage from Fire Types'||
    byLeader.get(1300)?.originalEnglishDescription!==
      'Small boost in damage dealt during Spark'||
    byLeader.get(1410)?.originalEnglishDescription!==
      'Small reduction in BB gauge required for BB & large boost to drop rate of BC produced during Spark')return;
 const block=document.createElement('div');
 block.id='bf11400-original-leader-english';
 block.style.cssText='padding:9px;margin:7px 0;border:1px solid #a4acaa;'+
   'border-radius:7px;background:#1b3137;color:#ecf4ee;'+
   'font:12px/1.55 system-ui,sans-serif';
 const name=document.createElement('strong');
 name.id='bf11400-original-name';
 const description=document.createElement('p');
 description.id='bf11400-original-description';
 const caveat=document.createElement('small');
 caveat.textContent='Original 2022 Global English localization. '+
   'Type2 starter leader stat effects are source-gated in v111/v113. '+
   'Type31 Spark damage/BC production and type5 elemental mitigation '+
   'are NOT implemented for synthetic enemy fights. Exact native '+
   'timing, stack order and enemy elements remain unverified.';
 block.append(name,description,caveat);
 document.getElementById('bf11200-raw')?.after(block);
 function lookup(lsId){return Number.isSafeInteger(lsId)?
   byLeader.get(lsId)||null:null;}
 function forUnit(unitId){
   const unit=prior.lookup(unitId);
   if(!unit)return null;
   const skill=lookup(unit.lsId);
   return skill?freeze({unitId,lsId:unit.lsId,
     name:skill.originalEnglishName,
     description:skill.originalEnglishDescription,
     skillTypeRaw:unit.skillTypeRaw,
     originalEnglish:true,combatImplemented:unit.skillTypeRaw==='2'}):null;
 }
 function refresh(){
   const row=forUnit(Number(select.value));
   name.textContent=row?row.name+' · Original Global LS #'+row.lsId:
     'Original English leader skill unavailable';
   description.textContent=row?row.description:
     'No source-verified 2022 English description for this ID.';
   return row;
 }
 // Make the original English leader names visible in the 72-form selector.
 for(const option of select.options){
   const skill=forUnit(Number(option.value));
   if(skill)option.textContent=option.textContent+
     ' · '+skill.name;
 }
 select.addEventListener('change',refresh);
 refresh();
 window.BFGlobalOriginalLeaderEnglishV11400=freeze({
   source:freeze({archive:'BF1_sgtext_part001.zip',
     sha256:'4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285',
     names:36,forms:72,originalEnglish:true,
     combatChanges:false,savedFieldsAdded:0}),
   lookup,forUnit,refresh,snapshot:()=>freeze({
     selected:forUnit(Number(select.value)),sourceOnly:true,
     sourceForms:72,localizedLeaderIds:36,
     addsCombatEffects:false,saveFieldsAdded:0})
 });
})();
