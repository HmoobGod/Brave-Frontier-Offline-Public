/* BF_GRAND_GAIA_CAMPAIGN_V100 */
(() => {
 'use strict';
 if(window.BFGrandGaiaCampaignV100) return;
 if(!window.BFMistralMap || !window.BFMorganMapV080 || !window.BFStLamiaMapV090 ||
    !window.BFQuestAreas || typeof QUESTS==='undefined' || QUESTS.length!==106) return;
 const regions=Object.freeze([
  Object.freeze({name:'Mistral',key:'mistral',ids:[1,10,20,30,40,50,60,70,80],required:0}),
  Object.freeze({name:'Morgan',key:'morgan',ids:[200,210,220,230,240,250,260],required:85}),
  Object.freeze({name:'St. Lamia',key:'stlamia',ids:[300,310,320,330,340,350,360],required:265})
 ]);
 const tabs=document.querySelector('.bf080-region-tabs');
 const list=document.getElementById('questlist');
 if(!tabs || !list || tabs.querySelectorAll('button').length!==3)return;
 const idset=new Set(regions.flatMap(r=>r.ids));
 if(idset.size!==23 || QUESTS.some(q=>!idset.has(q.dungeonId)))return;
 const style=document.createElement('style');
 style.id='bf100-campaign-style';
 style.textContent=[
  '#bf100-campaign{padding:12px 10px;margin:10px 0;border:1px solid #bb9860;',
  'border-radius:8px;background:linear-gradient(165deg,#182b44,#192233);color:#f6e9d5}',
  '#bf100-campaign h3{margin:0;font:800 16px Georgia,serif;letter-spacing:.03em}',
  '#bf100-campaign .bf100-subtitle{display:block;font:11px/1.5 Arial,sans-serif;color:#e1d0b6}',
  '.bf100-overall{margin:7px 0;font:700 13px Arial,sans-serif}',
  '.bf100-region-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));',
  'gap:7px;margin-top:8px}',
  '.bf100-region{display:flex;flex-direction:column;min-height:75px;padding:8px 5px;',
  'gap:4px;background:#253951;border:1px solid #8b9ab3;border-radius:5px;',
  'color:#fff;cursor:pointer;text-align:center}',
  '.bf100-region strong{font:700 12px Arial,sans-serif}',
  '.bf100-region small{font:11px Arial,sans-serif;color:#ddd}',
  '.bf100-region[aria-pressed=true]{border-color:#a3edfc;outline:1px solid #9edff0}',
  '.bf100-region progress{width:100%;height:7px;accent-color:#80cddc}',
  '#bf100-campaign .bf100-foot{display:block;margin-top:7px;',
  'font:10px/1.45 Arial,sans-serif;color:#c6d3dd}'
 ].join('');
 document.head.append(style);
 const section=document.createElement('section');
 section.id='bf100-campaign';
 section.setAttribute('aria-label','Source-backed offline Grand Gaia story progress');
 const header=document.createElement('h3');
 header.textContent='GRAND GAIA · CAMPAIGN PROGRESS';
 const hint=document.createElement('small');
 hint.className='bf100-subtitle';
 hint.textContent='Three original regions · 23 dungeons · 106 archived missions';
 const total=document.createElement('p');
 total.className='bf100-overall';
 total.setAttribute('aria-live','polite');
 const grid=document.createElement('div');grid.className='bf100-region-grid';
 const footer=document.createElement('small');
 footer.className='bf100-foot';
 footer.textContent='Original quest data and scenery. Battle enemies, AI, drops and combat calculations remain DEMO; archive Energy is not spent.';
 const controls=new Map();
 for(const region of regions){
   const button=document.createElement('button');
   button.type='button';button.className='bf100-region';
   button.dataset.bfCampaignRegion=region.key;
   const name=document.createElement('strong');name.textContent=region.name;
   const count=document.createElement('small');
   const bar=document.createElement('progress');
   bar.setAttribute('aria-label',region.name+' missions cleared');
   button.append(name,count,bar);
   button.addEventListener('click',()=>{
     if(region.key==='mistral')tabs.children[0].click();
     else if(region.key==='morgan')tabs.children[1].click();
     else tabs.children[2].click();
     refresh();
   });
   controls.set(region.key,{button,count,bar});
   grid.append(button);
 }
 section.append(header,hint,total,grid,footer);
 tabs.before(section);
 function summary(){
   const entries=regions.map(r=>{
     const quests=QUESTS.filter(q=>r.ids.includes(q.dungeonId));
     const cleared=quests.filter(q=>(P.questClears?.[q.missionId]||0)>0).length;
     const unlocked=quests.some(q=>questUnlocked(q));
     return Object.freeze({name:r.name,key:r.key,cleared,total:quests.length,unlocked,
       required:r.required});
   });
   return Object.freeze({regions:Object.freeze(entries),
     cleared:entries.reduce((n,x)=>n+x.cleared,0),
     total:entries.reduce((n,x)=>n+x.total,0),
     dungeons:idset.size});
 }
 function refresh(){
   const info=summary();
   total.textContent=info.cleared+' / '+info.total+' original missions cleared';
   for(const r of info.regions){
     const {button,count,bar}=controls.get(r.key);
     const locked=!r.unlocked;
     count.textContent=r.cleared+' / '+r.total+(locked?' · LOCKED':'');
     bar.max=r.total;bar.value=r.cleared;
     button.title=locked?
       ('Complete Mission '+r.required+' to unlock '+r.name):
       ('Open '+r.name+' original area map');
     const selected=r.key==='mistral'?!document.querySelector('.bf-mistral-map')?.hidden:
       r.key==='morgan'?!document.getElementById('bf080-morgan-map')?.hidden:
       !document.getElementById('bf090-stlamia-map')?.hidden;
     button.setAttribute('aria-pressed',String(selected));
     button.setAttribute('aria-label',r.name+', '+r.cleared+' of '+r.total+
       ' missions cleared'+(locked?', locked':''));
   }
   return info;
 }
 new MutationObserver(refresh).observe(list,{childList:true});
 tabs.addEventListener('click',refresh);
 refresh();
 window.BFGrandGaiaCampaignV100=Object.freeze({summary,refresh,
    get missionCount(){return 106},get dungeonCount(){return 23}});
})();
