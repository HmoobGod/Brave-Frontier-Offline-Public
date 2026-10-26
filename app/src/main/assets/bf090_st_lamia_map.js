/* BF_ORIGINAL_STLAMIA_MAP_V090 */
(() => {
  'use strict';
  if (window.BFStLamiaMapV090 || !window.BFMorganMapV080 ||
      !window.BFQuestAreas || !window.BFGlobalQuestText) return;
  const source=window.BF_STLAMIA_QUEST_DATA_V090;
  if(source?.schema!=='bf-global-st-lamia-2022-original-quests-v090' ||
     source.dungeons?.length!==7 || source.quests?.length!==36)return;
  const region=document.querySelector('.bf080-region-tabs'),
        mistral=document.querySelector('.bf-mistral-map'),
        morgan=document.getElementById('bf080-morgan-map'),
        quest=document.querySelector('section.questpanel'),
        list=document.getElementById('questlist');
  if(!region || !mistral || !morgan || !quest || !list)return;
  const oldButtons=Array.from(region.querySelectorAll('button'));
  if(oldButtons.length!==2)return;
  const ids=[300,310,320,330,340,350,360];
  if(source.dungeons.some((d,i)=>d.id!==ids[i] || d.areaId!==300 ||
       d.x<0||d.x>640||d.y<0||d.y>960))return;
  const tab=document.createElement('button');tab.type='button';
  tab.textContent='ST. LAMIA';tab.setAttribute('aria-pressed','false');region.append(tab);
  region.style.gridTemplateColumns='repeat(3,minmax(0,1fr))';
  const panel=document.createElement('section');
  panel.id='bf090-stlamia-map';panel.hidden=true;
  panel.setAttribute('aria-label','Original 2022 Brave Frontier Global St. Lamia area');
  panel.innerHTML=[
    '<header><img src="content/area/area_plate_0003.png" alt="Original St. Lamia map plate">',
    '<div><strong>ST. LAMIA · GRAND GAIA</strong>',
    '<small>Original 2022 region map and seven dungeons</small></div></header>',
    '<div class="bf090-map-frame"><img class="bf090-map-art"',
    ' src="content/area/area_0003.jpg" alt="Original St. Lamia world map">',
    '<div class="bf090-pin-layer" role="group" aria-label="St. Lamia dungeon locations"></div></div>',
    '<p id="bf090-map-status" aria-live="polite">Clear Tower of Morgan (Mission 265) to unlock St. Lamia.</p>',
    '<div class="bf090-map-list" role="group" aria-label="St. Lamia dungeon list"></div>',
    '<p>Original locations, English names, mission counts and artwork.',
    ' Encounter composition, AI, drops, timing and combat remain DEMO.</p>'
  ].join('');
  morgan.after(panel);
  const css=document.createElement('style');
  css.textContent=[
    '#bf090-stlamia-map{padding:10px;margin:0 0 12px;border:1px solid #947549;',
    'background:#151e30;color:#f4e5ce;border-radius:8px;font:12px system-ui}',
    '#bf090-stlamia-map[hidden]{display:none!important}',
    '#bf090-stlamia-map header{display:flex;align-items:center;gap:10px;margin-bottom:9px}',
    '#bf090-stlamia-map header img{width:120px;max-width:40%;height:auto;object-fit:contain}',
    '#bf090-stlamia-map header strong{display:block;font:800 15px Georgia,serif}',
    '#bf090-stlamia-map header small{display:block;font:11px Arial;color:#d0dbe8}',
    '.bf090-map-frame{position:relative;width:100%;max-width:500px;margin:auto;',
    'aspect-ratio:2/3;border:2px solid #947549;background:#10192a;overflow:hidden}',
    '.bf090-map-art{width:100%;height:100%;object-fit:fill;display:block}',
    '.bf090-pin-layer{position:absolute;inset:0;pointer-events:none}',
    '.bf090-pin{pointer-events:auto;position:absolute;transform:translate(-50%,-50%);',
    'border:2px solid #eed49f;background:#522e31;color:#fff;border-radius:50%;',
    'min-width:29px;min-height:29px;font:bold 10px Arial}',
    '.bf090-map-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin:10px 0}',
    '.bf090-map-list button{padding:8px 6px;text-align:left;min-height:55px;',
    'background:#273547;color:#f1e5ca;border:1px solid #957a53;border-radius:5px}',
    '.bf090-map-list button strong,.bf090-map-list button small{display:block}',
    '.bf090-map-list button small{opacity:.8;margin-top:4px}',
    '.bf090-locked{opacity:.58}',
    '.bf090-pin[aria-pressed=true],.bf090-map-list button[aria-pressed=true]{outline:2px solid #9de3fa}'
  ].join('');
  document.head.append(css);
  const pins=panel.querySelector('.bf090-pin-layer'),
        rows=panel.querySelector('.bf090-map-list'),
        notice=panel.querySelector('#bf090-map-status'),controls=new Map();
  let selected=false;
  function access(id){return QUESTS.some(q=>q.dungeonId===id&&questUnlocked(q))}
  function chooseRegion(){
    window.BFMorganMapV080.chooseRegion('mistral');
    mistral.hidden=true;morgan.hidden=true;panel.hidden=false;
    oldButtons.forEach(b=>b.setAttribute('aria-pressed','false'));
    tab.setAttribute('aria-pressed','true');
    selected=true;refresh();return true;
  }
  tab.addEventListener('click',chooseRegion);
  for(const button of oldButtons)button.addEventListener('click',()=>{
    panel.hidden=true;tab.setAttribute('aria-pressed','false');selected=false;
  });
  function openDungeon(id){
    const d=source.dungeons.find(d=>d.id===id);
    if(!d)return false;
    const options=QUESTS.filter(q=>q.dungeonId===id&&questUnlocked(q));
    if(!options.length){
      notice.textContent=d.name+' locked · clear Mission '+d.requires+' first';
      return false;
    }
    const next=options.find(q=>!P.questClears?.[q.missionId])||options[options.length-1];
    if(QUEST.missionId!==next.missionId && !BFQuestAreas.choose(next)){
      notice.textContent='Cannot select a mission during an action.';return false;
    }
    quest.querySelector('.bf-quest-area-tabs [data-bf-dungeon="'+id+'"]')?.click();
    notice.textContent=d.name+' · '+(BFGlobalQuestText.sourceFor(QUEST)?.mission.name||'Mission '+QUEST.missionId);
    chooseRegion();return true;
  }
  for(const d of source.dungeons){
    const pin=document.createElement('button');pin.type='button';
    pin.className='bf090-pin';pin.dataset.bfStLamiaPin=String(d.id);
    pin.textContent=String(d.id);
    pin.style.left=d.x/640*100+'%';pin.style.top=d.y/960*100+'%';
    pin.addEventListener('click',()=>openDungeon(d.id));pins.append(pin);
    const row=document.createElement('button');row.type='button';
    row.dataset.bfStLamiaList=String(d.id);
    row.innerHTML='<strong></strong><small></small>';
    row.querySelector('strong').textContent=d.name;
    row.addEventListener('click',()=>openDungeon(d.id));rows.append(row);
    controls.set(d.id,{pin,row});
  }
  function refresh(){
    for(const d of source.dungeons){
      const {pin,row}=controls.get(d.id),ok=access(d.id);
      const clear=QUESTS.filter(q=>q.dungeonId===d.id && P.questClears?.[q.missionId]).length;
      pin.classList.toggle('bf090-locked',!ok);row.classList.toggle('bf090-locked',!ok);
      pin.setAttribute('aria-pressed',String(QUEST?.dungeonId===d.id));
      row.setAttribute('aria-pressed',String(QUEST?.dungeonId===d.id));
      const text=(ok?'AVAILABLE':'LOCKED')+' · '+clear+'/'+QUESTS.filter(q=>q.dungeonId===d.id).length+' cleared';
      row.querySelector('small').textContent=text;
      pin.setAttribute('aria-label',d.name+', '+text);
    }
  }
  new MutationObserver(refresh).observe(list,{childList:true});
  refresh();
  if(ids.includes(QUEST?.dungeonId))chooseRegion();
  window.BFStLamiaMapV090=Object.freeze({
    entries:Object.freeze(source.dungeons.slice()),refresh,openDungeon,chooseRegion,
    isUnlocked:access,get selectedRegion(){return selected?'stlamia':null}
  });
})();
