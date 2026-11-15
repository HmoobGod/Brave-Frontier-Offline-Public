/* BF_GLOBAL_PLAYABLE_COMBAT_JOURNAL_V3200 */
(() => {
 'use strict';
 if(window.BFGlobalCombatJournalV3200 || !window.BFGlobalBattleResultsV3000 ||
    typeof S==='undefined'||typeof P==='undefined'||P.version!==7)return;
 const log=document.getElementById('log'),host=log?.parentElement;
 if(!log||!host||!log.parentElement)return;
 const css=document.createElement('style');css.id='bf3200-style';
 css.textContent='#bf3200-journal{padding:10px;margin:10px 0;border:1px solid #a38c69;border-radius:7px;background:#182c3f;color:#f1e7d3;font:12px/1.5 system-ui,sans-serif}'+
 '#bf3200-journal summary{font-weight:800;cursor:pointer;min-height:44px}'+
 '#bf3200-journal button{min-height:44px;margin:6px 7px 7px 0;padding:8px 10px;border:1px solid #bca078;border-radius:5px;background:#47617a;color:#fff;font-weight:bold}'+
 '#bf3200-journal button:disabled{opacity:.45}'+
 '#bf3200-report{box-sizing:border-box;width:100%;min-height:145px;padding:10px;background:#0c1a29;color:#eef5fc;border:1px solid #7e91a8;font:12px/1.4 monospace;resize:vertical}'+
 '#bf3200-count{color:#d0e0ed;margin:7px 0}'+
 '#bf3200-search{box-sizing:border-box;width:100%;min-height:44px;'+
 'margin:5px 0;padding:8px 10px;color:#eef5fc;background:#12263a;'+
 'border:1px solid #a4b4c8;border-radius:5px;font:14px system-ui,sans-serif}'+
 '#bf3200-filter-count{display:block;color:#d0e0ed;margin:0 0 6px}';
 css.textContent+='#bf3200-round-label{display:block;margin:6px 0}'+
 '#bf3200-round{box-sizing:border-box;width:100%;min-height:44px;padding:7px;'+
 'background:#12263a;color:#eef5fc;border:1px solid #a4b4c8;border-radius:5px}';
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf3200-journal';
 const title=document.createElement('summary');title.textContent='EXTENDED COMBAT JOURNAL · SESSION ONLY';
 const count=document.createElement('p');count.id='bf3200-count';
 const currentButton=document.createElement('button');currentButton.type='button';
 currentButton.id='bf3200-current';currentButton.textContent='CURRENT RUN';
 const previousButton=document.createElement('button');previousButton.type='button';
 previousButton.id='bf3200-previous';previousButton.textContent='PREVIOUS RUN';
 const search=document.createElement('input');search.id='bf3200-search';
 search.type='search';search.maxLength=80;search.autocomplete='off';
 search.placeholder='Filter retained combat entries';
 search.setAttribute('aria-label','Filter current or previous demo combat entries');
 const roundLabel=document.createElement('label');roundLabel.id='bf3200-round-label';
 roundLabel.textContent='SHOW ENTRIES ';
 const roundScope=document.createElement('select');roundScope.id='bf3200-round';
 roundScope.setAttribute('aria-label','Demo combat journal round view');
 for(const [value,text] of [['all','All recorded rounds'],
     ['latest','Latest recorded wave / round']]){
   const option=document.createElement('option');option.value=value;
   option.textContent=text;roundScope.append(option);
 }
 roundLabel.append(roundScope);
 const clear=document.createElement('button');clear.type='button';
 clear.id='bf3200-clear';clear.textContent='CLEAR FILTERS';
 const filterCount=document.createElement('small');filterCount.id='bf3200-filter-count';
 filterCount.setAttribute('role','status');
 const select=document.createElement('button');select.type='button';
 select.id='bf3200-select';select.textContent='SELECT REPORT TEXT';
 const output=document.createElement('textarea');output.id='bf3200-report';
 output.readOnly=true;output.setAttribute('aria-label','Read-only offline battle run report');
 const foot=document.createElement('small');
 foot.textContent='Captures the DEMO combat log while this app stays open, including removed on-screen log lines (up to 400 entries). No files, permissions, network calls or saved progress. Select text to copy it manually.';
 panel.append(title,count,currentButton,previousButton,search,roundLabel,clear,filterCount,select,output,foot);
 host.after(panel);
 const make=()=>({missionId:typeof QUEST==='undefined'?null:QUEST.missionId,
   mode:S.mode,items:[],wave:S.wave+1,round:S.round,phase:S.phase||'',complete:false});
 let observed=S,active=make(),previous=null,view='current',generation=0;
 function rotate(){
   if(observed===S)return;
   active.complete=!!observed.over;
   previous=active;observed=S;active=make();view='current';generation++;
 }
 function capture(entry){
   if(!entry||!entry.trim())return;
   active.items.push(Object.freeze({wave:S.wave+1,round:S.round,text:entry.trim()}));
   // Count alone stops changing at capacity, and native messages can repeat
   // verbatim across rounds. Refresh the view for every new retained record.
   generation++;
   if(active.items.length>400)active.items.shift();
   active.phase=S.phase||'';active.round=S.round;active.wave=S.wave+1;active.complete=!!S.over;
 }
 function record(events){
   rotate();
   for(const event of events){
     for(const node of event.addedNodes){
       if(node.nodeType===1&&node.tagName==='P')capture(node.textContent||'');
     }
   }
   refresh();
 }
 // Seed the original nine-line widget in chronological order, then retain future
 // lines from childList addedNodes even if native msg() trims them in one tick.
 for(const p of [...log.children].reverse())capture(p.textContent||'');
 const observer=new MutationObserver(record);
 observer.observe(log,{childList:true});
 function roundItems(source,scope){
   if(scope!=='latest')return source.items;
   // Use the selected run's last retained record, never current S metadata
   // while reading a previous run. A wave change may restart round numbering.
   const last=source.items[source.items.length-1];
   if(!last||!Number.isSafeInteger(last.wave)||last.wave<1||
      !Number.isSafeInteger(last.round)||last.round<1)return [];
   return source.items.filter(item=>item.wave===last.wave&&item.round===last.round);
 }
 function report(which=view,query='',scope='all'){
   rotate();
   const source=which==='previous'?previous:active;
   if(!source)return null;
   const term=typeof query==='string'?query.trim().slice(0,80).toLocaleLowerCase():'';
   const scoped=roundItems(source,scope);
   const items=term?scoped.filter(entry=>
     entry.text.toLocaleLowerCase().includes(term)):scoped;
   const header=['BRAVE FRONTIER GLOBAL · DEMO COMBAT LOG',
     'Mission ID: '+(source.missionId??'unknown'),
     'Mode: '+source.mode,
     'Final round seen: '+(source===active?S.round:source.round),
     'Entries retained: '+source.items.length,
     'Source enemy identities and AI are not restored.'];
   if(term)header.push('Session filter: '+term+' · '+items.length+' matching entries');
   if(scope==='latest')header.push(scoped.length?
     'Session round view: latest recorded Wave '+scoped[0].wave+' / Round '+scoped[0].round:
     'Session round view: latest recorded round unavailable');
   for(const entry of items)header.push('[Wave '+entry.wave+' / Round '+entry.round+'] '+entry.text);
   return header.join('\n');
 }
 let renderKey='';
 function snapshot(){
   rotate();return Object.freeze({
     current:active.items.length,previous:previous?.items.length||0,
     mode:view,missionId:active.missionId,capacity:400,
     lastEntry:active.items[active.items.length-1]?.text||null
   });
 }
 function refresh(){
   const s=snapshot(),term=search.value.trim().slice(0,80).toLocaleLowerCase();
   const key=JSON.stringify([s,generation,term,roundScope.value]);
   if(key!==renderKey){
     renderKey=key;
     count.textContent='Current '+s.current+' retained entries · Previous '+s.previous+' · cap '+s.capacity;
     previousButton.disabled=!previous;
     const source=view==='previous'?previous:active;
     const items=source?roundItems(source,roundScope.value):[];
     const matches=term?items?.filter(item=>item.text.toLocaleLowerCase().includes(term)).length||0:items?.length||0;
     const label=roundScope.value==='latest'?'latest-round':'retained';
     filterCount.textContent=term?matches+' of '+items.length+' '+label+' entries match':
       items.length+' '+label+' entries shown';
     output.value=report(view,term,roundScope.value)||'';
   }
   return s;
 }
 function show(which){
   if(which!=='current'&&which!=='previous')return false;
   if(which==='previous'&&!previous)return false;
   view=which;renderKey='';refresh();return true;
 }
 currentButton.addEventListener('click',()=>show('current'));
 previousButton.addEventListener('click',()=>show('previous'));
 search.addEventListener('input',refresh);
 roundScope.addEventListener('change',refresh);
 clear.addEventListener('click',()=>{
   search.value='';roundScope.value='all';renderKey='';refresh();search.focus();
 });
 select.addEventListener('click',()=>{output.focus();output.select()});
 panel.addEventListener('toggle',refresh);
 refresh();
 window.BFGlobalCombatJournalV3200=Object.freeze({snapshot,refresh,show,report});
})();
