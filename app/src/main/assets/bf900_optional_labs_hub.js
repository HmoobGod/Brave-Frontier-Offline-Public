/* BF_GLOBAL_OPTIONAL_LABS_HUB_V900 */
(() => {
 'use strict';
 if(window.BFOptionalLabsHubV900 || typeof P==='undefined'||P?.version!==7||
    typeof QUESTS==='undefined'||QUESTS.length!==106||
    !window.BFGlobalUnitArchive||BFGlobalUnitArchive.count!==2291||
    !window.BFGrandGaiaCampaignV100||!window.BFArchiveDraftV800)return;
 const ids=['bf200-trials','bf250-squad','bf300-tactics','bf400-dossier','bf800-draft'];
 const labs=ids.map(id=>document.getElementById(id));
 if(labs.some(x=>!x))return;
 const first=labs[0],host=first.closest('section.questpanel');
 if(!host||!labs.every(el=>host.contains(el)))return;
 const style=document.createElement('style');style.id='bf900-labs-styles';
 style.textContent=[
  '#bf900-labs{border:1px solid #a99065;border-radius:8px;',
  'background:#182c40;color:#f3e7d4;padding:10px;',
  'margin:13px 2px;font:12px/1.5 system-ui,sans-serif}',
  '#bf900-labs > summary{font:bold 15px Georgia,serif;',
  'cursor:pointer;min-height:42px;display:flex;align-items:center}',
  '#bf900-description{margin:7px 0;color:#f6d6ac}',
  '#bf900-coverage{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));',
  'gap:6px;margin:8px 0}',
  '#bf900-coverage div{background:#293e52;border-radius:5px;padding:8px}',
  '#bf900-coverage strong{display:block;font-size:14px}',
  '#bf900-coverage small{display:block;color:#d1dce7}',
  '#bf900-labs-content{padding:4px 0}',
  '#bf900-labs-content > details{margin:8px 0}',
  '#bf900-labs:focus-within{outline-offset:2px}'
 ].join('');
 document.head.append(style);
 const hub=document.createElement('details');hub.id='bf900-labs';
 hub.setAttribute('aria-label','Optional Global archive research and experimental training labs');
 const summary=document.createElement('summary');
 summary.textContent='ARCHIVE RESEARCH & TRAINING · OPTIONAL';
 const caution=document.createElement('p');caution.id='bf900-description';
 caution.textContent='The original-style story and quest controls remain outside this closed-by-default research area. These five read-only or synthetic experiments use recovered 2014 / 2022 records; no native original battle rules or quest rewards are claimed.';
 const coverage=document.createElement('div');coverage.id='bf900-coverage';
 const content=document.createElement('div');content.id='bf900-labs-content';
 hub.append(summary,caution,coverage,content);
 first.before(hub);
 for(const lab of labs)content.append(lab);
 function refresh(){
   const clears=QUESTS.filter(q=>(P.questClears?.[q.missionId]||0)>0).length;
   const tiles=[
     [clears+' / 106','Original Global missions cleared in demo'],
     ['23','Recorded original-region dungeons'],
     ['2,291','Recovered 2022 unit encyclopedia forms'],
     ['5','Source research and isolated training labs']
   ];
   coverage.replaceChildren();
   for(const [n,description] of tiles){
     const card=document.createElement('div');
     const strong=document.createElement('strong');strong.textContent=n;
     const small=document.createElement('small');small.textContent=description;
     card.append(strong,small);coverage.append(card);
   }
   return {cleared:clears,total:106,dungeons:23,archiveForms:2291,labs:5};
 }
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 hub.addEventListener('toggle',()=>{if(hub.open)refresh();});
 refresh();
 window.BFOptionalLabsHubV900=Object.freeze({
   get open(){return hub.open;},
   get labCount(){return labs.length;},
   get labIds(){return ids.slice();},
   refresh,openHub(){hub.open=true;return refresh();},
   closeHub(){hub.open=false;return true;}
 });
})();
