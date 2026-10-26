/* BF_GLOBAL_NEXT_CHAPTER_INTRO_V4000 */
(() => {
 'use strict';
 const results=window.BFGlobalBattleResultsV3000;
 const events=window.BFGlobalOriginalEventsV2200;
 const story=window.BFGlobalStoryBattleV2000;
 if(window.BFGlobalNextChapterIntroV4000||!results||!events||!story||
    !window.BFGlobalStoryBattleHandoffV3900||
    typeof P==='undefined'||P.version!==7||
    typeof QUESTS==='undefined'||QUESTS.length!==106||
    typeof S==='undefined')return;
 const resultPanel=document.getElementById('bf3000-result');
 const resultActions=document.getElementById('bf3000-actions');
 const output=document.getElementById('results');
 const questinfo=document.getElementById('questinfo');
 const reader=document.getElementById('bf2200-reader');
 if(!resultPanel||!resultActions||!output||!questinfo||!reader)return;
 const css=document.createElement('style');css.id='bf4000-style';
 css.textContent=[
  '#bf4000-next-intro{min-height:44px;padding:8px 12px;',
  'border:1px solid #ddc08e;border-radius:5px;background:#38576a;',
  'color:#fff;font-weight:800}',
  '#bf4000-next-intro:disabled{opacity:.42}',
  '#bf4000-note{display:block;margin-top:5px;color:#d1dded;',
  'font:11px/1.5 system-ui,sans-serif}'
 ].join('');document.head.append(css);
 const button=document.createElement('button');
 button.type='button';button.id='bf4000-next-intro';
 button.textContent='NEXT CHAPTER · ORIGINAL INTRO ›';
 button.setAttribute('aria-label','Continue to next unlocked mission and read its archived original dungeon introduction');
 resultActions.append(button);
 const note=document.createElement('small');note.id='bf4000-note';
 note.textContent='Optional link between DEMO victory and recovered 2022 original story. Does not skip missions, auto-play combat, grant rewards or create dialogue.';
 resultActions.after(note);
 function snapshot(){
   const r=results.snapshot();
   const target=r?.nextId?QUESTS.find(q=>q.missionId===r.nextId):null;
   const source=target?events.lookup('dungeon',target.dungeonId):null;
   const active=r?.done&&r.victory&&r.archive&&!S.busy&&
     typeof QUEST!=='undefined'&&QUEST?.missionId===r.missionId&&
     target&&questUnlocked(target)&&source&&source.lines.length>0;
   return Object.freeze({
     available:!!active,missionId:r?.missionId||null,
     nextId:active?target.missionId:null,
     dungeonId:active?target.dungeonId:null,
     source:active?source.source:null
   });
 }
 function refresh(){
   const s=snapshot();
   button.hidden=!s.available;
   button.disabled=!s.available;
   note.hidden=!s.available;
   return s;
 }
 function continueStory(){
   const before=snapshot();
   if(!before.available)return false;
   if(!results.advance()||typeof QUEST==='undefined'||
      QUEST.missionId!==before.nextId)return false;
   const ok=events.read('dungeon',before.dungeonId);
   if(ok){
     reader.scrollIntoView({block:'start',behavior:'smooth'});
   }
   refresh();
   return !!ok&&events.snapshot().chosen==='dungeon:'+before.dungeonId;
 }
 button.addEventListener('click',continueStory);
 new MutationObserver(refresh).observe(output,{subtree:true,childList:true,characterData:true});
 new MutationObserver(refresh).observe(questinfo,{subtree:true,childList:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},950);
 window.BFGlobalNextChapterIntroV4000=Object.freeze({snapshot,refresh,continueStory});
 refresh();
})();
