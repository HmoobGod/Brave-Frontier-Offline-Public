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
 # v358: native loader inserts v143 after v101; dynamically read the 2022
 # reference only once the source-qualified lookup is present.
 assert '2022 source reference:' not in page.locator('#bf101-next').text_content()
 page.add_script_tag(path=str(A/'bf14300_original_quest_energy.js'))
 # Native v143 boot must refresh the already-mounted Continue Story shortcut
 # without requiring a manual tab or button click.
 page.wait_for_function("()=>document.getElementById('bf101-next')?.textContent.includes('2022 source reference:')")
 preview=page.locator('#bf101-next').text_content()
 assert '2022 source reference: 3 waves · Energy 0 · EXP 5 · Zel 500 · Karma 100' in preview,preview
 assert 'DEMO credits EXP/Zel/Karma on clear' in preview
 assert 'stamina not enforced' in preview
 checked=page.evaluate("""()=>{
   const original=window.BFOriginalGlobalQuestEnergyV14300,
     originalSave=localStorage.getItem('bf_global_offline_demo_v7'),
     originalP=JSON.stringify(P),before=QUEST.missionId;
   try{
     window.BFOriginalGlobalQuestEnergyV14300={
       source:original.source,
       lookup:id=>{const row=[...original.lookup(id)];row[5]+=1;return row;}
     };
     BFGrandGaiaContinueV101.refresh();
     const forged=!document.getElementById('bf101-next').textContent.includes('2022 source reference:');
     window.BFOriginalGlobalQuestEnergyV14300={
       source:original.source,lookup:()=>{throw Error('read failed');}
     };
     BFGrandGaiaContinueV101.refresh();
     const throwing=!document.getElementById('bf101-next').textContent.includes('2022 source reference:');
     return {forged,throwing,saveSame:localStorage.getItem('bf_global_offline_demo_v7')===originalSave,
       playerSame:JSON.stringify(P)===originalP,questSame:QUEST.missionId===before};
   }finally{
     window.BFOriginalGlobalQuestEnergyV14300=original;
     BFGrandGaiaContinueV101.refresh();
   }
 }""")
 assert checked=={'forged':True,'throwing':True,'saveSame':True,'playerSame':True,'questSame':True},checked
 before=page.evaluate("""()=>({p:JSON.stringify(P),
     save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('BFGrandGaiaContinueV101.refresh()')
 after=page.evaluate("""()=>({p:JSON.stringify(P),
     save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'passive refresh must not change save'
 # v419: direct Home -> next original mission must be an explicit MANUAL
 # action, 44px accessible on 320px phones, never an Auto/save shortcut.
 page.set_viewport_size({'width':320,'height':740})
 home_next=page.locator('#bf101-home-manual-continue')
 assert page.evaluate('BF_homeNav.current')=='home'
 assert home_next.count()==1 and home_next.is_visible() and home_next.is_enabled()
 home_metrics=home_next.evaluate("""el=>({
   height:el.getBoundingClientRect().height,
   left:el.getBoundingClientRect().left,
   right:el.getBoundingClientRect().right,
   width:innerWidth
 })""")
 assert home_metrics['height']>=44 and home_metrics['left']>=0,home_metrics
 assert home_metrics['right']<=home_metrics['width']+1,home_metrics
 blocked_home=page.evaluate("""()=>{
   const btn=document.getElementById('bf101-home-manual-continue');
   const old={busy:S.busy,auto:S.auto};
   const mission=QUEST.missionId,save=localStorage.getItem('bf_global_offline_demo_v7');
   try{
     S.busy=true;BFGrandGaiaContinueV101.refresh();
     const busy=btn.disabled;
     btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));
     const noBusyRoute=BF_homeNav.current==='home';
     S.busy=false;S.auto=true;BFGrandGaiaContinueV101.refresh();
     const auto=btn.disabled;
     btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));
     return {busy,noBusyRoute,auto,noAutoRoute:BF_homeNav.current==='home',
       sameMission:QUEST.missionId===mission,
       sameSave:localStorage.getItem('bf_global_offline_demo_v7')===save};
   }finally{Object.assign(S,old);BFGrandGaiaContinueV101.refresh();}
 }""")
 assert all(blocked_home.values()),blocked_home
 before_home=page.evaluate("""()=>({
    p:JSON.stringify(P),stored:localStorage.getItem('bf_global_offline_demo_v7')
 })""")
 home_next.click()
 after_home=page.evaluate("""()=>({
   route:BF_homeNav.current,mission:QUEST.missionId,auto:S.auto,
   checked:document.getElementById('auto').checked,
   p:JSON.stringify(P),stored:localStorage.getItem('bf_global_offline_demo_v7')
 })""")
 assert after_home['route']=='quest' and after_home['mission']==1,after_home
 assert not after_home['auto'] and not after_home['checked'],after_home
 assert after_home['p']==before_home['p'] and after_home['stored']==before_home['stored'],after_home
 page.evaluate("BF_homeNav.go('home')")
 assert home_next.is_enabled(),'Home shortcut must re-enable on native route event'
 page.set_viewport_size({'width':390,'height':844})
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
 # Real player click: only source-qualified next story mission + native Auto.
 # Isolated browser ensures the pre-existing 106-mission and save-recovery
 # regression suites above remain unchanged, including default manual play.
 auto_page=browser.new_page(viewport={'width':390,'height':844})
 auto_page.on('pageerror',lambda e:errors.append(str(e)))
 auto_page.evaluate("""()=>{const db={};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
     removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
     get length(){return Object.keys(db).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 auto_page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 auto_page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
     'bf100_grand_gaia_campaign.js','bf101_story_continue.js'):
  auto_page.add_script_tag(path=str(A/name))
 auto_page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 btn=auto_page.locator('#bf101-continue-auto')
 assert btn.count()==1
 assert btn.is_disabled(),'unknown original economy must block native Auto'
 auto_page.add_script_tag(path=str(A/'bf14300_original_quest_energy.js'))
 assert auto_page.evaluate('BFGrandGaiaContinueV101.canContinueAuto()') is True
 assert btn.is_enabled()
 # The original story navigation stays manual by default.
 assert auto_page.locator('#bf101-continue').is_enabled()
 guard=auto_page.evaluate("""()=>{const base=window.BFGrandGaiaCampaignV100,
   previousRepeat=window.BFGlobalQoLQuestRepeatV9800,
   before=QUEST.missionId,checks={};
   try{
     window.BFGrandGaiaCampaignV100={
       ...base,sourceEconomyReadiness:()=>null};
     BFGrandGaiaContinueV101.refresh();
     checks.unknownEconomy=!BFGrandGaiaContinueV101.canContinueAuto()&&
       document.getElementById('bf101-continue-auto').disabled;
     window.BFGrandGaiaCampaignV100={
       ...base,waveReadiness:id=>({...base.waveReadiness(id),verifiedWaveCount:999})};
     checks.badWaves=!BFGrandGaiaContinueV101.canContinueAuto();
     window.BFGrandGaiaCampaignV100=base;
     window.BFGlobalQoLQuestRepeatV9800={
       statusSnapshot:()=>({active:true})};
     checks.repeat=!BFGrandGaiaContinueV101.canContinueAuto();
     window.BFGlobalQoLQuestRepeatV9800=previousRepeat;
     const auto=document.getElementById('auto');
     const oldPending=saveRecoveryPending;
     saveRecoveryPending=true;
     checks.pendingSave=!BFGrandGaiaContinueV101.canContinueAuto();
     saveRecoveryPending=oldPending;
     if(S.party[0]){
       const oldOrder=S.party[0].action;
       S.party[0].action={kind:'attack',target:0};
       checks.queuedOrder=!BFGrandGaiaContinueV101.canContinueAuto();
       S.party[0].action=oldOrder;
     }else checks.queuedOrder=false;
     auto.disabled=true;
     checks.disabled=!BFGrandGaiaContinueV101.canContinueAuto();
     auto.disabled=false;
     auto.checked=true;S.auto=true;
     checks.alreadyAuto=!BFGrandGaiaContinueV101.canContinueAuto();
     auto.checked=false;S.auto=false;
     return {checks,unchanged:QUEST.missionId===before};
   }finally{
     window.BFGrandGaiaCampaignV100=base;
     if(previousRepeat===undefined)delete window.BFGlobalQoLQuestRepeatV9800;
     else window.BFGlobalQoLQuestRepeatV9800=previousRepeat;
     S.auto=false;document.getElementById('auto').checked=false;
     document.getElementById('auto').disabled=false;
     BFGrandGaiaContinueV101.refresh();
   }
 }""")
 assert guard=={'checks':{'unknownEconomy':True,'badWaves':True,
   'repeat':True,'pendingSave':True,'queuedOrder':True,
   'disabled':True,'alreadyAuto':True},'unchanged':True},guard
 # Use a REAL button click, not a direct helper invocation.
 before_auto=auto_page.evaluate("""()=>({mission:QUEST.missionId,
   version:P.version,clears:JSON.stringify(P.questClears),
   saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert btn.is_enabled()
 btn.click()
 started=auto_page.evaluate("""()=>({
   mission:QUEST.missionId,mode:S.mode,over:S.over,busy:S.busy,
   auto:S.auto,checked:document.getElementById('auto').checked,
   waves:S.totalWaves,version:P.version,clears:JSON.stringify(P.questClears),
   stored:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert started['mission']==1 and started['mode']=='archive',started
 assert started['auto'] and started['checked'] and not started['over'],started
 assert not started['busy'] and started['waves']==auto_page.evaluate('QUESTS[0].battles'),started
 assert started['clears']==before_auto['clears'] and started['version']==7,started
 # Starting native Auto does not itself grant a clear or schedule the next quest.
 assert auto_page.evaluate('BFGrandGaiaContinueV101.canContinueAuto()') is False
 # Native finish() disables its Auto checkbox on an ended battle; that is
 # EXPECTED after a stored Victory, not a reason to block next-story routing.
 auto_page.evaluate('finish(true); BFGrandGaiaContinueV101.refresh()')
 victory=auto_page.evaluate("""()=>({
   done:S.over,phase:S.phase,autoDisabled:document.getElementById('auto').disabled,
   autoChecked:document.getElementById('auto').checked,
   saved:localStorage.getItem('bf_global_offline_demo_v7'),
   clears:JSON.stringify(P.questClears),next:BFGrandGaiaContinueV101.nextMission,
   eligible:BFGrandGaiaContinueV101.canContinueAuto()})""")
 assert victory['done'] and victory['phase']=='Victory',victory
 assert victory['saved'] and victory['autoDisabled'] and not victory['autoChecked'],victory
 assert victory['next']==2 and victory['eligible'],victory
 assert btn.is_enabled(),'a stored victory must enable next story + native Auto'
 # A real touch/click starts mission 2 once. Native quest selection may
 # persist lastMission; it must not award a second clear or rewrite clear counts.
 committed=auto_page.evaluate("""()=>({
   memory:JSON.stringify(P.questClears),
   stored:JSON.stringify(JSON.parse(localStorage.getItem('bf_global_offline_demo_v7')).questClears),
   saveVersion:JSON.parse(localStorage.getItem('bf_global_offline_demo_v7')).version})""")
 assert committed['saveVersion']==7,committed
 btn.click()
 next_started=auto_page.evaluate("""()=>({
   mission:QUEST.missionId,over:S.over,auto:S.auto,
   checked:document.getElementById('auto').checked,
   waves:S.totalWaves,clears:JSON.stringify(P.questClears),
   stored:JSON.stringify(JSON.parse(localStorage.getItem('bf_global_offline_demo_v7')).questClears),
   saveVersion:JSON.parse(localStorage.getItem('bf_global_offline_demo_v7')).version})""")
 assert next_started['mission']==2 and not next_started['over'],next_started
 assert next_started['auto'] and next_started['checked'],next_started
 assert next_started['waves']==auto_page.evaluate('QUESTS[1].battles'),next_started
 assert next_started['clears']==committed['memory'],next_started
 assert next_started['stored']==committed['stored'] and next_started['saveVersion']==7,next_started
 assert auto_page.evaluate('BFGrandGaiaContinueV101.canContinueAuto()') is False
 # A native defeat also ends with a disabled Auto checkbox. The next
 # original mission remains the same uncleared mission and is player-clickable.
 auto_page.evaluate('finish(false); BFGrandGaiaContinueV101.refresh()')
 defeat=auto_page.evaluate("""()=>({
   done:S.over,phase:S.phase,disabled:document.getElementById('auto').disabled,
   next:BFGrandGaiaContinueV101.nextMission,
   eligible:BFGrandGaiaContinueV101.canContinueAuto(),
   clears:JSON.stringify(P.questClears)})""")
 assert defeat['done'] and defeat['phase']=='Defeat' and defeat['disabled'],defeat
 assert defeat['next']==2 and defeat['eligible'] and defeat['clears']==committed['memory'],defeat
 assert btn.is_enabled(),'a defeat must not strand the next manual mission'
 btn.click()
 retried=auto_page.evaluate("""()=>({
   mission:QUEST.missionId,over:S.over,auto:S.auto,
   checked:document.getElementById('auto').checked,
   clears:JSON.stringify(P.questClears)})""")
 assert retried['mission']==2 and not retried['over'],retried
 assert retried['auto'] and retried['checked'] and retried['clears']==committed['memory'],retried
 assert not errors,errors
 auto_page.close()
 assert not errors,errors
 browser.close()
print('PASS v1.01 Continue Story across 106 missions, 3 regions, save v7')
