/* BF_GLOBAL_PERSONAL_GEM_UI_V17000 */
(() => {
 'use strict';
 const api=window.BFGlobalCustomGemsV17000;
 if(window.BFGlobalPersonalGemUIV17000||!api||
   typeof P==='undefined'||P.version!==7||api.rates.replay!==1)return;
 const host=document.getElementById('questlist')||
   document.getElementById('bf16900-imp-fusion');
 if(!host)return;
 const panel=document.createElement('details');
 panel.id='bf17000-gem-rewards';
 panel.style.cssText='padding:10px;margin:10px 4px;border:1px solid #afacdf;'+
   'border-radius:9px;color:#fcf7ff;background:#343252;font:12px/1.5 system-ui';
 const header=document.createElement('summary');
 header.textContent='GEMS · PERSONAL OFFLINE REWARDS';
 header.style.cssText='cursor:pointer;min-height:40px;font-weight:800';
 const stat=document.createElement('p');
 const intro=document.createElement('p');
 intro.textContent='Optional personal rewards: 1,000 welcome Gems once, 100 Gems per '+
   'local calendar day, 25 for a regular quest first clear, 100 for a dungeon '+
   'finale first clear, and 1 for every successful cleared-quest replay. '+
   'Your original Global reward ledger remains separate.';
 const custom=document.createElement('button');
 custom.type='button';custom.textContent='ENABLE PERSONAL GEM REWARDS';
 const original=document.createElement('button');
 original.type='button';original.textContent='USE ORIGINAL REWARD MODE';
 const welcome=document.createElement('button');
 welcome.type='button';welcome.textContent='CLAIM 1,000 FIRST-LOGIN GEMS';
 const daily=document.createElement('button');
 daily.type='button';daily.textContent='CLAIM 100 DAILY GEMS';
 const history=document.createElement('p');
 const msg=document.createElement('p');
 const note=document.createElement('small');
 note.textContent='Local clock/date determines a daily claim; rolling the clock back '+
   'cannot claim a prior day again. The clock can still be changed offline. '+
   'Already-cleared quests are not paid retroactively, but later replays earn '+
   '1 Gem. All Gem claims and quest counts use the same v7 save transaction. '+
   'Back up your save before using an older APK; old parsers can drop newer '+
   'Gem metadata. Gem spending in summons is a separate future mechanic.';
 for(const button of [custom,original,welcome,daily]){
   button.style.cssText='padding:8px 10px;margin:3px;min-height:40px;'+
     'border-radius:6px;font-weight:700';
 }
 panel.append(header,stat,intro,custom,original,welcome,daily,history,msg,note);
 host.after(panel);
 let message='';
 function render(){
   const s=api.snapshot(),personal=s.mode==='custom';
   stat.textContent='Gem balance: '+s.balance.toLocaleString()+
     ' · Reward mode: '+(personal?'PERSONAL OFFLINE':'ORIGINAL / NO CUSTOM GEMS');
   custom.hidden=personal;original.hidden=!personal;
   welcome.disabled=!personal||s.welcomeClaimed;
   daily.disabled=!personal||!api.localDate()||
     s.lastDailyDate!==null&&api.localDate()<=s.lastDailyDate;
   history.textContent='First-clear Gem claims: '+s.firstPaid.length+
     ' · Replayed quest rewards: '+s.replaysPaid+
     ' · Daily claims: '+s.dailyClaims+
     ' · Last daily date: '+(s.lastDailyDate||'none')+
     ' · Quarantined prior clears: '+s.legacyClears.length;
   msg.textContent=message;
 }
 function click(fn,success,failure){
   const ok=fn();message=ok?success:failure;render();
 }
 custom.addEventListener('click',()=>click(()=>api.setMode('custom'),
  'Personal Gem rewards are active.','Could not save the Gem mode.'));
 original.addEventListener('click',()=>click(()=>api.setMode('original'),
  'Original mode active; personal Gem balance preserved.','Could not save mode.'));
 welcome.addEventListener('click',()=>click(api.claimWelcome,
  'Claimed 1,000 welcome Gems.','Already claimed, inactive, or save unavailable.'));
 daily.addEventListener('click',()=>click(api.claimDaily,
  'Claimed 100 daily Gems.','Already claimed today, inactive, or save unavailable.'));
 window.BFGlobalPersonalGemUIV17000=Object.freeze({refresh:render});
 render();
})();