"""v1.01 regression: 106 archived quests, unlock-respecting Continue Story."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
js=(A/'bf101_story_continue.js').read_text('utf-8')
assert js.count('/* BF_GRAND_GAIA_CONTINUE_V101 */')==1
assert 'localStorage' not in js and 'saveProgress(' not in js
assert 'questUnlocked(q)' in js and 'BFQuestAreas.choose(q)' in js
java=(ROOT/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
assert java.index('readPackagedText("bf100_grand_gaia_campaign.js")') < java.index('readPackagedText("bf101_story_continue.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
   const db={};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
      getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
      removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
      get length(){return Object.keys(db).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf-8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7
 assert page.evaluate('QUESTS.length')==106
 assert page.evaluate('BFGrandGaiaContinueV101.snapshot()')=={
    'total':106,'done':0,'mistral':0,'morgan':0,'stlamia':0,'nextMission':1}
 assert page.locator('#bf101-continue').count()==1
 before=page.evaluate("""()=>({p:JSON.stringify(P),
     save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('BFGrandGaiaContinueV101.refresh()')
 after=page.evaluate("""()=>({p:JSON.stringify(P),
     save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'passive refresh must not change save'
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 # A live Auto player turn can have busy=false; a bounded repeat can
 # still own the victory screen. Neither state permits story rerouting.
 owned=page.evaluate("""()=>{
   const button=document.getElementById('bf101-continue'),
     saved=localStorage.getItem('bf_global_offline_demo_v7'),
     progress=JSON.stringify(P),quest=QUEST.missionId,
     original={mode:S.mode,auto:S.auto,busy:S.busy,over:S.over},
     oldRepeat=window.BFGlobalQoLQuestRepeatV9800;
   try{
     S.mode='archive';S.auto=true;S.busy=false;S.over=false;
     BFGrandGaiaContinueV101.refresh();
     const autoBlocked=button.disabled &&
       document.getElementById('bf101-next').textContent.includes('AUTO BATTLE / REPEAT ACTIVE');
     button.dispatchEvent(new MouseEvent('click',{bubbles:true}));
     const autoNoRoute=QUEST.missionId===quest;
     S.auto=false;S.over=true;
     window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>({active:true})};
     BFGrandGaiaContinueV101.refresh();
     const repeatBlocked=button.disabled &&
       document.getElementById('bf101-next').textContent.includes('AUTO BATTLE / REPEAT ACTIVE');
     button.dispatchEvent(new MouseEvent('click',{bubbles:true}));
     const repeatNoRoute=QUEST.missionId===quest;
     // Broken optional result providers must not silently bypass a live repeat.
     window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>{throw Error('bad repeat status')}};
     BFGrandGaiaContinueV101.refresh();
     const brokenBlocked=button.disabled;
     return {autoBlocked,autoNoRoute,repeatBlocked,repeatNoRoute,brokenBlocked,
       progressSame:JSON.stringify(P)===progress,
       saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved};
   }finally{
     Object.assign(S,original);
     if(oldRepeat===undefined)delete window.BFGlobalQoLQuestRepeatV9800;
     else window.BFGlobalQoLQuestRepeatV9800=oldRepeat;
     BFGrandGaiaContinueV101.refresh();
   }
 }""")
 assert owned=={'autoBlocked':True,'autoNoRoute':True,
    'repeatBlocked':True,'repeatNoRoute':True,'brokenBlocked':True,
    'progressSame':True,'saveSame':True},owned
 assert page.locator('#bf101-continue').is_enabled()
 # v341: a completed archived victory must have a precise committed v7
 # clear receipt before the global 106-mission shortcut can route onward.
 # The existing results module is loaded later than v101; simulated providers
 # here exercise the same read-only API without modifying persisted saves.
 receipt=page.evaluate("""()=>{
   const provider=window.BFGlobalBattleResultsV3000,
     button=document.getElementById('bf101-continue'),
     old={mode:S.mode,over:S.over,busy:S.busy,phase:S.phase,auto:S.auto},
     q=QUEST,oldClear=P.questClears[q.missionId],
     originalEnabled=saveEnabled,originalPending=saveRecoveryPending,
     beforeP=JSON.stringify(P),beforeSave=localStorage.getItem('bf_global_offline_demo_v7');
   const result={};
   try{
     S.mode='archive';S.over=true;S.busy=false;
     S.phase='Victory';S.auto=false;
     saveEnabled=true;saveRecoveryPending=false;
     P.questClears[q.missionId]=1;
     delete window.BFGlobalBattleResultsV3000;
     BFGrandGaiaContinueV101.refresh();
     result.legacy=BFGrandGaiaContinueV101.nextMission===2&&!button.disabled;
     window.BFGlobalBattleResultsV3000={committedClearCount:()=>0};
     BFGrandGaiaContinueV101.refresh();
     result.stale=button.disabled&&BFGrandGaiaContinueV101.nextMission===null&&
       document.getElementById('bf101-next').textContent.includes('VICTORY NOT SAVED');
     button.dispatchEvent(new MouseEvent('click',{bubbles:true}));
     result.staleNoRoute=QUEST.missionId===q.missionId;
     window.BFGlobalBattleResultsV3000={committedClearCount:()=>NaN};
     BFGrandGaiaContinueV101.refresh();
     result.corrupt=button.disabled;
     window.BFGlobalBattleResultsV3000={committedClearCount:()=>{throw Error('receipt unavailable')}};
     BFGrandGaiaContinueV101.refresh();
     result.throws=button.disabled;
     window.BFGlobalBattleResultsV3000={
       get committedClearCount(){throw Error('broken receipt getter')}};
     BFGrandGaiaContinueV101.refresh();
     result.getterThrows=button.disabled;
     window.BFGlobalBattleResultsV3000={};
     BFGrandGaiaContinueV101.refresh();
     result.missingApi=button.disabled;
     window.BFGlobalBattleResultsV3000={committedClearCount:()=>1};
     BFGrandGaiaContinueV101.refresh();
     result.committed=BFGrandGaiaContinueV101.nextMission===2&&!button.disabled;
     return {...result,saveSame:localStorage.getItem('bf_global_offline_demo_v7')===beforeSave,
       originalQuest:QUEST.missionId===q.missionId};
   }finally{
     Object.assign(S,old);
     saveEnabled=originalEnabled;saveRecoveryPending=originalPending;
     if(oldClear===undefined)delete P.questClears[q.missionId];
     else P.questClears[q.missionId]=oldClear;
     if(provider===undefined)delete window.BFGlobalBattleResultsV3000;
     else window.BFGlobalBattleResultsV3000=provider;
     BFGrandGaiaContinueV101.refresh();
   }
 }""")
 assert receipt=={'legacy':True,'stale':True,'staleNoRoute':True,
    'corrupt':True,'throws':True,'getterThrows':True,'missingApi':True,'committed':True,
    'saveSame':True,'originalQuest':True},receipt
 # The button must fail closed with the same canonical full-catalog policy
 # as the campaign resolver. Keep test-only corrupt records atomic to avoid
 # exposing an invalid ledger to the live browser renderer between calls.
 bad=page.evaluate("""()=>{const id=QUESTS[QUESTS.length-1].missionId;
   const prior=P.questClears[id],mission=QUEST.missionId;
   const before=localStorage.getItem('bf_global_offline_demo_v7');
   try{
     P.questClears[id]=-1;
     BFGrandGaiaContinueV101.refresh();
     const global=BFGrandGaiaCampaignV100.nextPlayable();
     const next=BFGrandGaiaContinueV101.nextMission;
     const disabled=document.getElementById('bf101-continue').disabled;
     document.getElementById('bf101-continue').click();
     return {global,next,disabled,missionUnchanged:QUEST.missionId===mission,
       saveUnchanged:localStorage.getItem('bf_global_offline_demo_v7')===before};
   }finally{
     if(prior===undefined)delete P.questClears[id];
     else P.questClears[id]=prior;
   }
 }""")
 assert bad=={'global':None,'next':None,'disabled':True,
   'missionUnchanged':True,'saveUnchanged':True},bad
 assert page.evaluate('BFGrandGaiaContinueV101.refresh().nextMission')==1
 assert page.locator('#bf101-continue').is_enabled()
 page.locator('#bf101-continue').click()
 assert page.evaluate('QUEST.missionId')==1
 assert page.locator('.bf-mistral-map').is_visible()
 page.evaluate('()=>{P.questClears[85]=1;renderQuestList()}')
 assert page.evaluate('BFGrandGaiaContinueV101.nextMission')==1
 page.evaluate('()=>{for(const q of QUESTS.slice(0,34))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGrandGaiaContinueV101.nextMission')==200
 assert page.evaluate('BFGrandGaiaCampaignV100.nextPlayable().missionId')==200
 page.locator('#bf101-continue').click()
 assert page.evaluate('QUEST.missionId')==200
 assert page.locator('#bf080-morgan-map').is_visible()
 page.evaluate('()=>{for(const q of QUESTS.slice(0,70))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGrandGaiaContinueV101.nextMission')==300
 assert page.evaluate('BFGrandGaiaCampaignV100.nextPlayable().missionId')==300
 page.locator('#bf101-continue').click()
 assert page.evaluate('QUEST.missionId')==300
 assert page.locator('#bf090-stlamia-map').is_visible()
 page.locator('.bf080-region-tabs button').nth(1).click()
 assert page.locator('#bf080-morgan-map').is_visible()
 assert not page.locator('#bf090-stlamia-map').is_visible()
 page.evaluate('()=>{for(const q of QUESTS)P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGrandGaiaContinueV101.snapshot().done')==106
 assert page.evaluate('BFGrandGaiaContinueV101.nextMission') is None
 assert page.locator('#bf101-continue').is_disabled()
 assert '106 archived story missions cleared' in page.locator('#bf101-next').text_content()
 assert page.locator('#bf101-story-continue [aria-valuenow]').get_attribute('aria-valuenow')=='106'
 # Start a separate, clean synthetic player profile for the quota case.
 # Rewinding a previously cleared 106-mission profile to zero in memory is
 # not a valid save migration and can correctly fail the v7 save guard.
 page.close()
 page=browser.new_page(viewport={'width':390,'height':844})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
   const db={};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
      getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
      removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
      get length(){return Object.keys(db).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf-8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.evaluate('P.questClears[1]') is None
 assert page.evaluate('QUEST.missionId')==1
 persisted=page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 page.evaluate("""()=>{window.__continueOriginalSet=localStorage.setItem.bind(localStorage);
   window.__continueDenySave=true;
   localStorage.setItem=(key,value)=>{
     if(__continueDenySave&&key==='bf_global_offline_demo_v7')
       throw new DOMException('Synthetic storage quota','QuotaExceededError');
     return __continueOriginalSet(key,value);
   };
   finish(true);
   BFGrandGaiaContinueV101.refresh();
 }""")
 assert page.evaluate('P.questClears[1]')>=1
 assert page.evaluate('BFGrandGaiaContinueV101.snapshot().nextMission') is None
 assert page.evaluate('BFGrandGaiaContinueV101.nextMission') is None
 assert page.locator('#bf101-continue').is_disabled()
 assert 'VICTORY NOT SAVED' in page.locator('#bf101-next').inner_text()
 assert page.evaluate('QUEST.missionId')==1
 assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==persisted
 assert page.evaluate("()=>{__continueDenySave=false;return saveProgress()}") is True
 assert page.evaluate('BFGrandGaiaContinueV101.refresh().nextMission')==2
 assert page.locator('#bf101-continue').is_enabled()
 page.locator('#bf101-continue').click()
 assert page.evaluate('QUEST.missionId')==2
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v1.01 Continue Story across 106 missions, 3 regions, save v7')
