/* BF_GLOBAL_SOURCE_ALL_PLAYABLE_LEADER_RECIPIENTS_V11300 */
(() => {
 'use strict';
 // v111 correctly knows the original type2 leader percentages but applies
 // them only to 30 initial starter forms. 2022 F_UNIT identifies the
 // elements of 42 additional PLAYABLE forms. Those are legitimate targets
 // of the leader's matching-element skill, whatever their own leader skill.
 const starter=window.BFGlobalStarterLeaderSourceV11000;
 const playable=window.BFGlobalPlayableLeadersV11200;
 const combat=window.BFGlobalStarterLeaderCombatV11100;
 const original=window.playerUnit;
 if(window.BFGlobalAllLeaderRecipientsV11300||
    !starter||!playable||!combat||
    typeof starter.lookup!=='function'||
    typeof playable.lookup!=='function'||
    typeof original!=='function'||
    !String(original).includes('return apply(unit,i)')||
    typeof P==='undefined'||P.version!==7||
    typeof S==='undefined'||!Array.isArray(P.roster)||
    !Array.isArray(P.squad)||
    typeof effectiveUnit!=='function')return;
 const mode=document.getElementById('mode');
 const host=document.getElementById('bf11100-leader-combat')||
   document.getElementById('squadpicker');
 if(!mode||!host)return;
 const freeze=Object.freeze,applied=new WeakMap();
 let count=0,rejected=0;
 function eligibility(leaderBase,targetFormId){
   if(!Number.isSafeInteger(leaderBase)||!P.roster.includes(leaderBase)||
      !Number.isSafeInteger(targetFormId))return null;
   const leaderForm=effectiveUnit(leaderBase);
   if(!Number.isSafeInteger(leaderForm?.id))return null;
   const leader=starter.lookup(leaderForm.id);
   const recipient=playable.lookup(targetFormId);
   // Important: this is RECIPIENT-ONLY expansion. Never activate the
   // recipient's own raw type31/5/compound leader skills.
   if(!leader||!recipient||recipient.skillTypeRaw==='2'||
      recipient.unimplementedRaw!==true||
      !Number.isSafeInteger(recipient.element)||recipient.element<1||
      recipient.element>6||leader.element!==recipient.element||
      !Number.isSafeInteger(leader.atkPercent)||leader.atkPercent<0||
      leader.atkPercent>50||!Number.isSafeInteger(leader.hpPercent)||
      leader.hpPercent<0||leader.hpPercent>10)return null;
   return freeze({leaderId:leaderForm.id,targetId:recipient.unitId,
      element:recipient.element,atkPercent:leader.atkPercent,
      hpPercent:leader.hpPercent,sourceQualified:true,
      recipientLeaderSkillActivated:false});
 }
 function apply(unit,slot){
   if(!unit||typeof unit!=='object'||applied.has(unit)||
      mode.value!=='archive'||!unit.active||
      !Number.isSafeInteger(slot)||slot<0||slot>=6||
      !Number.isSafeInteger(unit.unitId)||
      P.squad[slot]!==unit.baseId||!P.roster.includes(unit.baseId)||
      !Number.isSafeInteger(unit.atk)||unit.atk<1||
      !Number.isSafeInteger(unit.maxHp)||unit.maxHp<1||
      unit.hp!==unit.maxHp){rejected++;return unit;}
   const bonus=eligibility(P.squad[0],unit.unitId);
   if(!bonus||(!bonus.atkPercent&&!bonus.hpPercent)){
     rejected++;return unit;
   }
   const baseAtk=unit.atk,baseHp=unit.maxHp;
   // Same DEMO integer floor policy as v111 (not native stat ordering).
   const newAtk=Math.floor(baseAtk*(100+bonus.atkPercent)/100);
   const newHp=Math.floor(baseHp*(100+bonus.hpPercent)/100);
   if(!Number.isSafeInteger(newAtk)||newAtk<1||newAtk>1e9||
      !Number.isSafeInteger(newHp)||newHp<1||newHp>1e9){
     rejected++;return unit;
   }
   unit.atk=newAtk;unit.hp=newHp;unit.maxHp=newHp;
   applied.set(unit,freeze({slot,unitId:unit.unitId,
     leaderId:bonus.leaderId,baseAtk,baseHp,newAtk,newHp,
     atkPercent:bonus.atkPercent,hpPercent:bonus.hpPercent,
     recipientOriginalLeaderNotActivated:true}));
   count++;
   return unit;
 }
 window.playerUnit=function(i){
   return apply(original.apply(this,arguments),i);
 };
 const panel=document.createElement('details');
 panel.id='bf11300-leader-recipients';
 panel.style.cssText='margin:8px 2px;padding:9px;border:1px solid #aac1a7;'+
   'border-radius:7px;background:#1c3633;color:#edf6e9;'+
   'font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL LEADER EFFECT · ALL PLAYABLE RECIPIENTS';
 heading.style.cssText='cursor:pointer;min-height:35px;font-weight:800';
 const summary=document.createElement('p');
 summary.id='bf11300-counts';
 const rows=document.createElement('ol');
 rows.id='bf11300-rows';
 const caution=document.createElement('small');
 caution.textContent='2022 type2 starter leader effects now target source-matched '+
   'elemental units among all 72 playable forms; 42 non-starter forms are '+
   'eligible recipients only. Their own raw type31 Spark/type5 mitigation/ '+
   'compound leader skills remain UNIMPLEMENTED. Base stats, rounding and '+
   'enemy encounters remain DEMO. No save modifications.';
 panel.append(heading,summary,rows,caution);host.after(panel);
 function snapshot(){
   const recorded=(Array.isArray(S.party)?S.party:[]).
     map(u=>applied.get(u)).filter(Boolean);
   return freeze({mode:S.mode,active:S.mode==='archive',
     expandedRecipientCount:recorded.length,
     appliedSinceLoad:count,rejectedSinceLoad:rejected,
     extraSourceForms:42,sourceForms:72,leaderForms:30,
     actualRows:freeze(recorded),
     originalLeaderTypes31Or5Activated:false,
     savedFieldsAdded:0,trainingAffected:false});
 }
 function refresh(){
   const s=snapshot();
   panel.hidden=s.mode!=='archive';
   summary.textContent=s.expandedRecipientCount+
     ' additional source-qualified squad recipients in this battle';
   rows.replaceChildren();
   if(panel.open)for(const item of s.actualRows){
     const row=document.createElement('li');
     row.textContent='Slot '+(item.slot+1)+' · #'+item.unitId+
       ': ATK '+item.baseAtk+' → '+item.newAtk+
       ' (+'+item.atkPercent+'%), HP '+item.baseHp+
       ' → '+item.newHp+' (+'+item.hpPercent+'%)';
     rows.append(row);
   }
   return s;
 }
 panel.addEventListener('toggle',refresh);
 mode.addEventListener('change',()=>setTimeout(refresh,0));
 document.getElementById('reset')?.addEventListener('click',()=>setTimeout(refresh,0));
 const timer=setInterval(()=>{if(!document.hidden&&panel.open)refresh();},2300);
 window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 window.BFGlobalAllLeaderRecipientsV11300=freeze({
   source:freeze({masterArchiveSha256:
     '69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
     scope:'Original 2022 type2 leader, all 72 source-proven same-element forms',
     activatesUnknownLeaderSkills:false,changesSave:false,
     demoRoundingUnverified:true}),
   eligibility,apply,snapshot,refresh
 });
 refresh();
})();