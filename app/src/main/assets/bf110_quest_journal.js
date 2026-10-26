/* BF_GLOBAL_QUEST_JOURNAL_V110 */
(() => {
 'use strict';
 if (window.BFGlobalQuestJournalV110 ||
     typeof QUESTS==='undefined' || QUESTS.length!==106 ||
     !window.BFGlobalQuestText || !window.BFQuestAreas ||
     !window.BFGrandGaiaContinueV101 ||
     !window.BFMorganMapV080 || !window.BFStLamiaMapV090) return;
 const host=document.getElementById('bf101-story-continue');
 const list=document.getElementById('questlist');
 const tabs=document.querySelector('.bf080-region-tabs');
 if(!host || !list || !tabs || tabs.querySelectorAll('button').length!==3 ||
    QUESTS[0]?.missionId!==1 || QUESTS[105]?.missionId!==365) return;
 const archive=QUESTS.map(q=>{
   const source=BFGlobalQuestText.sourceFor(q);
   if(!source || !source.mission?.name || !source.dungeon?.name ||
      typeof source.mission.description!=='string') return null;
   return Object.freeze({q,id:q.missionId,region:q.dungeonId>=300?'stlamia':
     q.dungeonId>=200?'morgan':'mistral',name:source.mission.name,
     dungeon:source.dungeon.name,description:source.mission.description});
 });
 // Never show ambiguous IDs or guessed translations.
 if(archive.some(row=>!row) || new Set(archive.map(r=>r.id)).size!==106)return;
 const style=document.createElement('style');
 style.textContent=[
   '#bf110-journal{margin:10px 0;padding:9px;border:1px solid #a78c60;',
   'border-radius:7px;background:#1b283b;color:#f7e9ce;font:12px/1.5 system-ui,sans-serif}',
   '#bf110-journal summary{cursor:pointer;font:bold 14px Georgia,serif;min-height:30px}',
   '.bf110-filters{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin:10px 0}',
   '.bf110-filters label{display:flex;flex-direction:column;gap:3px;font-size:11px}',
   '.bf110-filters input,.bf110-filters select{box-sizing:border-box;width:100%;min-height:37px;',
   'padding:7px;border:1px solid #9e895e;border-radius:4px;background:#111c2b;color:white}',
   '#bf110-search-wrap{grid-column:1/-1}',
   '#bf110-count{margin:5px 0;color:#dde5ea}',
   '.bf110-entry{display:grid;grid-template-columns:1fr auto;align-items:center;gap:5px;',
   'border-top:1px solid #485970;padding:7px 0}',
   '.bf110-entry strong{display:block;font-size:12px}',
   '.bf110-entry small{display:block;color:#c9d1d9}',
   '.bf110-actions{display:flex;gap:4px;flex-wrap:wrap}',
   '.bf110-actions button,#bf110-more{min-height:34px;padding:5px 7px;border:1px solid #ad986e;',
   'border-radius:4px;background:#31465c;color:#fff;font-weight:700}',
   '.bf110-actions button:disabled{opacity:.5;background:#30343c}',
   '#bf110-preview{margin:8px 0;padding:8px;border:1px solid #7c94a3;background:#172034;',
   'white-space:pre-wrap;overflow-wrap:anywhere}',
   '#bf110-foot{display:block;margin:9px 0 2px;color:#cad3de}'
 ].join('');
 document.head.append(style);

 const panel=document.createElement('details');panel.id='bf110-journal';
 panel.setAttribute('aria-label','Browse original Global quest journal');
 const title=document.createElement('summary');
 title.textContent='GLOBAL QUEST JOURNAL · 106 MISSIONS';
 const filters=document.createElement('div');filters.className='bf110-filters';
 function selectFilter(id,label,values){
   const wrap=document.createElement('label');wrap.textContent=label;
   const control=document.createElement('select');control.id=id;
   for(const [value,name] of values){
     const option=document.createElement('option');option.value=value;option.textContent=name;
     control.append(option);
   }
   wrap.append(control);filters.append(wrap);return control;
 }
 const regions=selectFilter('bf110-region','REGION',[
    ['all','All three regions'],['mistral','Mistral'],['morgan','Morgan'],['stlamia','St. Lamia']]);
 const states=selectFilter('bf110-state','PROGRESS',[
    ['all','All missions'],['available','Available · uncleared'],['cleared','Cleared'],['locked','Locked']]);
 const searchWrap=document.createElement('label');searchWrap.id='bf110-search-wrap';
 searchWrap.textContent='FIND BY NAME / DUNGEON / MISSION ID';
 const search=document.createElement('input');
 search.id='bf110-search';search.type='search';search.autocomplete='off';
 search.placeholder='Search all 106 original quests';
 searchWrap.append(search);filters.append(searchWrap);
 const count=document.createElement('p');count.id='bf110-count';count.setAttribute('aria-live','polite');
 const preview=document.createElement('div');preview.id='bf110-preview';
 preview.setAttribute('aria-live','polite');
 preview.textContent='Select DETAILS to read an original archived mission description.';
 const results=document.createElement('div');results.id='bf110-results';
 const more=document.createElement('button');more.id='bf110-more';more.type='button';
 more.textContent='SHOW MORE MISSIONS';
 const foot=document.createElement('small');foot.id='bf110-foot';
 foot.textContent='Original Global quest text and recorded battle/energy/reward totals. Native enemies, AI, drops, combat math and Energy deduction remain DEMO.';
 panel.append(title,filters,count,preview,results,more,foot);
 host.after(panel);
 let visibleLimit=20, previewId=null;

 function progress(row){
   if((P.questClears?.[row.id]||0)>0)return 'cleared';
   return questUnlocked(row.q)?'available':'locked';
 }
 function matching(){
   const query=search.value.trim().toLocaleLowerCase();
   return archive.filter(row=>(regions.value==='all'||row.region===regions.value) &&
      (states.value==='all'||progress(row)===states.value) &&
      (!query || [String(row.id),row.name,row.dungeon].some(t=>t.toLocaleLowerCase().includes(query))));
 }
 function inspect(id){
   const row=archive.find(r=>r.id===Number(id));
   if(!row)return false;
   previewId=row.id;
   const q=row.q,locked=!questUnlocked(q),clears=P.questClears?.[q.missionId]||0;
   preview.textContent=[
     row.name+' · Mission '+row.id+' · '+row.dungeon,
     row.description,
     'Original recorded: '+q.battles+' battles · '+q.energy+' Energy cost · '+
         q.exp+' EXP · '+q.zel+' Zel · '+q.karma+' Karma',
     'Progress: '+(clears?clears+' clear(s)':locked?'LOCKED · requires Mission '+q.requires:'AVAILABLE'),
     'Original enemy formations, drop probabilities, native combat and Energy spending are not restored.'
   ].join('\n');
   return true;
 }
 function chooseMission(id){
   const row=archive.find(r=>r.id===Number(id));
   if(!row || !questUnlocked(row.q) || !!S?.busy)return false;
   if(!BFQuestAreas.choose(row.q))return false;
   const index=row.region==='stlamia'?2:row.region==='morgan'?1:0;
   tabs.querySelectorAll('button')[index]?.click();
   inspect(row.id);refresh();
   document.getElementById('bf-quest-details')?.scrollIntoView({block:'start',behavior:'smooth'});
   return true;
 }
 function refresh(){
   const rows=matching();
   count.textContent=rows.length+' matching missions · showing '+Math.min(visibleLimit,rows.length)+
     ' · '+rows.filter(r=>progress(r)==='available').length+' available and uncleared';
   const fragment=document.createDocumentFragment();
   for(const row of rows.slice(0,visibleLimit)){
     const state=progress(row);
     const item=document.createElement('div');item.className='bf110-entry';
     item.dataset.bfJournalEntry=String(row.id);
     const info=document.createElement('div');
     const name=document.createElement('strong');name.textContent=row.name;
     const meta=document.createElement('small');
     meta.textContent='Mission '+row.id+' · '+row.dungeon+' · '+
       state.toUpperCase()+(state==='locked'?' · clear '+row.q.requires:'');
     info.append(name,meta);
     const actions=document.createElement('div');actions.className='bf110-actions';
     const view=document.createElement('button');view.type='button';
     view.dataset.bfJournalPreview=String(row.id);view.textContent='DETAILS';
     view.addEventListener('click',()=>inspect(row.id));
     const go=document.createElement('button');go.type='button';
     go.dataset.bfJournalOpen=String(row.id);
     go.textContent=state==='locked'?'LOCKED':'OPEN';
     go.disabled=state==='locked'||!!S?.busy;
     go.addEventListener('click',()=>chooseMission(row.id));
     actions.append(view,go);item.append(info,actions);fragment.append(item);
   }
   results.replaceChildren(fragment);
   more.hidden=rows.length<=visibleLimit;
   more.disabled=!!S?.busy;
   if(previewId!==null)inspect(previewId);
   return rows.length;
 }
 function changed(){visibleLimit=20;refresh();}
 for(const s of [regions,states])s.addEventListener('change',changed);
 search.addEventListener('input',changed);
 more.addEventListener('click',()=>{visibleLimit+=20;refresh();});
 new MutationObserver(refresh).observe(list,{childList:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 refresh();
 window.BFGlobalQuestJournalV110=Object.freeze({
   get total(){return archive.length},
   get matchingCount(){return matching().length},
   get previewMission(){return previewId},
   refresh,inspect,chooseMission
 });
})();
