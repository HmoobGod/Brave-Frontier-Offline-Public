/* BF_ORIGINAL_MORGAN_MAP_V080 */
(() => {
  'use strict';
  if (window.BFMorganMapV080 || !window.BFMistralMap ||
      !window.BFQuestAreas || !window.BFGlobalQuestText) return;
  const source=window.BF_MORGAN_QUEST_DATA_V080;
  if(source?.schema!=='bf-global-morgan-2022-original-quests-v080' ||
     source.dungeons?.length!==7 || source.quests?.length!==36)return;
  const questPanel=document.querySelector('section.questpanel');
  const mistral=document.querySelector('.bf-mistral-map');
  const list=document.getElementById('questlist');
  if(!questPanel || !mistral || !list)return;
  const dungeonIds=[200,210,220,230,240,250,260];
  if(source.dungeons.some((d,i)=>d.id!==dungeonIds[i] ||
     d.nameKey!=='MST_DUNGEONS_DUNGEON_'+d.id+'_NAME' ||
     d.areaId!==200 || d.x<0 || d.x>640 || d.y<0 || d.y>960))return;
  if(source.quests.some(q=>!dungeonIds.includes(q.dungeonId) ||
     !QUESTS.some(o=>o.missionId===q.missionId && o.dungeonId===q.dungeonId)))return;

  const style=document.createElement('style');
  style.id='bf080-morgan-style';
  style.textContent=[
    '.bf-mistral-map[hidden]{display:none!important}',
    '.bf080-region-tabs{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0 8px}',
    '.bf080-region-tabs button{min-height:42px;border:1px solid #b18e56;border-radius:5px;',
    'background:#26384a;color:#f3e5c2;font-weight:800;cursor:pointer}',
    '.bf080-region-tabs button[aria-pressed=true]{background:#73522c;color:#fff}',
    '#bf080-morgan-map{padding:10px;margin:0 0 12px;border:1px solid #947549;',
    'background:#151e30;color:#f4e5ce;border-radius:8px}',
    '#bf080-morgan-map[hidden]{display:none!important}',
    '#bf080-morgan-map header{display:flex;align-items:center;gap:10px;margin-bottom:9px}',
    '#bf080-morgan-map header img{width:120px;max-width:40%;height:auto;object-fit:contain}',
    '#bf080-morgan-map header strong{display:block;font:800 15px Georgia,serif}',
    '#bf080-morgan-map header small{font:11px Arial,sans-serif;color:#d0dbe8}',
    '.bf080-map-frame{position:relative;width:100%;max-width:500px;margin:auto;',
    'aspect-ratio:2/3;border:2px solid #947549;background:#10192a;overflow:hidden}',
    '.bf080-map-art{width:100%;height:100%;object-fit:fill;display:block}',
    '.bf080-pin-layer{position:absolute;inset:0;pointer-events:none}',
    '.bf080-pin{pointer-events:auto;position:absolute;transform:translate(-50%,-50%);',
    'border:2px solid #eed49f;background:#513c24;color:#fff;border-radius:50%;',
    'min-width:31px;min-height:31px;font:800 11px Arial;cursor:pointer}',
    '.bf080-pin[aria-pressed=true]{background:#0b8099;border-color:#b7faff}',
    '.bf080-pin.bf080-locked{opacity:.66;background:#252b35}',
    '.bf080-map-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin:12px 0}',
    '.bf080-map-list button{padding:8px;border:1px solid #8b7653;border-radius:5px;',
    'background:#26374d;color:#f2e4cf;text-align:left;cursor:pointer;min-height:48px}',
    '.bf080-map-list button strong{display:block;font:800 12px Georgia,serif}',
    '.bf080-map-list button small{display:block;font:10px Arial,sans-serif}',
    '.bf080-map-list button.bf080-locked{opacity:.65}',
    '.bf080-map-list button[aria-pressed=true]{outline:2px solid #96def0}',
    '#bf080-morgan-map p{font:12px/1.4 Arial,sans-serif}',
    '#bf080-morgan-map .bf080-note{font:10px/1.45 Arial,sans-serif;color:#c4d1de}'
  ].join('');
  document.head.append(style);
  const tabs=document.createElement('div');
  tabs.className='bf080-region-tabs';
  tabs.setAttribute('role','group');
  tabs.setAttribute('aria-label','Select Grand Gaia world area');
  const mistButton=document.createElement('button');
  mistButton.type='button';mistButton.dataset.bfRegion='mistral';
  mistButton.textContent='MISTRAL · 9 DUNGEONS';
  const morgButton=document.createElement('button');
  morgButton.type='button';morgButton.dataset.bfRegion='morgan';
  morgButton.textContent='MORGAN · 7 DUNGEONS';
  tabs.append(mistButton,morgButton);
  mistral.before(tabs);
  const panel=document.createElement('section');
  panel.id='bf080-morgan-map';
  panel.hidden=true;
  panel.setAttribute('aria-label','Original 2022 Brave Frontier Global Morgan area map');
  panel.innerHTML=[
    '<header><img src="content/area/area_plate_0002.png" alt="Original Morgan map plate">',
    '<div><strong>MORGAN · GRAND GAIA</strong><small>2022 Global map and original dungeon coordinates</small></div></header>',
    '<div class="bf080-map-frame"><img class="bf080-map-art" src="content/area/area_0002.jpg"',
    ' alt="Original Brave Frontier Morgan area map"><div class="bf080-pin-layer"',
    ' role="group" aria-label="Select a Morgan dungeon"></div></div>',
    '<p id="bf080-map-status" aria-live="polite">Clear Mistral Mission 85 to unlock Morgan.</p>',
    '<div class="bf080-map-list" role="group" aria-label="Morgan dungeon list"></div>',
    '<p class="bf080-note">Original map, names, English missions, wave counts, EXP/Zel and backgrounds.',
    ' Enemy formations, combat formulas, drops and cutscenes remain offline DEMO systems.</p>'
  ].join('');
  mistral.after(panel);
  const pins=panel.querySelector('.bf080-pin-layer'),items=panel.querySelector('.bf080-map-list');
  const status=panel.querySelector('#bf080-map-status');
  const controls=new Map();
  let selectedRegion='mistral';
  function chooseRegion(area){
     if(area!=='mistral' && area!=='morgan')return false;
     selectedRegion=area;
     mistral.hidden=area!=='mistral';
     panel.hidden=area!=='morgan';
     mistButton.setAttribute('aria-pressed',String(area==='mistral'));
     morgButton.setAttribute('aria-pressed',String(area==='morgan'));
     if(area==='morgan') refresh();
     return true;
  }
  mistButton.addEventListener('click',()=>chooseRegion('mistral'));
  morgButton.addEventListener('click',()=>chooseRegion('morgan'));
  function unlocked(d){return QUESTS.some(q=>q.dungeonId===d.id && questUnlocked(q));}
  function openDungeon(id){
    const entry=source.dungeons.find(x=>x.id===id);
    if(!entry)return false;
    const candidates=QUESTS.filter(q=>q.dungeonId===id && questUnlocked(q));
    if(!candidates.length){
       status.textContent=entry.name+' locked · clear Mission '+entry.requires+' first';
       return false;
    }
    const target=candidates.find(q=>!P.questClears?.[q.missionId])||candidates[candidates.length-1];
    if(QUEST.missionId!==target.missionId && !BFQuestAreas.choose(target)){
       status.textContent='Cannot switch quests during battle.';
       return false;
    }
    questPanel.querySelector('.bf-quest-area-tabs [data-bf-dungeon="'+id+'"]')?.click();
    status.textContent=entry.name+' · '+(BFGlobalQuestText.sourceFor(QUEST)?.mission.name||'Mission '+QUEST.missionId);
    chooseRegion('morgan');refresh();return true;
  }
  for(const d of source.dungeons){
    const pin=document.createElement('button');pin.type='button';
    pin.className='bf080-pin';pin.dataset.bfMorganPin=String(d.id);
    pin.textContent=String(d.id);pin.title=d.name;
    pin.style.left=d.x/640*100+'%';pin.style.top=d.y/960*100+'%';
    pin.addEventListener('click',()=>openDungeon(d.id));pins.append(pin);
    const button=document.createElement('button');button.type='button';
    button.dataset.bfMorganList=String(d.id);
    button.innerHTML='<strong></strong><small></small>';
    button.querySelector('strong').textContent=d.name;
    button.addEventListener('click',()=>openDungeon(d.id));items.append(button);
    controls.set(d.id,{pin,button});
  }
  function refresh(){
    for(const d of source.dungeons){
      const ok=unlocked(d);
      const selected=QUEST?.dungeonId===d.id;
      const {pin,button}=controls.get(d.id);
      const cleared=QUESTS.filter(q=>q.dungeonId===d.id &&
          (P.questClears?.[q.missionId]||0)>0).length;
      const total=QUESTS.filter(q=>q.dungeonId===d.id).length;
      const label=(ok?'AVAILABLE':'LOCKED')+' · '+cleared+'/'+total+' cleared';
      pin.classList.toggle('bf080-locked',!ok);
      button.classList.toggle('bf080-locked',!ok);
      pin.setAttribute('aria-pressed',String(selected));
      button.setAttribute('aria-pressed',String(selected));
      pin.setAttribute('aria-label',d.name+', '+label);
      button.setAttribute('aria-label',d.name+', '+label);
      button.querySelector('small').textContent=label;
    }
  }
  chooseRegion('mistral');
  new MutationObserver(refresh).observe(list,{childList:true});
  document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
  refresh();
  window.BFMorganMapV080=Object.freeze({
    entries:source.dungeons,refresh,openDungeon,chooseRegion,
    isUnlocked(id){const d=source.dungeons.find(q=>q.id===id);return d?unlocked(d):false},
    get selectedRegion(){return selectedRegion}
  });
})();
