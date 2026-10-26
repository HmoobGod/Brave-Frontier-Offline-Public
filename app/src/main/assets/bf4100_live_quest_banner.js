/* BF_GLOBAL_LIVE_QUEST_BANNER_V4100 */
(() => {
 'use strict';
 const story=window.BFGlobalStoryBattleV2000;
 if(window.BFGlobalLiveQuestBannerV4100||!story||
    !window.BFGlobalBattleBackdropV3800||
    !window.BFGlobalNextChapterIntroV4000||
    typeof P==='undefined'||P.version!==7||
    typeof QUESTS==='undefined'||QUESTS.length!==106||
    typeof S==='undefined')return;
 const battle=document.getElementById('battle');
 const hud=document.getElementById('bf2000-run');
 const mode=document.getElementById('mode');
 const questinfo=document.getElementById('questinfo');
 if(!battle||!hud||!mode||!questinfo)return;
 const arena=battle.parentElement;
 if(!arena||!arena.classList.contains('arena'))return;
 const css=document.createElement('style');css.id='bf4100-style';
 css.textContent=[
  '#bf4100-panel{margin:9px 0;padding:10px;border:1px solid #9e8766;',
  'border-radius:7px;background:#203248;color:#f3e6cc;font:12px/1.5 system-ui,sans-serif}',
  '#bf4100-panel label{display:flex;gap:9px;align-items:center;min-height:44px;font-weight:800}',
  '#bf4100-panel input{width:18px;height:18px;accent-color:#bfab7c}',
  '#bf4100-panel small{display:block;color:#ccd8e5;margin-top:3px}',
  '#bf4100-banner{position:absolute;left:50%;top:6px;transform:translateX(-50%);',
  'z-index:3;width:max-content;max-width:calc(100% - 16px);',
  'padding:5px 12px;border:1px solid #be9e65;border-radius:7px;',
  'background:rgba(14,29,43,.89);color:#fff1d3;',
  'font:800 12px/1.45 system-ui,sans-serif;text-align:center;',
  'overflow-wrap:anywhere;pointer-events:none;box-sizing:border-box}',
  '#bf4100-banner[hidden]{display:none!important}'
 ].join('');document.head.append(css);
 const panel=document.createElement('section');panel.id='bf4100-panel';
 const label=document.createElement('label');label.htmlFor='bf4100-toggle';
 label.textContent='OPTIONAL MISSION NAME IN BATTLE';
 const toggle=document.createElement('input');toggle.id='bf4100-toggle';
 toggle.type='checkbox';
 toggle.setAttribute('aria-label','Show original quest name and demo wave in battlefield');
 label.prepend(toggle);
 const note=document.createElement('small');
 note.textContent='Uses original 2022 Global quest and dungeon names. Wave status and all active combat remain DEMO. Display only; off by default.';
 panel.append(label,note);hud.append(panel);
 const banner=document.createElement('div');
 banner.id='bf4100-banner';
 banner.hidden=true;
 banner.setAttribute('aria-label','Archived quest and demo wave status');
 banner.setAttribute('aria-live','off');
 arena.append(banner);
 let enabled=false,last='';
 function snapshot(){
   const q=typeof QUEST==='undefined'?null:QUEST;
   const s=story.snapshot();
   const available=!!q&&!!s&&s.archive&&mode.value==='archive'&&
     questUnlocked(q)&&s.missionId===q.missionId&&
     typeof s.name==='string'&&s.name.length>0&&
     typeof s.dungeon==='string'&&s.dungeon.length>0;
   return Object.freeze({enabled,available,applied:enabled&&available,
     missionId:available?q.missionId:null,
     name:available?s.name:null,dungeon:available?s.dungeon:null,
     wave:available?s.current:null,total:available?s.total:null,
     state:available?(s.won?'VICTORY':s.lost?'DEFEAT':s.busy?'TURN IN PROGRESS':'BATTLE'):null});
 }
 function refresh(){
   const s=snapshot(),key=JSON.stringify(s);
   if(key===last)return s;
   last=key;
   panel.hidden=!s.available;
   toggle.disabled=!s.available;
   toggle.checked=enabled;
   banner.hidden=!s.applied;
   banner.textContent=s.applied?s.name+' · '+s.dungeon+' · WAVE '+
     s.wave+'/'+s.total+' · '+s.state:'';
   return s;
 }
 function setEnabled(value){
   if(typeof value!=='boolean'||value&&!snapshot().available)return false;
   enabled=value;last='';refresh();return true;
 }
 toggle.addEventListener('change',()=>setEnabled(toggle.checked));
 mode.addEventListener('change',refresh);
 new MutationObserver(refresh).observe(questinfo,{subtree:true,childList:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},900);
 window.BFGlobalLiveQuestBannerV4100=Object.freeze({snapshot,refresh,setEnabled});
 refresh();
})();
