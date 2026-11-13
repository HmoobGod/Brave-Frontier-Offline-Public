/* BF_HOME_BATTLE_READINESS_V420 */
(() => {
  'use strict';
  if (window.BFHomeBattleReadinessV420) return;
  // A read-only Home panel. Never choose a quest, save, start combat or Auto.
  const home=document.getElementById('bf-home');
  const story=home?.querySelector('.bf-scene-story');
  const explore=home?.querySelector('.bf-scene-explore');
  const campaign=window.BFGrandGaiaCampaignV100;
  const archive=window.BFOriginalGlobalQuestEnergyV14300;
  if(!story || !explore || story.parentElement!==explore.parentElement ||
     !window.BF_homeNav || !campaign ||
     !archive || typeof campaign.nextPlayable!=='function' ||
     typeof campaign.summary!=='function' ||
     typeof archive.lookup!=='function' ||
     typeof P==='undefined' || P?.version!==7 ||
     typeof QUESTS==='undefined' || !Array.isArray(QUESTS) ||
     QUESTS.length!==106) return;

  const style=document.createElement('style');
  style.id='bf420-home-readiness-style';
  style.textContent=[
    '#bf420-home-readiness{box-sizing:border-box;max-width:100%;margin:10px 0;',
    'padding:11px 10px;border:1px solid #ba9656;border-radius:7px;',
    'background:linear-gradient(145deg,#25364b,#151e2f);color:#f6e5c2;',
    'font:12px/1.45 Arial,sans-serif;overflow-wrap:anywhere}',
    '#bf420-home-readiness h3{font:800 15px Georgia,serif;margin:0 0 7px;',
    'color:#ffe1aa}',
    '#bf420-home-readiness .bf420-row{margin:6px 0;display:flex;',
    'gap:6px;justify-content:space-between;flex-wrap:wrap}',
    '#bf420-home-readiness .bf420-row strong{color:#f9e4b5}',
    '#bf420-home-readiness .bf420-actions{display:grid;',
    'grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin:10px 0 0}',
    '#bf420-home-readiness button{box-sizing:border-box;min-height:44px;',
    'min-width:0;max-width:100%;padding:8px 6px;white-space:normal;',
    'color:#ffedc5;background:#43566d;border:1px solid #c9a973;',
    'border-radius:5px;font:800 11px Arial,sans-serif;cursor:pointer}',
    '#bf420-home-readiness button:disabled{opacity:.5;cursor:not-allowed}',
    '#bf420-home-readiness button:focus-visible{outline:3px solid #a7e2ff}',
    '#bf420-home-readiness .bf420-note{display:block;font:10px/1.5 Arial,sans-serif;',
    'color:#cedbea;margin:7px 0 0}',
    '@media(max-width:340px){#bf420-home-readiness .bf420-actions{',
    'grid-template-columns:1fr}}'
  ].join('');
  const card=document.createElement('section');
  card.id='bf420-home-readiness';
  card.setAttribute('aria-label','Source-checked Home mission and squad readiness');
  const heading=document.createElement('h3');
  heading.textContent='NEXT ADVENTURE · MANUAL PREVIEW';
  const mission=document.createElement('div');
  mission.id='bf420-home-mission';
  mission.className='bf420-row';
  mission.setAttribute('role','status');
  mission.setAttribute('aria-live','polite');
  const party=document.createElement('div');
  party.id='bf420-home-party';
  party.className='bf420-row';
  const actions=document.createElement('div');
  actions.className='bf420-actions';
  const questButton=document.createElement('button');
  questButton.id='bf420-home-quest';
  questButton.type='button';
  questButton.textContent='VIEW QUEST · MANUAL';
  const unitsButton=document.createElement('button');
  unitsButton.id='bf420-home-units';
  unitsButton.type='button';
  unitsButton.textContent='CHECK SQUAD';
  actions.append(questButton,unitsButton);
  const note=document.createElement('small');
  note.className='bf420-note';
  note.textContent='2022 archived mission and Energy references only. '+
    'Enemy formations, rewards and battle logic remain an offline DEMO. '+
    'No automatic quest selection, combat or stamina spending.';
  card.append(heading,mission,party,actions,note);
  // Home first: do not push the original playable Quest/Summon artwork
  // below the viewport. Append this optional preview AFTER Adventure.
  explore.insertAdjacentElement('afterend',card);
  document.head.append(style);

  function snapshot(){
    try{
      if(archive.source?.year!==2022 ||
         archive.source?.recordCount!==106 ||
         archive.source?.sourceSha256!==
           'a1b36659dfc80bc6e1e0e244ba52b3c6d423b239cf684439a5488bf679764a66' ||
         archive.source?.staminaEnforced!==false ||
         !Array.isArray(P.squad) || P.squad.length>6 ||
         QUESTS.length!==106) return null;
      const filled=P.squad.filter(id=>Number.isSafeInteger(id) &&
        id>=0 && typeof effectiveUnit==='function' && !!effectiveUnit(id)).length;
      const progress=campaign.summary();
      if(progress?.total!==106 || !Number.isSafeInteger(progress.cleared) ||
         progress.cleared<0 || progress.cleared>106)return null;
      const next=campaign.nextPlayable();
      if(next===null && progress.cleared===106)
        return Object.freeze({complete:true,filled,missionId:null,waves:null,energy:null});
      if(!next || !Number.isSafeInteger(next.missionId) ||
         !Number.isSafeInteger(next.dungeonId) ||
         !Number.isSafeInteger(next.battles) || next.battles<1)return null;
      const matches=QUESTS.filter(q=>q?.missionId===next.missionId);
      if(matches.length!==1)return null;
      const q=matches[0],row=archive.lookup(next.missionId);
      if(!Array.isArray(row) || row.length!==8 ||
         row.some(v=>!Number.isSafeInteger(v)||v<0) ||
         ![q.missionId,q.dungeonId,q.requires,q.battles,
           q.energy,q.exp,q.zel,q.karma].every((v,i)=>v===row[i]) ||
         q.dungeonId!==next.dungeonId || q.battles!==next.battles ||
         typeof questUnlocked!=='function' || !questUnlocked(q))
        return null;
      const fromSource=window.BFGlobalQuestText?.sourceFor?.(q);
      const name=typeof fromSource?.mission?.name==='string' &&
        fromSource.mission.name.trim()?fromSource.mission.name.trim():'Mission '+q.missionId;
      return Object.freeze({complete:false,missionId:q.missionId,
        waves:row[3],energy:row[4],name:name.slice(0,90),filled});
    }catch(_){return null;}
  }
  function available(){
    if(window.BF_homeNav?.current!=='home'||S?.busy===true||S?.auto===true)return false;
    const repeat=window.BFGlobalQoLQuestRepeatV9800;
    if(repeat){
      if(typeof repeat.statusSnapshot!=='function')return false;
      try{if(repeat.statusSnapshot()?.active)return false;}
      catch(_){return false;}
    }
    return true;
  }
  function refresh(){
    const s=snapshot(),can=available();
    mission.replaceChildren();
    if(!s)mission.textContent='Archived mission preview unavailable · inspect Quests.';
    else if(s.complete)mission.textContent='All 106 archived missions cleared (DEMO battles).';
    else mission.textContent='NEXT · '+s.name+' · Mission '+s.missionId+
      ' · 2022 original '+s.waves+' waves · Energy '+s.energy+' (reference only)';
    party.textContent=s?'CURRENT SQUAD · '+s.filled+'/6 filled slots':
      'CURRENT SQUAD · source state unavailable';
    questButton.disabled=!s || s.complete || !can;
    unitsButton.disabled=!s || !can;
    return s;
  }
  function go(route){
    const s=refresh();
    if(!s || !available() || (route==='quest'&&s.complete))return false;
    return window.BF_homeNav?.go?.(route)===true;
  }
  questButton.addEventListener('click',()=>{if(!questButton.disabled)go('quest');});
  unitsButton.addEventListener('click',()=>{if(!unitsButton.disabled)go('units');});
  window.addEventListener('bf-route-change',event=>{
    if(event?.detail?.route==='home')refresh();
  });
  window.BFHomeBattleReadinessV420=Object.freeze({snapshot,refresh});
  refresh();
})();
