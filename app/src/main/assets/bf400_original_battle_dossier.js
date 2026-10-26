/* BF_GLOBAL_ORIGINAL_BATTLE_DOSSIER_V400 */
(() => {
 'use strict';
 if(window.BFGlobalBattleDossierV400 || typeof P==='undefined' || P?.version!==7 ||
   typeof QUESTS==='undefined'||QUESTS.length!==106||
   !window.BFGlobalUnitArchive || !window.BFArchiveTrialsV200 ||
   !window.BFSquadTrainingV250 || !window.BFTacticalRoundsV300 ||
   typeof effectiveUnit!=='function')return;
 const catalog=window.BFGlobalUnitArchive,history=window.BFArchiveTrialsV200;
 if(catalog.count!==2291||!catalog.originalCodexAvailable||
   history.missions!==21||history.historicalWaves!==112||
   history.historicalEntries!==264||history.distinctUnitIds!==42)return;
 const IDs=[1,2,10,11,20,21,30,31,40,41,42,50,51,52,60,61,70,71,200,202,240];
 if(IDs.some(id=>!history.sourceFor(id)?.waves?.length))return;
 const anchor=document.getElementById('bf300-tactics');
 if(!anchor)return;
 const css=document.createElement('style');css.id='bf400-dossier-style';
 css.textContent=[
  '#bf400-dossier{margin:12px 2px;padding:11px;background:#1d3045;',
  'border:1px solid #a99169;color:#f5e8d1;border-radius:8px;',
  'font:12px/1.5 system-ui,sans-serif}',
  '#bf400-dossier summary{cursor:pointer;min-height:33px;',
  'font:bold 15px Georgia,serif}',
  '#bf400-dossier select,#bf400-dossier button{min-height:40px;',
  'background:#314d6c;color:#f5f1e6;border:1px solid #af9a75;',
  'border-radius:5px;padding:7px;box-sizing:border-box}',
  '#bf400-dossier select{width:100%}',
  '#bf400-dossier button{margin:4px}',
  '.bf400-panel{border-top:1px solid #62758b;margin-top:8px;padding-top:8px}',
  '.bf400-row{display:flex;align-items:center;gap:8px;padding:6px;',
  'margin:5px 0;background:#273e56;border-radius:5px}',
  '.bf400-row img{width:44px;height:44px;flex:0 0 44px;object-fit:contain}',
  '.bf400-row strong,.bf400-row small{display:block;overflow-wrap:anywhere}',
  '.bf400-row small{color:#d3dae5}',
  '.bf400-skill{padding:7px;border:1px solid #536881;border-radius:5px;',
  'margin:5px 0;background:#23394f}',
  '.bf400-skill strong{display:block}',
  '.bf400-skill p{margin:3px 0}',
  '.bf400-caution{color:#ffe0ac}',
  '.bf400-kv{display:grid;grid-template-columns:1fr 1fr;gap:6px}',
  '.bf400-kv div{padding:6px;background:#253b55;border-radius:5px}',
  '#bf400-wave-foes{max-height:320px;overflow:auto}',
  '#bf400-integrity{color:#d5e0ec;font-size:11px}'
 ].join('');
 document.head.append(css);
 const root=document.createElement('details');root.id='bf400-dossier';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL GLOBAL BATTLE DOSSIER · v4.00';
 const caution=document.createElement('p');caution.className='bf400-caution';
 caution.textContent='2022 Global original unit names, elements, skills and English lore are read-only archive records. Enemy waves below come from dated 2014 files and are NOT verified 2022 Global wave formations. This research view does not change battle or progression.';
 const squadPanel=document.createElement('section');squadPanel.className='bf400-panel';
 const squadHeading=document.createElement('strong');
 squadHeading.textContent='OWNED SQUAD · 2022 SOURCE INTELLIGENCE';
 const squadSelect=document.createElement('select');squadSelect.id='bf400-unit';
 squadSelect.setAttribute('aria-label','Choose an equipped unit to inspect');
 const squadCard=document.createElement('div');squadCard.id='bf400-unit-card';
 const skills=document.createElement('div');skills.id='bf400-unit-skills';
 const update=document.createElement('button');update.type='button';
 update.id='bf400-refresh';update.textContent='REFRESH EQUIPPED SQUAD';
 squadPanel.append(squadHeading,squadSelect,squadCard,skills,update);
 const missionPanel=document.createElement('section');missionPanel.className='bf400-panel';
 const missionHeading=document.createElement('strong');
 missionHeading.textContent='2014 HISTORICAL ENCOUNTER SOURCES';
 const mission=document.createElement('select');mission.id='bf400-mission';
 mission.setAttribute('aria-label','Choose a historical mission');
 for(const id of IDs){
   const row=history.sourceFor(id);
   const option=document.createElement('option');option.value=String(id);
   option.textContent='Mission '+id+' · '+row.name;mission.append(option);
 }
 const wave=document.createElement('select');wave.id='bf400-wave';
 wave.setAttribute('aria-label','Select historical wave');
 const origin=document.createElement('p');origin.id='bf400-source';
 const metrics=document.createElement('div');metrics.id='bf400-wave-metrics';
 metrics.className='bf400-kv';
 const foes=document.createElement('div');foes.id='bf400-wave-foes';
 const integrity=document.createElement('p');integrity.id='bf400-integrity';
 missionPanel.append(missionHeading,mission,wave,origin,metrics,foes,integrity);
 root.append(heading,caution,squadPanel,missionPanel);
 anchor.after(root);
 const elements={1:'Fire',2:'Water',3:'Earth',4:'Thunder',5:'Light',6:'Dark'};
 const label=(node,value)=>{node.textContent=value;return node;};
 const para=value=>label(document.createElement('p'),value);
 const b=(value,cls)=>{const el=document.createElement('strong');el.textContent=value;
   if(cls)el.className=cls;return el;};
 const tag=(txt)=>{const el=document.createElement('small');el.textContent=txt;return el;};
 const selectedMission=()=>history.sourceFor(Number(mission.value));
 function equipped(){
   const seen=new Set(),out=[];
   if(!Array.isArray(P.squad)||!Array.isArray(P.roster))return out;
   for(const id of P.squad.slice(0,6)){
     if(!Number.isInteger(id)||seen.has(id)||!P.roster.includes(id))continue;
     seen.add(id);
     const unit=effectiveUnit(id);
     if(!unit||!Number.isInteger(unit.id))continue;
     const a=catalog.find(unit.id),record=catalog.originalRecord(unit.id);
     out.push({sourceId:id,formId:unit.id,name:a?.name||unit.name,
       element:a?.element??null,rarity:a?.rarity??null,thumbnail:!!a?.thumbnail,
       baseStats:a?.stats||null,original:record||null});
   }
   return out;
 }
 let selectedUnit=null;
 function refreshSquad(){
   const list=equipped();
   const keep=Number(squadSelect.value)||selectedUnit;
   squadSelect.replaceChildren();
   for(const u of list){
     const opt=document.createElement('option');
     opt.value=String(u.sourceId);
     opt.textContent=u.name+' · #'+u.formId;
     squadSelect.append(opt);
   }
   if(list.some(u=>u.sourceId===keep))squadSelect.value=String(keep);
   selectedUnit=list.some(u=>u.sourceId===keep)?keep:list[0]?.sourceId??null;
   showUnit(selectedUnit);return list.length;
 }
 function showUnit(baseId=Number(squadSelect.value)){
   const row=equipped().find(u=>u.sourceId===Number(baseId));
   squadCard.replaceChildren();skills.replaceChildren();
   if(!row){squadCard.append(para('No equipped, owned units to inspect.'));
     return null;}
   selectedUnit=row.sourceId;
   squadSelect.value=String(row.sourceId);
   const card=document.createElement('div');card.className='bf400-row';
   if(row.thumbnail){
     const img=document.createElement('img');img.loading='lazy';
     img.src='content/unit_archive/unit_ills_thum_'+row.formId+'.png';
     img.alt='Archived 2022 Global unit thumbnail';card.append(img);
   }
   const info=document.createElement('div');
   info.append(b(row.name+' · ★'+(row.rarity??'?')),
     tag('Original 2022 Global form #'+row.formId+' · '+
       (elements[row.element]||'Element unavailable')));
   if(row.baseStats){
     const st=row.baseStats;
     info.append(tag('ARCHIVED BASE HP '+(st.hp??'?')+' · ATK '+(st.atk??'?')+
       ' · DEF '+(st.def??'?')+' · REC '+(st.rec??'?')));
   }
   card.append(info);squadCard.append(card);
   if(!row.original){
     skills.append(para('Archived 2022 skill and lore records unavailable for this form.'));
     return {formId:row.formId,available:false,skillNames:[]};
   }
   let names=[];
   const abilityLabels=[['leader','LEADER SKILL'],['bb','BRAVE BURST'],
     ['sbb','SUPER BRAVE BURST'],['ubb','ULTIMATE BRAVE BURST'],
     ['extra','EXTRA SKILL']];
   for(const [key,heading] of abilityLabels){
     const ability=row.original[key];
     if(!ability)continue;
     const box=document.createElement('article');box.className='bf400-skill';
     const name=String(ability.name||'Name not recovered');
     names.push(name);
     box.append(b(heading+' · '+name),
       tag('Original 2022 Global skill ID '+(ability.id??'not recorded')));
     if(ability.description)box.append(para(String(ability.description)));
     skills.append(box);
   }
   if(row.original.story){
     const story=document.createElement('details');
     story.append(label(document.createElement('summary'),'ORIGINAL 2022 UNIT HISTORY'),
       para(String(row.original.story)));
     skills.append(story);
   }
   if(!names.length)skills.append(para('No original skill text recovered for this form.'));
   skills.append(para('Source skill descriptions are NOT simulated in the practice battle.'));
   return {formId:row.formId,available:true,skillNames:names};
 }
 function waveRows(){
   const row=selectedMission();
   const waveIndex=Number(wave.value);
   if(!row||!Number.isInteger(waveIndex)||waveIndex<1||
      waveIndex>row.waves.length)return [];
   return row.waves[waveIndex-1].enemies.map((e,i)=>{
     const now=catalog.find(e.unitId);
     return {slot:i+1,name:e.name,unitId:e.unitId,hp:e.hp,atk:e.atk,
       def:e.def,aiId:e.aiId,sourceYear:2014,
       unit2022:now?{name:now.name,element:elements[now.element]||null,
         thumbnail:!!now.thumbnail,exactName:now.name===e.name}:null};
   });
 }
 function showMission(id=Number(mission.value)){
   const row=history.sourceFor(Number(id));if(!row)return false;
   mission.value=String(row.id);wave.replaceChildren();
   for(let w=1;w<=row.waves.length;w++){
     const opt=document.createElement('option');opt.value=String(w);
     opt.textContent='2014 wave '+w+' / '+row.waves.length;wave.append(opt);
   }
   wave.value='1';return showWave();
 }
 function showWave(n=Number(wave.value)){
   const row=selectedMission();if(!row)return false;
   const w=Number(n);if(!Number.isInteger(w)||w<1||w>row.waves.length)return false;
   wave.value=String(w);
   const entries=waveRows();
   origin.replaceChildren(b('Historical 2014 data · '+row.name),
     tag(row.sourcePath+' · Git blob '+row.gitBlobSha),
     para('2014 enemy lineup; NOT authenticated 2022 native spawn, AI, rewards or damage rules.'));
   metrics.replaceChildren();
   const measures=[
     ['2014 enemy slots',entries.length],
     ['2014 total listed HP',entries.reduce((v,e)=>v+e.hp,0)],
     ['Largest 2014 ATK',Math.max(0,...entries.map(e=>e.atk))],
     ['2022 catalog IDs matched',entries.filter(e=>e.unit2022!==null).length]
   ];
   for(const [key,value] of measures){
     const div=document.createElement('div');
     div.append(tag(key),b(String(value)));metrics.append(div);
   }
   foes.replaceChildren();
   for(const e of entries){
     const card=document.createElement('div');card.className='bf400-row';
     if(e.unit2022?.thumbnail){
       const img=document.createElement('img');img.loading='lazy';
       img.src='content/unit_archive/unit_ills_thum_'+e.unitId+'.png';
       img.alt='2022 catalog thumbnail; not verified historical enemy battle sprite';
       card.append(img);
     }
     const detail=document.createElement('div');
     detail.append(b('2014 · '+e.name+' · #'+e.unitId+' · slot '+e.slot),
       tag('2014 HP '+e.hp+' · ATK '+e.atk+' · DEF '+e.def+
         ' · AI record '+e.aiId));
     if(e.unit2022){
       detail.append(tag('2022 catalog: '+e.unit2022.name+
         ' · '+e.unit2022.element+
         (e.unit2022.exactName?' · exact name match':' · name differs')));
     }else detail.append(tag('No matching 2022 catalog ID'));
     card.append(detail);foes.append(card);
   }
   integrity.textContent='Research coverage: '+history.missions+
     ' missions · '+history.historicalWaves+' archived waves · '+
     history.historicalEntries+' enemy slots · '+
     history.distinctUnitIds+' distinct archived enemy IDs; '+
     catalog.count+' original 2022 encyclopedia forms. Verified native 2022 formations: 0.';
   return true;
 }
 squadSelect.addEventListener('change',()=>showUnit(Number(squadSelect.value)));
 update.addEventListener('click',refreshSquad);
 mission.addEventListener('change',()=>showMission(Number(mission.value)));
 wave.addEventListener('change',()=>showWave(Number(wave.value)));
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(!root.open)return;
   refreshSquad();
 });
 new MutationObserver(()=>{
   if(root.open && !squadSelect.matches(':focus'))refreshSquad();
 }).observe(document.getElementById('bf-owned-box'),{childList:true});
 refreshSquad();showMission(1);
 window.BFGlobalBattleDossierV400=Object.freeze({
   get missionCount(){return IDs.length;},
   get sourceYear(){return 2014;},
   get originalUnitCount(){return catalog.count;},
   get squad(){return equipped().map(u=>({
     sourceId:u.sourceId,formId:u.formId,name:u.name,
     element:u.element,originalSkillAvailable:!!u.original}))},
   showUnit,refreshSquad,showMission,showWave,
   get waveEntries(){return waveRows().map(e=>({...e}));}
 });
})();
