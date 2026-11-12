"""v30.00 playable demo battle results/redo/continue/source-clear-event actions."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf3000_battle_results.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_DEMO_BATTLE_RESULTS_V3000 */')==1
assert len(src.encode('utf8'))<65536
# Saving is explicitly user-triggered only by the rescue button. The module
# never writes storage directly or adds an alternate save key/format.
assert src.count('localStorage.getItem(')==1 and src.count('saveProgress()')==1
assert 'localStorage.setItem(' not in src and 'localStorage.removeItem(' not in src
assert src.count("document.getElementById('downloadsave')")==1
assert java.index('readPackagedText("bf2900_original_event_expressions.js")') < java.index('readPackagedText("bf3000_battle_results.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
 get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
       'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
       'bf110_quest_journal.js','bf2000_story_battle_hud.js',
       'bf2100_battle_command_tray.js','bf2200_original_event_reader.js',
       'bf2300_morgan_event_dialogue.js','bf2400_st_lamia_event_dialogue.js',
       'bf2500_story_event_prompt.js','bf2600_original_event_portraits.js',
       'bf2700_original_event_stage.js','bf2800_dialogue_speaker_cues.js',
       'bf2900_original_event_expressions.js','bf3000_battle_results.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.evaluate('P.version')==7
 # No canonical v7 receipt exists yet: missing storage must fail closed.
 assert page.evaluate('BFGlobalBattleResultsV3000.committedClearCount(1)') is None
 assert page.evaluate('BFGlobalBattleResultsV3000.committedClearCount(-1)') is None
 assert page.evaluate('BFGlobalBattleResultsV3000.committedClearCount(1.5)') is None
 assert page.evaluate('BFGlobalBattleResultsV3000.snapshot().done') is False
 assert page.locator('#bf3000-result').is_hidden()
 assert page.evaluate('BFGlobalBattleResultsV3000.replayBattle()') is False
 assert page.evaluate('BFGlobalBattleResultsV3000.advance()') is False
 assert page.evaluate('BFGlobalBattleResultsV3000.readScene()') is False
 before=page.evaluate("""()=>({p:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('BFGlobalBattleResultsV3000.refresh()')
 after=page.evaluate("""()=>({p:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'read-only result polling must not mutate save'
 page.evaluate('finish(false)')
 assert page.evaluate('BFGlobalBattleResultsV3000.refresh().done') is True
 assert page.evaluate('BFGlobalBattleResultsV3000.snapshot().victory') is False
 assert page.locator('#bf3000-result').is_visible()
 assert 'DEFEAT' in page.locator('#bf3000-reward').inner_text()
 assert page.locator('#bf3000-next').is_disabled()
 assert page.evaluate('BFGlobalBattleResultsV3000.replayBattle()') is True
 assert page.evaluate('S.over') is False
 assert page.evaluate('QUEST.missionId')==1
 page.evaluate('finish(true)')
 s=page.evaluate('BFGlobalBattleResultsV3000.refresh()')
 assert s['victory'] and s['archive'] and s['clears']==1,s
 assert s['exp']==5 and s['nextId']==2,s
 assert page.evaluate('BFGlobalBattleResultsV3000.committedClearCount(1)')==1
 # A stale/corrupt canonical receipt cannot be bypassed by a still-true
 # saveEnabled flag. All post-victory navigation shares the stored-clear gate.
 stale=page.evaluate("""()=> {
   const key='bf_global_offline_demo_v7',
     original=localStorage.getItem(key),progress=JSON.stringify(P),
     receipt=JSON.parse(original),api=BFGlobalBattleResultsV3000;
   try{
     receipt.questClears[1]=0;
     localStorage.setItem(key,JSON.stringify(receipt));
     const now=api.refresh();
     return {saveFlag:saveEnabled,stored:now.stored,next:now.nextId,
       replay:now.canReplay,advance:api.advance(),
       replayAction:api.replayBattle(),
       rescue:!document.getElementById('bf3000-retry-save').hidden,
       progressSame:JSON.stringify(P)===progress,
       mission:QUEST.missionId};
   }finally{localStorage.setItem(key,original);api.refresh();}
 }""")
 assert stale=={'saveFlag':True,'stored':False,'next':None,
   'replay':False,'advance':False,'replayAction':False,
   'rescue':True,'progressSame':True,'mission':1},stale
 assert page.evaluate('BFGlobalBattleResultsV3000.snapshot().stored') is True
 assert 'SIMULATED' in page.locator('#bf3000-reward').inner_text()
 assert not page.locator('#bf3000-next').is_disabled()
 assert page.evaluate('BFGlobalBattleResultsV3000.readScene()') is False
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalBattleResultsV3000.advance()') is False
 assert page.evaluate('BFGlobalBattleResultsV3000.replayBattle()') is False
 page.evaluate('S.busy=false')
 assert page.evaluate('BFGlobalBattleResultsV3000.advance()') is True
 assert page.evaluate('QUEST.missionId')==2
 assert page.evaluate('S.over') is False
 assert page.evaluate('P.questClears[1]')==1
 assert page.evaluate('JSON.parse(localStorage.getItem("bf_global_offline_demo_v7")).version')==7
 # Source-verified mission clear event gated on real archived progression.
 page.evaluate("""()=>{P.questClears[2]=1;renderQuestList();if(!BFQuestAreas.choose(QUESTS.find(q=>q.missionId===10)))throw Error('No mission 10')}""")
 assert page.evaluate('QUEST.missionId')==10
 page.evaluate('finish(true)')
 assert page.evaluate('BFGlobalBattleResultsV3000.refresh().clearScene') is True
 # Even an apparently successful victory must not unlock a source clear
 # scene if its canonical save receipt no longer matches this mission.
 stale_scene=page.evaluate("""()=>{
   const key='bf_global_offline_demo_v7',saved=localStorage.getItem(key),
     raw=JSON.parse(saved),api=BFGlobalBattleResultsV3000,
     progress=JSON.stringify(P);
   try{
     delete raw.questClears[10];
     localStorage.setItem(key,JSON.stringify(raw));
     const result=api.refresh();
     return {stored:result.stored,clearScene:result.clearScene,
       readScene:api.readScene(),replay:result.canReplay,
       progressSame:JSON.stringify(P)===progress};
   }finally{localStorage.setItem(key,saved);api.refresh();}
 }""")
 assert stale_scene=={'stored':False,'clearScene':False,'readScene':False,
   'replay':False,'progressSame':True},stale_scene
 assert page.evaluate('BFGlobalBattleResultsV3000.snapshot().clearScene') is True
 # Result-screen Next must agree with the campaign resolver even when a later
 # archived mission has just been cleared and earlier missions are unfinished.
 linked=page.evaluate("""()=>({
    campaign:BFGrandGaiaCampaignV100.nextPlayable()?.missionId||null,
    hud:BFGlobalStoryBattleV2000.snapshot().nextId,
    result:BFGlobalBattleResultsV3000.snapshot().nextId
 })""")
 assert linked['campaign']==linked['hud']==linked['result'],linked
 # Invalid *later* saved quest clear must block all navigation consumers.
 quarantined=page.evaluate("""()=>{const id=QUESTS[QUESTS.length-1].missionId;
   const prior=P.questClears[id];
   try{
     P.questClears[id]=-1;
     return [BFGrandGaiaCampaignV100.nextPlayable(),
       BFGlobalStoryBattleV2000.snapshot().nextId,
       BFGlobalBattleResultsV3000.snapshot().nextId];
   }finally{
     if(prior===undefined)delete P.questClears[id];
     else P.questClears[id]=prior;
   }
 }""")
 assert quarantined==[None,None,None],quarantined
 assert page.evaluate('BFGlobalBattleResultsV3000.readScene()') is True
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().chosen')=='clear:10'
 assert 'Farm' in page.locator('#bf2200-text').inner_text()
 assert page.evaluate('BFGlobalBattleResultsV3000.replayBattle()') is True
 page.locator('#mode').select_option('training')
 page.evaluate('finish(true)')
 s=page.evaluate('BFGlobalBattleResultsV3000.refresh()')
 assert s['archive'] is False and s['nextId'] is None and s['exp']==0,s
 assert 'No rewards' in page.locator('#bf3000-reward').inner_text()
 assert page.evaluate('BFGlobalBattleResultsV3000.advance()') is False
 assert page.evaluate('BFGlobalBattleResultsV3000.readScene()') is False
 # A genuine DEMO victory may update memory even though the canonical v7
 # write fails. Never offer Next until that victory has actually been stored.
 page.locator('#mode').select_option('archive')
 assert page.evaluate('BFQuestAreas.choose(QUESTS.find(q=>q.missionId===1))') is True
 before_saved=page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 page.evaluate("""() => {
   window.__resultOriginalSet=localStorage.setItem.bind(localStorage);
   window.__resultQuota=true;
   localStorage.setItem=(key,value)=>{
     if(__resultQuota&&key==='bf_global_offline_demo_v7')
       throw new DOMException('Synthetic quota failure','QuotaExceededError');
     return __resultOriginalSet(key,value);
   };
   finish(true);
 }""")
 failed=page.evaluate('BFGlobalBattleResultsV3000.refresh()')
 assert failed['done'] and failed['victory'] and failed['archive']
 assert failed['stored'] is False and failed['nextId'] is None
 assert failed['canReplay'] is False
 # A fresh in-memory clear under quota failure cannot masquerade as a
 # committed v7 receipt; only the PREVIOUS saved count is returned.
 assert page.evaluate('BFGlobalBattleResultsV3000.committedClearCount(1)')<page.evaluate('P.questClears[1]')
 assert page.locator('#bf3000-next').is_disabled()
 assert page.locator('#bf3000-replay').is_disabled()
 assert page.locator('#bf3000-retry-save').is_visible()
 assert page.locator('#bf3000-backup').is_visible()
 # The story shortcut must immediately reflect an uncommitted victory.
 page.evaluate('BFGrandGaiaContinueV101.refresh()')
 assert page.locator('#bf101-continue').is_disabled()
 assert 'VICTORY NOT SAVED' in page.locator('#bf101-next').inner_text()
 # Simulate stale onscreen button/text before Retry Save; the retry handler
 # itself must restore the correct blocked UI without quest/nav events.
 page.evaluate("""() => {
   document.getElementById('bf101-continue').disabled=false;
   document.getElementById('bf101-next').textContent='STALE RECEIPT';
 }""")
 before_retry=page.evaluate('JSON.stringify(P)')
 page.locator('#bf3000-retry-save').click()
 assert page.locator('#bf101-continue').is_disabled()
 assert 'VICTORY NOT SAVED' in page.locator('#bf101-next').inner_text()
 assert page.evaluate('BFGlobalBattleResultsV3000.snapshot().stored') is False
 assert page.evaluate('JSON.stringify(P)')==before_retry
 # An unexpected storage adapter exception must not escape the Retry Save
 # click handler or change the unsaved win, prior stored bytes, or navigation.
 before_throw_save=page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 page.evaluate("""()=>{window.__v3000OriginalSave=window.saveProgress;
   window.saveProgress=()=>{throw new Error('Synthetic retry save failure')};}""")
 page.locator('#bf3000-retry-save').click()
 assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before_throw_save
 assert page.evaluate('JSON.stringify(P)')==before_retry
 assert page.evaluate('BFGlobalBattleResultsV3000.snapshot().stored') is False
 assert page.locator('#bf3000-next').is_disabled()
 assert page.locator('#bf3000-replay').is_disabled()
 assert page.locator('#bf3000-retry-save').is_visible()
 page.evaluate("window.saveProgress=window.__v3000OriginalSave")
 assert not errors,errors
 # Do not launch an actual download in this test; the standalone signed-APK
 # browser proof separately verifies the exported JSON bytes.
 page.evaluate("""() => {window.__v3000Exports=0;
   document.getElementById('downloadsave').addEventListener('click',e=>{
     __v3000Exports++;e.stopImmediatePropagation();
   },true)}""")
 page.locator('#bf3000-backup').click()
 assert page.evaluate('__v3000Exports')==1
 assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before_saved
 assert page.evaluate('BFGlobalBattleResultsV3000.replayBattle()') is False
 memory=page.evaluate('JSON.stringify(P)')
 assert page.evaluate('BFGlobalBattleResultsV3000.advance()') is False
 assert page.evaluate('QUEST.missionId')==1
 assert page.evaluate('JSON.stringify(P)')==memory
 # A later *successful* manual save re-enables the same earned next mission.
 page.evaluate('window.__resultQuota=false')
 page.locator('#bf3000-retry-save').click()
 # No explicit Continue refresh here: Retry Save must update the UI on its own.
 assert page.locator('#bf101-continue').is_enabled()
 assert page.locator('#bf101-next').inner_text().startswith('NEXT:')
 assert page.evaluate('BFGrandGaiaContinueV101.nextMission') is not None
 saved=page.evaluate('BFGlobalBattleResultsV3000.refresh()')
 assert page.locator('#bf3000-retry-save').is_hidden()
 assert page.locator('#bf3000-backup').is_hidden()
 # Mission 10 was already cleared earlier in this same test; the story
 # router may now offer 11 rather than 2 even when replaying mission 1.
 # Verify the chosen archived next mission, not a stale hard-coded ID.
 assert saved['stored'] and saved['canReplay']
 next_id=saved['nextId']
 assert isinstance(next_id,int) and next_id>1
 assert not page.locator('#bf3000-next').is_disabled()
 assert not page.locator('#bf3000-replay').is_disabled()
 assert page.evaluate('BFGlobalBattleResultsV3000.advance()') is True
 assert page.evaluate('QUEST.missionId')==next_id
 assert page.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_demo_v7')).questClears[1]")>=1
 # A newly won source-verified clear scene must also be inaccessible after
 # failed storage; otherwise an unsaved mission 10 still reports completion.
 page.evaluate("""() => {
    P.questClears[2]=1;renderQuestList();
    if(!BFQuestAreas.choose(QUESTS.find(q=>q.missionId===10)))
      throw Error('No mission 10 for save-scene regression');
 }""")
 scene_save=page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 page.evaluate('()=>{__resultQuota=true;finish(true)}')
 missing=page.evaluate('BFGlobalBattleResultsV3000.refresh()')
 assert missing['victory'] and not missing['stored']
 assert missing['canReplay'] is False
 assert page.locator('#bf3000-replay').is_disabled()
 assert page.evaluate('BFGlobalBattleResultsV3000.replayBattle()') is False
 assert missing['clearScene'] is False
 assert page.locator('#bf3000-scene').is_hidden()
 assert page.evaluate('BFGlobalBattleResultsV3000.readScene()') is False
 assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==scene_save
 assert page.evaluate('()=>{__resultQuota=false;return saveProgress()}') is True
 scene_saved=page.evaluate('BFGlobalBattleResultsV3000.refresh()')
 assert scene_saved['stored'] and scene_saved['clearScene'] and scene_saved['canReplay']
 assert page.locator('#bf3000-scene').is_visible()
 assert page.evaluate('BFGlobalBattleResultsV3000.readScene()') is True
 assert page.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_demo_v7')).questClears[10]")>=1
 assert not errors,errors
 # A fresh separate browser page proves player-clicked DEFEAT retry uses
 # the native Auto checkbox exactly once, never rewrites P or canonical v7.
 trial=browser.new_page(viewport={'width':390,'height':844})
 trial_errors=[];trial.on('pageerror',lambda e:trial_errors.append(str(e)))
 trial.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',
   {configurable:true,value:{getItem:k=>db[k]??null,
   setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
   key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 trial.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 trial.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
       'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
       'bf110_quest_journal.js','bf2000_story_battle_hud.js',
       'bf2100_battle_command_tray.js','bf2200_original_event_reader.js',
       'bf2300_morgan_event_dialogue.js','bf2400_st_lamia_event_dialogue.js',
       'bf2500_story_event_prompt.js','bf2600_original_event_portraits.js',
       'bf2700_original_event_stage.js','bf2800_dialogue_speaker_cues.js',
       'bf2900_original_event_expressions.js','bf3000_battle_results.js'):
  trial.add_script_tag(path=str(A/name))
 trial.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert trial.locator('#bf3000-retry-auto').count()==1
 assert trial.evaluate('BFGlobalBattleResultsV3000.retryDefeatAuto()') is False
 trial.evaluate('finish(false)')
 assert trial.evaluate('BFGlobalBattleResultsV3000.canRetryDefeatAuto()') is True
 before=trial.evaluate("""()=>({
    saved:localStorage.getItem('bf_global_offline_demo_v7'),
    player:JSON.stringify(P),mission:QUEST.missionId})""")
 # Unknown repeat session must deny retry BEFORE invoking native reset.
 invalid=trial.evaluate("""()=>{const prior=window.BFGlobalQoLQuestRepeatV9800;
  try{window.BFGlobalQoLQuestRepeatV9800={statusSnapshot(){
    throw Error('repeat broken')}};
    return {ready:BFGlobalBattleResultsV3000.canRetryDefeatAuto(),
      action:BFGlobalBattleResultsV3000.retryDefeatAuto(),
      stillDefeat:S.over};}
  finally{window.BFGlobalQoLQuestRepeatV9800=prior}
 }""")
 assert invalid=={'ready':False,'action':False,'stillDefeat':True},invalid
 success=trial.evaluate("""()=>{const auto=document.getElementById('auto');
    const done=BFGlobalBattleResultsV3000.retryDefeatAuto();
    const status={done,running:S.auto,checked:auto.checked,over:S.over,
      mission:QUEST.missionId};
    if(auto.checked&&!auto.disabled)auto.click();
    else{S.auto=false;auto.checked=false}
    return status;}""")
 assert success['done'] and success['running'] and success['checked'],success
 assert not success['over'] and success['mission']==before['mission'],success
 trial.evaluate('finish(false)')
 # Native Auto click failure after replay disarms Auto and preserves manual
 # play; no P/version-7 quest save or reward is ever mutated by the shortcut.
 denied=trial.evaluate("""()=>{const auto=document.getElementById('auto');
    const click=auto.click;auto.click=()=>{throw Error('no native toggle')};
    try{const ok=BFGlobalBattleResultsV3000.retryDefeatAuto();
      return {ok,running:S.auto,checked:auto.checked,over:S.over,
        mission:QUEST.missionId,saved:localStorage.getItem('bf_global_offline_demo_v7'),
        player:JSON.stringify(P)};}
    finally{auto.click=click}
 }""")
 assert denied['ok'] is False and denied['running'] is False,denied
 assert denied['checked'] is False and denied['over'] is False,denied
 assert denied['mission']==before['mission'],denied
 assert denied['saved']==before['saved'] and denied['player']==before['player'],denied
 assert not trial_errors,trial_errors
 trial.close()
 browser.close()
print('PASS v30.00: real demo victory/defeat results, retry and next via engine, original source scene, training isolation')
