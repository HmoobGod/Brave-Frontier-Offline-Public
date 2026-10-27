/* BF_GLOBAL_ALL_PLAYABLE_LEADER_SOURCE_V11200 */
(() => {
 'use strict';
 // 72 exact 2022 F_UNIT => F_LEADER_SKILL records. Only v111 has
 // verified live starter type2 stat effects; type31/5/compound are RAW.
 const starter=window.BFGlobalStarterLeaderSourceV11000;
 if(window.BFGlobalPlayableLeadersV11200||!starter||
    typeof starter.lookup!=='function'||typeof P==='undefined'||P.version!==7)return;
 const freeze=Object.freeze,byId=new Map();
 const archive='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9';
 for(let element=1;element<=6;element++)for(let i=0;i<5;i++){
   const uid=element*10000+11+i,old=starter.lookup(uid);
   if(!old||old.element!==element||old.unitId!==uid)return;
   byId.set(uid,freeze({unitId:uid,rarity:i+2,element,
     lsId:old.lsId,skillTypeRaw:'2',passiveSkillInfoRaw:old.passive,
     v111SourceQualified:true,unimplementedRaw:false}));
 }
 const extra=[[10021,2,1,1300,"31","15,0,0,0,0,0"],[10022,3,1,1301,"31","30,0,0,0,0,0"],[10023,4,1,1302,"31","50,0,0,0,0,0"],[10024,5,1,1302,"31","50,0,0,0,0,0"],[10025,6,1,1313,"31@34","50,0,0,0,0,0@0.5"],[10041,2,1,500,"5","1,10"],[10042,3,1,500,"5","1,10"],[20021,2,2,1300,"31","15,0,0,0,0,0"],[20022,3,2,1301,"31","30,0,0,0,0,0"],[20023,4,2,1302,"31","50,0,0,0,0,0"],[20024,5,2,1302,"31","50,0,0,0,0,0"],[20025,6,2,1303,"31","75,0,0,0,0,0"],[20041,2,2,502,"5","2,10"],[20042,3,2,502,"5","2,10"],[30021,2,3,1400,"31","0,30,0,0,0,0"],[30022,3,3,1401,"31","0,50,0,0,0,0"],[30023,4,3,1402,"31","0,70,0,0,0,0"],[30024,5,3,1402,"31","0,70,0,0,0,0"],[30025,6,3,1410,"31@48","0,70,0,0,0,0@15"],[30041,2,3,504,"5","3,10"],[30042,3,3,504,"5","3,10"],[40021,2,4,1400,"31","0,30,0,0,0,0"],[40022,3,4,1401,"31","0,50,0,0,0,0"],[40023,4,4,1402,"31","0,70,0,0,0,0"],[40024,5,4,1402,"31","0,70,0,0,0,0"],[40025,6,4,1411,"31@49","0,70,0,0,0,0@15,20,100"],[40041,2,4,506,"5","4,10"],[40042,3,4,506,"5","4,10"],[50021,2,5,1400,"31","0,30,0,0,0,0"],[50022,3,5,1401,"31","0,50,0,0,0,0"],[50023,4,5,1402,"31","0,70,0,0,0,0"],[50024,5,5,1402,"31","0,70,0,0,0,0"],[50025,6,5,1412,"31@32","0,70,0,0,0,0@20"],[50041,2,5,508,"5","5,10"],[50042,3,5,508,"5","5,10"],[60021,2,6,1300,"31","15,0,0,0,0,0"],[60022,3,6,1301,"31","30,0,0,0,0,0"],[60023,4,6,1302,"31","50,0,0,0,0,0"],[60024,5,6,1302,"31","50,0,0,0,0,0"],[60025,6,6,1314,"31@29","50,0,0,0,0,0@15"],[60041,2,6,510,"5","6,10"],[60042,3,6,510,"5","6,10"]];
 for(const [unitId,rarity,element,lsId,skillTypeRaw,passiveSkillInfoRaw] of extra){
   if(byId.has(unitId)||!Number.isSafeInteger(unitId)||
     !Number.isSafeInteger(lsId)||typeof skillTypeRaw!=='string'||
     typeof passiveSkillInfoRaw!=='string')return;
   byId.set(unitId,freeze({unitId,rarity,element,lsId,skillTypeRaw,
     passiveSkillInfoRaw,v111SourceQualified:false,unimplementedRaw:true}));
 }
 if(byId.size!==72||new Set([...byId.values()].map(x=>x.lsId)).size!==36||
   byId.get(10021)?.passiveSkillInfoRaw!=='15,0,0,0,0,0'||
   byId.get(10041)?.skillTypeRaw!=='5'||
   byId.get(60025)?.skillTypeRaw!=='31@29')return;
 function lookup(id){return Number.isSafeInteger(id)?byId.get(id)||null:null;}
 const source=freeze({archive:'2022 F_UNIT_MST_1/2_Ver1084.json + F_LEADER_SKILL_MST_Ver749.json',
   sourceZipSha256:archive,forms:72,leaderSkills:36,
   rawSemanticsUnverifiedForNonType2:true,savedFieldsAdded:0,combatChanges:false});
 const host=document.getElementById('bf11000-leader-audit')||
   document.getElementById('squadpicker');
 if(!host)return;
 const panel=document.createElement('details');panel.id='bf11200-playable-leaders';
 panel.style.cssText='padding:10px;margin:9px 2px;border:1px solid #a3b29e;'+
   'border-radius:7px;background:#233339;color:#f6f3e9;font:12px/1.5 system-ui,sans-serif';
 const title=document.createElement('summary');
 title.textContent='2022 ORIGINAL LEADER SKILLS · ALL 72 PLAYABLE FORMS';
 title.style.cssText='min-height:35px;font-weight:800;cursor:pointer';
 const select=document.createElement('select');select.id='bf11200-form';
 select.style.cssText='background:#294955;color:#fff;border:1px solid #a2baba;'+
   'min-height:40px;max-width:100%;width:100%';
 const output=document.createElement('p');output.id='bf11200-raw';
 const caution=document.createElement('small');
 caution.textContent='Exact original 2022 leader skill type and raw passive fields. '+
   'v111 only applies source-verified starter type2 ATK/HP effects in archive DEMO. '+
   'Type31 spark, type5 elemental and compound @ effects are NOT implemented '+
   'by this reader; native timing, recipients and stacking still need proof.';
 for(const row of byId.values()){
   const option=document.createElement('option');option.value=String(row.unitId);
   option.textContent='#'+row.unitId+' · '+row.rarity+'★ LS #'+row.lsId;
   select.append(option);
 }
 panel.append(title,select,output,caution);host.after(panel);
 function refresh(){
   const row=lookup(Number(select.value));
   output.textContent=row?('Unit #'+row.unitId+' · Leader #'+row.lsId+
     ' · original skillType '+row.skillTypeRaw+' · passive '+
     row.passiveSkillInfoRaw+(row.unimplementedRaw?' · RAW ONLY':' · v111 sourced stat skill')):
     'Unknown archived leader profile';
   return row;
 }
 select.addEventListener('change',refresh);refresh();
 window.BFGlobalPlayableLeadersV11200=freeze({source,lookup,refresh,
   snapshot:()=>freeze({current:lookup(Number(select.value)),
     count:byId.size,mode:typeof S==='undefined'?null:S.mode,saveFieldsAdded:0})});
})();
