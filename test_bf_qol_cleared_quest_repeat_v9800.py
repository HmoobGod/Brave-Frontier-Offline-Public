"""v98: bounded cleared-mission automation driven only by verified result/replay."""
from pathlib import Path
import shutil, re, json
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
src=(A/'bf9800_qol_cleared_quest_repeat.js').read_text('utf8')
assert src.count('BF_GLOBAL_QOL_CLEARED_QUEST_REPEAT_V9800')==1
assert len(src.encode('utf8'))<65536
assert not any(x in src for x in ('saveProgress(', 'localStorage', 'awardDemoRewards(', 'finish(true)', 'BFAndroid', 'fetch('))
assert 'results.replayBattle()' in src
assert 's.clears<=session.lastClear' in src
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'readPackagedText("bf9800_qol_cleared_quest_repeat.js")' in java

with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content("""<html><body><div id="bf2000-run"></div>
   <input id="auto" type="checkbox"></body></html>""")
 # set_content runs on about:blank, where native localStorage is denied.
 # Provide a disposable in-memory key/value store and write counter rather
 # than depending on a real browser origin or the owner's canonical save.
 p.evaluate("""()=>{
   const data=new Map();
   window.__v98StorageWrites=0;
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:key=>data.has(key)?data.get(key):null,
     setItem:(key,value)=>{data.set(String(key),String(value));__v98StorageWrites++;},
     removeItem:key=>data.delete(String(key)),
     clear:()=>data.clear(),key:i=>[...data.keys()][i]??null,
     get length(){return data.size}
   }});
 }""")
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011],squad:[10011],questClears:{1:1}};
   localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
   window.QUEST={missionId:1};
   window.S={mode:'archive',over:true,busy:false,phase:'Victory'};
   window.__repeatCount=0;
   const snapshot=()=>({missionId:QUEST.missionId,done:S.over,
     victory:S.over&&S.phase==='Victory',archive:S.mode==='archive',
     clears:P.questClears[QUEST.missionId]||0,stored:window.__stored98!==false,
     canReplay:S.over&&!S.busy});
   const replayBattle=()=>{
     if(!S.over||S.busy)return false;
     window.__repeatCount++;S.over=false;S.phase='Battle';return true;
   };
   window.BFGlobalBattleResultsV3000={snapshot,replayBattle};
 }""")
 p.add_script_tag(path=str(A/'bf9800_qol_cleared_quest_repeat.js'))
 api='BFGlobalQoLQuestRepeatV9800'
 assert p.locator('#bf9800-auto-repeat').count()==1
 assert p.evaluate(api+'.statusSnapshot().active') is False
 # With the source-backed 2022 campaign module available, all original
 # 2022 quest-wave and scalar-economy fields must match before unattended
 # replay; a later source mismatch must disarm an already-running repeat.
 source_proof=p.evaluate("""()=>{
   const repeat=BFGlobalQoLQuestRepeatV9800,prev=window.BFGrandGaiaCampaignV100,
     oldBattles=QUEST.battles,oldTotal=S.totalWaves,oldOver=S.over,
     oldPhase=S.phase,oldAuto=S.auto,
     saved=localStorage.getItem('bf_global_offline_demo_v7'),
     player=JSON.stringify(P),before=__repeatCount;
   let invalidWave=false,invalidEconomy=false,missingEconomy=false,
       unknownEconomy=false,brokenSource=false,
       invalidLiveWave=false,started=false,stopped=false,
       disarmed=false,noExtraReplay=false;
   try{
     QUEST.battles=3;S.totalWaves=3;
     const api={waveReadiness:()=>({missionId:1,verifiedWaveCount:4}),
       sourceEconomyReadiness:()=>true};
     window.BFGrandGaiaCampaignV100=api;
     invalidWave=!repeat.start(2)&&__repeatCount===before;
     api.waveReadiness=()=>({missionId:1,verifiedWaveCount:3});
     api.sourceEconomyReadiness=()=>false;
     invalidEconomy=!repeat.start(2)&&__repeatCount===before;
     delete api.sourceEconomyReadiness;
     missingEconomy=!repeat.start(2)&&__repeatCount===before;
     api.sourceEconomyReadiness=()=>undefined;
     unknownEconomy=!repeat.start(2)&&__repeatCount===before;
     api.sourceEconomyReadiness=()=>{throw Error('bad original source')};
     brokenSource=!repeat.start(2)&&__repeatCount===before;
     api.sourceEconomyReadiness=()=>true;
     // The live battle's real totalWaves must be an exact source-matching
     // safe integer. Previously NaN/undefined/text slipped through because
     // a comparison ran only when totalWaves WAS already an integer.
     const beforeTotals=__repeatCount;
     invalidLiveWave=[undefined,null,NaN,Infinity,'3',3.5,0,-1,2]
       .every(value=>{
         S.totalWaves=value;
         return !repeat.start(2)&&__repeatCount===beforeTotals;
       });
     S.totalWaves=3;
     started=repeat.start(2)&&repeat.statusSnapshot().active;
     const afterStart=__repeatCount;
     api.waveReadiness=()=>null;
     stopped=repeat.poll()===true&&!repeat.statusSnapshot().active&&
       repeat.statusSnapshot().reason===
         'Stopped: verified 2022 quest record changed';
     disarmed=!document.getElementById('auto').checked;
     noExtraReplay=__repeatCount===afterStart;
   }finally{
     if(prev===undefined)delete window.BFGrandGaiaCampaignV100;
     else window.BFGrandGaiaCampaignV100=prev;
     if(oldBattles===undefined)delete QUEST.battles;
     else QUEST.battles=oldBattles;
     if(oldTotal===undefined)delete S.totalWaves;
     else S.totalWaves=oldTotal;
     S.over=oldOver;S.phase=oldPhase;
     if(oldAuto===undefined)delete S.auto;else S.auto=oldAuto;
     document.getElementById('auto').checked=false;
     window.__repeatCount=before;
   }
   return {invalidWave,invalidEconomy,missingEconomy,unknownEconomy,
     brokenSource,invalidLiveWave,
     started,stopped,disarmed,noExtraReplay,
     saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved,
     playerSame:JSON.stringify(P)===player};
 }""")
 assert source_proof=={
   'invalidWave':True,'invalidEconomy':True,'missingEconomy':True,
   'unknownEconomy':True,'brokenSource':True,
   'invalidLiveWave':True,'started':True,'stopped':True,
   'disarmed':True,'noExtraReplay':True,
   'saveSame':True,'playerSame':True},source_proof
 # An invalid canonical save receipt must prevent an unattended replay
 # even if the old general stored boolean still reports success.
 p.evaluate('BFGlobalBattleResultsV3000.committedClearCount=()=>0')
 assert p.evaluate(api+'.start(2)') is False
 assert p.evaluate('window.__repeatCount')==0
 p.evaluate('delete BFGlobalBattleResultsV3000.committedClearCount')
 assert p.locator('#bf9800-repeat-count option').count()==6
 assert p.locator('#bf9800-repeat-count option').all_text_contents()==[
   '1 additional clears','2 additional clears','5 additional clears',
   '10 additional clears','20 additional clears','50 additional clears']
 assert p.locator('#bf9800-repeat-count').input_value()=='2'
 assert p.evaluate(api+'.start(0)') is False
 assert p.evaluate(api+'.start(21)') is False
 assert p.evaluate(api+'.start(51)') is False
 assert p.evaluate(api+'.start(1.5)') is False
 p.evaluate("window.__stored98=false")
 assert p.evaluate(api+'.start(2)') is False
 p.evaluate("window.__stored98=true")
 # Native victory normally disables the Auto control until replayBattle
 # begins the next battle. Allow that transition; if the new battle STILL
 # cannot enable Auto, abort the repeat session without saving or continuing.
 p.evaluate("document.getElementById('auto').disabled=true")
 before_replays=p.evaluate('window.__repeatCount')
 before_save=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 assert p.evaluate(api+'.start(1)') is False
 assert p.evaluate('window.__repeatCount')==before_replays+1
 assert p.evaluate(api+'.statusSnapshot().active') is False
 assert p.evaluate(api+'.statusSnapshot().reason')=='Stopped: native Auto could not start'
 assert not p.locator('#auto').is_checked()
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before_save
 p.evaluate("""()=>{document.getElementById('auto').disabled=false;
    window.__repeatCount=0;S.over=true;S.phase='Victory';}""")
 # A real native victory can disable Auto UNTIL the newly replayed battle
 # enables it. This valid transition must still start and then cleanly stop.
 native_victory=p.evaluate("""()=>{const impl=BFGlobalBattleResultsV3000;
   const native=impl.replayBattle,auto=document.getElementById('auto');
   const before=window.__repeatCount;
   const saved=localStorage.getItem('bf_global_offline_demo_v7');
   auto.disabled=true;
   try{
     impl.replayBattle=()=>{const accepted=native();auto.disabled=false;
       return accepted;};
     const accepted=BFGlobalQoLQuestRepeatV9800.start(1);
     const armed=BFGlobalQoLQuestRepeatV9800.statusSnapshot().active;
     const enabled=auto.checked&&!auto.disabled;
     const stopped=BFGlobalQoLQuestRepeatV9800.stop('Fixture reset',false);
     return {accepted,armed,enabled,stopped,disarmed:!auto.checked,
       replayCount:window.__repeatCount-before,
       saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved};
   }finally{
     impl.replayBattle=native;auto.disabled=false;auto.checked=false;
     window.__repeatCount=before;S.over=true;S.phase='Victory';
   }
 }""")
 assert native_victory=={'accepted':True,'armed':True,'enabled':True,
   'stopped':True,'disarmed':True,'replayCount':1,'saveSame':True},native_victory
 # Native replay may leave Auto CHECKED but disabled. Its checked state
 # alone does not establish that the new battle can drive Auto.
 disabled_checked=p.evaluate("""()=>{const impl=BFGlobalBattleResultsV3000;
   const original=impl.replayBattle,auto=document.getElementById('auto');
   const before=window.__repeatCount;
   const saved=localStorage.getItem('bf_global_offline_demo_v7');
   const priorAuto=S.auto;
   try{
     impl.replayBattle=()=>{const ok=original();
       auto.checked=true;auto.disabled=true;S.auto=true;return ok;};
     const accepted=BFGlobalQoLQuestRepeatV9800.start(1);
     const status=BFGlobalQoLQuestRepeatV9800.statusSnapshot();
     return {accepted,armed:status.active,reason:status.reason,
       disarmed:!auto.checked&&S.auto===false,
       replayCount:window.__repeatCount-before,
       saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved};
   }finally{
     impl.replayBattle=original;auto.disabled=false;auto.checked=false;
     S.auto=priorAuto;
     window.__repeatCount=before;S.over=true;S.phase='Victory';
   }
 }""")
 assert disabled_checked=={'accepted':False,'armed':False,
   'reason':'Stopped: native Auto could not start','disarmed':True,
   'replayCount':1,'saveSame':True},disabled_checked
 # A stale checked Auto input is not evidence of native battle execution.
 # An explicit S.auto=false after replay must disarm the session rather
 # than leaving repeat armed against a manual-only battle.
 mismatched=p.evaluate("""()=>{const impl=BFGlobalBattleResultsV3000;
   const native=impl.replayBattle,auto=document.getElementById('auto');
   const count=window.__repeatCount,priorAuto=S.auto;
   const saved=localStorage.getItem('bf_global_offline_demo_v7');
   try{
     impl.replayBattle=()=>{const accepted=native();
       auto.checked=true;S.auto=false;return accepted;};
     const accepted=BFGlobalQoLQuestRepeatV9800.start(2);
     const state=BFGlobalQoLQuestRepeatV9800.statusSnapshot();
     return {accepted,armed:state.active,reason:state.reason,
       disarmed:!auto.checked&&S.auto===false,
       replayCount:window.__repeatCount-count,
       savedSame:localStorage.getItem('bf_global_offline_demo_v7')===saved};
   }finally{impl.replayBattle=native;auto.checked=false;S.auto=priorAuto;
     window.__repeatCount=count;S.over=true;S.phase='Victory';}
 }""")
 assert mismatched=={'accepted':False,'armed':False,
   'reason':'Stopped: native Auto could not start','disarmed':True,
   'replayCount':1,'savedSame':True},mismatched
 # A later native Auto engine shutoff (without a checkbox change event)
 # also cancels the repeat before any second quest can start.
 mismatch_poll=p.evaluate("""()=>{const auto=document.getElementById('auto');
   const count=window.__repeatCount,priorAuto=S.auto;
   const saved=localStorage.getItem('bf_global_offline_demo_v7');
   try{
     const started=BFGlobalQoLQuestRepeatV9800.start(2);
     if(!started)return {fixtureFailed:true};
     S.auto=false;
     const stopped=BFGlobalQoLQuestRepeatV9800.poll();
     const status=BFGlobalQoLQuestRepeatV9800.statusSnapshot();
     return {started,stopped,armed:status.active,
       reason:status.reason,disarmed:!auto.checked&&S.auto===false,
       replayCount:window.__repeatCount-count,
       savedSame:localStorage.getItem('bf_global_offline_demo_v7')===saved};
   }finally{auto.checked=false;S.auto=priorAuto;
     window.__repeatCount=count;S.over=true;S.phase='Victory';}
 }""")
 assert mismatch_poll=={'started':True,'stopped':True,'armed':False,
   'reason':'Stopped: Auto Battle disabled','disarmed':True,
   'replayCount':1,'savedSame':True},mismatch_poll
 # The native checkbox can also become disabled AFTER a real replay starts.
 # Detect that immediately, so no invisible repeat session remains armed.
 toggle_lost=p.evaluate("""()=>{const impl=BFGlobalBattleResultsV3000;
   const before=window.__repeatCount;
   const saved=localStorage.getItem('bf_global_offline_demo_v7');
   const native=impl.replayBattle;
   try{
     impl.replayBattle=()=>{
       const result=native();
       document.getElementById('auto').disabled=true;
       return result;
     };
     const accepted=BFGlobalQoLQuestRepeatV9800.start(2);
     const status=BFGlobalQoLQuestRepeatV9800.statusSnapshot();
     return {accepted,armed:status.active,
       reason:status.reason,auto:document.getElementById('auto').checked,
       replayCount:window.__repeatCount-before,
       saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved};
   }finally{
     impl.replayBattle=native;
     document.getElementById('auto').disabled=false;
     // The rejected replay is an isolated failure fixture, not a completed
     // normal test run. Restore this test harness's synthetic replay counter.
     window.__repeatCount=before;
     S.over=true;S.phase='Victory';
   }
 }""")
 assert toggle_lost=={'accepted':False,'armed':False,
   'reason':'Stopped: native Auto could not start','auto':False,
   'replayCount':1,'saveSame':True},toggle_lost
 # A throwing native replay adapter must cancel the entire bounded session,
 # including if the adapter already began the next battle before throwing.
 # No fabricated clear, extra replay, owner save write or native Auto remains.
 for after_start in (False,True):
  replay_exception=p.evaluate("""afterStart=>{
    const api=BFGlobalQoLQuestRepeatV9800,
      impl=window.BFGlobalBattleResultsV3000,original=impl.replayBattle,
      auto=document.getElementById('auto'),prevAuto=S.auto,
      beforeCount=window.__repeatCount,
      beforeWrites=window.__v98StorageWrites,
      beforePlayer=JSON.stringify(P),
      beforeSave=localStorage.getItem('bf_global_offline_demo_v7');
    try{
      S.over=true;S.busy=false;S.mode='archive';S.phase='Victory';
      S.auto=false;auto.checked=false;
      impl.replayBattle=()=>{
        if(afterStart){
          const started=original();
          if(!started)throw Error('test fixture failed to start');
          S.auto=true;auto.checked=true;
        }
        throw Error('native replay failed');
      };
      const accepted=api.start(2),state=api.statusSnapshot();
      return {accepted,active:state.active,reason:state.reason,
        nativeStopped:S.auto===false&&!auto.checked,
        replayDelta:window.__repeatCount-beforeCount,
        saveSame:localStorage.getItem('bf_global_offline_demo_v7')===beforeSave,
        writesSame:window.__v98StorageWrites===beforeWrites,
        playerSame:JSON.stringify(P)===beforePlayer};
    }finally{
      impl.replayBattle=original;auto.disabled=false;auto.checked=false;
      if(prevAuto===undefined)delete S.auto;else S.auto=prevAuto;
      S.over=true;S.busy=false;S.phase='Victory';
      window.__repeatCount=beforeCount;
    }
  }""",after_start)
  assert replay_exception=={'accepted':False,'active':False,
    'reason':'Stopped: native mission replay failed','nativeStopped':True,
    'replayDelta':1 if after_start else 0,
    'saveSame':True,'writesSame':True,'playerSame':True},replay_exception
 # A throwing native Auto checkbox click handler must not leave a repeat
 # session armed. Cover both re-arming after a replay starts and disarming
 # an already-active session; neither may modify P or canonical v7 storage.
 for during_stop in (False,True):
  broken_click=p.evaluate("""duringStop=>{
    const api=BFGlobalQoLQuestRepeatV9800,
      auto=document.getElementById('auto'),
      originalClick=auto.click,impl=BFGlobalBattleResultsV3000,
      originalReplay=impl.replayBattle,
      beforeCount=__repeatCount,beforeWrites=__v98StorageWrites,
      beforePlayer=JSON.stringify(P),
      beforeSave=localStorage.getItem('bf_global_offline_demo_v7'),
      previousAuto=S.auto;
    try{
      S.mode='archive';S.over=true;S.busy=false;S.phase='Victory';
      delete S.auto;auto.disabled=false;auto.checked=false;
      if(duringStop){
        if(!api.start(2))return {fixtureFailed:true};
      }else{
        // Simulate a replay adapter that already reports native Auto ON,
        // even though the checkbox handler subsequently fails to arm.
        impl.replayBattle=()=>{
          const started=originalReplay();
          if(started)S.auto=true;
          return started;
        };
      }
      auto.click=()=>{throw Error('native checkbox handler failed');};
      const accepted=duringStop?api.stop('Stopped by player',false):api.start(2);
      const snapshot=api.statusSnapshot();
      return {accepted,active:snapshot.active,
        reason:snapshot.reason,
        nativeDisarmed:S.auto===false&&!auto.checked,
        replayDelta:__repeatCount-beforeCount,
        progressSame:JSON.stringify(P)===beforePlayer,
        saveSame:localStorage.getItem('bf_global_offline_demo_v7')===beforeSave,
        writesSame:__v98StorageWrites===beforeWrites};
    }finally{
      impl.replayBattle=originalReplay;
      auto.click=originalClick;auto.checked=false;auto.disabled=false;
      if(previousAuto===undefined)delete S.auto;else S.auto=previousAuto;
      S.over=true;S.busy=false;S.phase='Victory';__repeatCount=beforeCount;
    }
  }""",during_stop)
  assert broken_click=={'accepted':True if during_stop else False,
    'active':False,
    'reason':'Stopped by player' if during_stop else 'Stopped: native Auto could not start',
    'nativeDisarmed':True,'replayDelta':1,
    'progressSame':True,'saveSame':True,'writesSame':True},broken_click
 # A snapshot can return an object whose property getter throws later.
 # Reading every used field inside the guard must disarm an active session.
 getter_failure=p.evaluate("""()=>{
   const api=BFGlobalQoLQuestRepeatV9800,
     result=BFGlobalBattleResultsV3000,old=result.snapshot,
     auto=document.getElementById('auto'),prev=S.auto,
     count=__repeatCount,writes=__v98StorageWrites,
     player=JSON.stringify(P),save=localStorage.getItem('bf_global_offline_demo_v7');
   try{
     S.mode='archive';S.over=true;S.busy=false;S.phase='Victory';
     delete S.auto;auto.checked=false;auto.disabled=false;
     result.snapshot=()=>({get done(){throw Error('getter failed')}});
     const refused=api.start(2)===false;
     result.snapshot=old;
     const started=api.start(2)===true;
     S.auto=true;auto.checked=true;
     result.snapshot=()=>({get missionId(){throw Error('getter failed')}});
     const stopped=api.poll()===true;
     return {refused,started,stopped,active:api.statusSnapshot().active,
       reason:api.statusSnapshot().reason,disarmed:S.auto===false&&!auto.checked,
       delta:__repeatCount-count,playerSame:JSON.stringify(P)===player,
       saveSame:localStorage.getItem('bf_global_offline_demo_v7')===save,
       writesSame:__v98StorageWrites===writes};
   }finally{
     result.snapshot=old;auto.checked=false;auto.disabled=false;
     if(prev===undefined)delete S.auto;else S.auto=prev;
     S.mode='archive';S.over=true;S.busy=false;S.phase='Victory';
     __repeatCount=count;
   }
 }""")
 assert getter_failure=={'refused':True,'started':True,'stopped':True,
   'active':False,'reason':'Stopped: battle results unavailable',
   'disarmed':True,'delta':1,'playerSame':True,'saveSame':True,
   'writesSame':True},getter_failure
 # Native results may throw before a repeat starts, between the initial
 # snapshot and playAgain(), or in a timer poll while native Auto is armed.
 # Never continue without a trusted result or modify the canonical v7 save.
 snapshot_failures=p.evaluate("""()=>{
   const api=BFGlobalQoLQuestRepeatV9800,
     result=BFGlobalBattleResultsV3000,
     original=result.snapshot,
     auto=document.getElementById('auto'),
     previousAuto=S.auto,beforeCount=__repeatCount,
     beforeWrites=__v98StorageWrites,
     beforePlayer=JSON.stringify(P),
     beforeSave=localStorage.getItem('bf_global_offline_demo_v7');
   let refusedStart=false,disabledUI=false,stagedFailure=false,
     stagedReason='',started=false,stopped=false,disarmed=false,
     stoppedReason='',delta=0;
   try{
     S.mode='archive';S.over=true;S.busy=false;S.phase='Victory';
     delete S.auto;auto.checked=false;auto.disabled=false;
     result.snapshot=()=>{throw Error('read failed')};
     refusedStart=api.start(2)===false;
     disabledUI=api.poll()===false&&
       document.getElementById('bf9800-start').disabled;
     let reads=0;
     result.snapshot=()=>{
       if(++reads===2)throw Error('read failed after arming');
       return original();
     };
     stagedFailure=api.start(2)===false&&!api.statusSnapshot().active;
     stagedReason=api.statusSnapshot().reason;
     result.snapshot=original;
     started=api.start(2)===true;
     const afterStart=__repeatCount;
     S.auto=true;auto.checked=true;
     result.snapshot=()=>{throw Error('poll read failed')};
     stopped=api.poll()===true&&!api.statusSnapshot().active;
     stoppedReason=api.statusSnapshot().reason;
     disarmed=S.auto===false&&!auto.checked;
     delta=__repeatCount-beforeCount;
     return {refusedStart,disabledUI,stagedFailure,stagedReason,
       started,stopped,stoppedReason,disarmed,delta,
       noFurtherReplay:__repeatCount===afterStart,
       playerSame:JSON.stringify(P)===beforePlayer,
       saveSame:localStorage.getItem('bf_global_offline_demo_v7')===beforeSave,
       writesSame:__v98StorageWrites===beforeWrites};
   }finally{
     result.snapshot=original;auto.checked=false;auto.disabled=false;
     if(previousAuto===undefined)delete S.auto;else S.auto=previousAuto;
     S.mode='archive';S.over=true;S.busy=false;S.phase='Victory';
     __repeatCount=beforeCount;
   }
 }""")
 assert snapshot_failures=={
   'refusedStart':True,'disabledUI':True,
   'stagedFailure':True,'stagedReason':'Stopped: replay prerequisites changed',
   'started':True,'stopped':True,
   'stoppedReason':'Stopped: battle results unavailable',
   'disarmed':True,'delta':1,'noFurtherReplay':True,
   'playerSame':True,'saveSame':True,'writesSame':True},snapshot_failures
 # A one-clear player choice is a genuine bounded native replay: it executes
 # one additional quest, confirms the stored clear, then restores Auto OFF.
 assert p.evaluate(api+'.start(1)') is True
 assert p.evaluate('window.__repeatCount')==1
 assert p.locator('#auto').is_checked()
 p.evaluate("""()=>{P.questClears[1]++;S.over=true;S.phase='Victory';
   document.getElementById('auto').checked=false;}""")
 assert p.evaluate(api+'.poll()') is True
 assert p.evaluate(api+'.statusSnapshot().active') is False
 assert p.evaluate(api+'.statusSnapshot().completed')==1
 assert p.evaluate('window.__repeatCount')==1
 assert not p.locator('#auto').is_checked()
 assert p.evaluate(api+'.start(2)') is True
 assert p.evaluate('window.__repeatCount')==2
 assert p.locator('#auto').is_checked()
 assert p.evaluate(api+'.statusSnapshot().target')==2
 p.evaluate("""()=>{P.questClears[1]++;S.over=true;S.phase='Victory';
   document.getElementById('auto').checked=false;}""")
 assert p.evaluate(api+'.poll()') is True
 assert p.evaluate('window.__repeatCount')==3
 assert p.evaluate(api+'.statusSnapshot().completed')==1
 p.evaluate("""()=>{P.questClears[1]++;S.over=true;S.phase='Victory'}""")
 assert p.evaluate(api+'.poll()') is True
 assert p.evaluate(api+'.statusSnapshot().active') is False
 assert p.evaluate(api+'.statusSnapshot().completed')==2
 assert not p.locator('#auto').is_checked()
 assert p.evaluate('window.__repeatCount')==3
 # Long opt-in repeat runs still require one real stored-clear receipt for
 # every additional replay. No direct save writes, hidden rewards, free
 # clears or unbounded loops: 20 and 50 must both terminate exactly.
 for length in (20,50):
  outcome=p.evaluate("""count=>{
    const api=BFGlobalQoLQuestRepeatV9800,
      auto=document.getElementById('auto'),
      originalWrites=__v98StorageWrites,
      previousReplay=__repeatCount,
      stored=localStorage.getItem('bf_global_offline_demo_v7');
    S.over=true;S.busy=false;S.phase='Victory';
    auto.checked=false;
    if(!api.start(count))return {error:'start failed',count};
    const armed=api.statusSnapshot().target===count;
    for(let i=0;i<count;i++){
      // Simulate one real result receipt at a time; the repeat module
      // must never add quest clears or write the v7 save on its own.
      P.questClears[1]++;
      S.over=true;S.phase='Victory';auto.checked=false;
      if(!api.poll())return {error:'poll failed',count,i};
      const snap=api.statusSnapshot();
      if(i<count-1&&(!snap.active||snap.completed!==i+1))
        return {error:'early stop',count,i,snap};
    }
    const end=api.statusSnapshot();
    return {armed,complete:end.completed,active:end.active,
      additionalReplays:__repeatCount-previousReplay,
      autoDisarmed:!auto.checked,
      saveSame:localStorage.getItem('bf_global_offline_demo_v7')===stored,
      writesSame:__v98StorageWrites===originalWrites};
  }""",length)
  assert outcome=={'armed':True,'complete':length,'active':False,
                   'additionalReplays':length,'autoDisarmed':True,
                   'saveSame':True,'writesSame':True},outcome
 # The live counter can advance before a save actually commits. The v322
 # native v3000 receipt API must stop Auto before another replay begins.
 p.evaluate("""()=>{QUEST.missionId=1;S.over=true;S.busy=false;
   S.phase='Victory';document.getElementById('auto').checked=false;}""")
 assert p.evaluate(api+'.start(2)') is True
 receipt_blocked=p.evaluate("""()=>{
   const results=BFGlobalBattleResultsV3000,
     old=__repeatCount,save=localStorage.getItem('bf_global_offline_demo_v7');
   P.questClears[1]++;S.over=true;S.phase='Victory';
   results.committedClearCount=id=>P.questClears[id]-1;
   const stopped=BFGlobalQoLQuestRepeatV9800.poll(),
     state=BFGlobalQoLQuestRepeatV9800.statusSnapshot();
   delete results.committedClearCount;
   return {stopped,active:state.active,reason:state.reason,
     noNextReplay:__repeatCount===old,
     saveUnchanged:localStorage.getItem('bf_global_offline_demo_v7')===save,
     autoDisarmed:!document.getElementById('auto').checked};
 }""")
 assert receipt_blocked=={'stopped':True,'active':False,
   'reason':'Stopped: latest clear not committed to v7 save',
   'noNextReplay':True,'saveUnchanged':True,'autoDisarmed':True},receipt_blocked
 # Cannot start before first successful clear of a mission.
 p.evaluate("""()=>{QUEST.missionId=2;P.questClears[2]=0;S.over=true;S.phase='Victory'}""")
 assert p.evaluate(api+'.start(2)') is False
 # Running quest switch cancels without claiming any new rewards.
 p.evaluate("""()=>{QUEST.missionId=1;S.over=true;S.phase='Victory'}""")
 assert p.evaluate(api+'.start(2)') is True
 p.evaluate('QUEST.missionId=2')
 p.evaluate(api+'.poll()')
 assert p.evaluate(api+'.statusSnapshot().active') is False
 assert 'quest or mode changed' in p.evaluate(api+'.statusSnapshot().reason')
 assert not p.locator('#auto').is_checked(),'unexpected quest change kept native Auto running'
 # Defeat stops repeats instead of replaying a loss.
 p.evaluate("""()=>{QUEST.missionId=1;S.over=true;S.phase='Victory'}""")
 assert p.evaluate(api+'.start(2)') is True
 p.evaluate("""()=>{S.over=true;S.phase='Defeat'}""")
 p.evaluate(api+'.poll()')
 assert p.evaluate(api+'.statusSnapshot().active') is False
 assert 'battle lost' in p.evaluate(api+'.statusSnapshot().reason')
 assert not p.locator('#auto').is_checked(),'defeat cancellation kept native Auto running'
 # A failed native save or unconfirmed repeated clear must also disarm Auto,
 # and may never trigger another replay or mutate the canonical player data.
 for failed in ('save','missing-clear'):
  p.evaluate("""()=>{QUEST.missionId=1;S.busy=false;S.over=true;S.phase='Victory';
    window.__stored98=true;document.getElementById('auto').checked=false;}""")
  assert p.evaluate(api+'.start(2)') is True,failed
  assert p.locator('#auto').is_checked(),failed
  before_player=p.evaluate('JSON.stringify(P)')
  before_replays=p.evaluate('window.__repeatCount')
  p.evaluate('S.over=true;S.phase="Victory"')
  if failed=='save':p.evaluate('window.__stored98=false')
  assert p.evaluate(api+'.poll()') is True,failed
  assert not p.evaluate(api+'.statusSnapshot().active'),failed
  assert not p.locator('#auto').is_checked(),failed
  assert p.evaluate('window.__repeatCount')==before_replays,failed
  assert p.evaluate('JSON.stringify(P)')==before_player,failed
  p.evaluate('window.__stored98=true')
 # An unexpectedly jumped clear counter must never be counted as one replay
 # or start another unattended battle. The simulator changes P deliberately;
 # the replay module must not write further P fields or local saved storage.
 p.evaluate("""()=>{QUEST.missionId=1;S.busy=false;S.over=true;S.phase='Victory';
   window.__stored98=true;document.getElementById('auto').checked=false;}""")
 assert p.evaluate(api+'.start(2)') is True
 assert p.locator('#auto').is_checked()
 old_replays=p.evaluate('window.__repeatCount')
 p.evaluate("""()=>{P.questClears[1]+=2;S.over=true;S.phase='Victory';
   document.getElementById('auto').checked=false;}""")
 after_external=p.evaluate('JSON.stringify(P)')
 before_save=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 before_writes=p.evaluate('__v98StorageWrites')
 assert p.evaluate(api+'.poll()') is True
 assert p.evaluate(api+'.statusSnapshot().active') is False
 assert p.evaluate(api+'.statusSnapshot().completed')==0
 assert 'unexpected saved clear count' in p.evaluate(api+'.statusSnapshot().reason')
 assert not p.locator('#auto').is_checked()
 assert p.evaluate('window.__repeatCount')==old_replays
 assert p.evaluate('JSON.stringify(P)')==after_external
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before_save
 assert p.evaluate('__v98StorageWrites')==before_writes
 # Auto checkbox turning off is an immediate opt-out.
 p.evaluate("""()=>{S.over=true;S.phase='Victory'}""")
 assert p.evaluate(api+'.start(5)') is True
 p.locator('#auto').uncheck()
 assert p.evaluate(api+'.statusSnapshot().active') is False
 assert 'Auto Battle disabled' in p.evaluate(api+'.statusSnapshot().reason')
 # The actual native Android bridge may fire while document.hidden is
 # still false. A completed result must not replay on foreground return.
 java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
 bridge_match=re.search(r'private static final String UI_BACKGROUND_JS\s*=\s*("[^\n]+");',java)
 assert bridge_match
 native_background=json.loads(bridge_match[1])
 assert 'bf-native-background' in native_background
 p.evaluate("""()=>{window.__repeatHiddenSignals=0;
     document.addEventListener('visibilitychange',()=>__repeatHiddenSignals++);}""")
 for phase in ('running','completed'):
  p.evaluate("""()=>{QUEST.missionId=1;S.over=true;S.phase='Victory';
    document.getElementById('auto').checked=false;}""")
  assert p.evaluate(api+'.start(2)') is True
  if phase=='completed':
   p.evaluate("""()=>{P.questClears[1]++;S.over=true;S.phase='Victory';
     document.getElementById('auto').checked=false;}""")
  previous_replays=p.evaluate('window.__repeatCount')
  before_player=p.evaluate('JSON.stringify(P)')
  p.evaluate(native_background)
  assert p.evaluate('document.hidden') is False
  assert p.evaluate('__repeatHiddenSignals')==0
  assert p.evaluate(api+'.statusSnapshot().active') is False,(phase,'Native background left repeat armed')
  assert 'background' in p.evaluate(api+'.statusSnapshot().reason')
  assert not p.locator('#auto').is_checked()
  assert p.evaluate('JSON.stringify(P)')==before_player
  p.evaluate(api+'.poll()')
  assert p.evaluate('window.__repeatCount')==previous_replays,(phase,'Replay continued after Android pause')
 # Without an auto-repeat session the module must not interfere with ordinary
 # Auto controls. The real Android bridge calls Smart Auto separately first.
 p.locator('#auto').check()
 p.evaluate(native_background)
 assert p.locator('#auto').is_checked()
 p.locator('#auto').uncheck()
 # On browser-only background/close, Auto MUST stop too. Otherwise the
 # repeat session is disarmed but native Auto can keep running unattended.
 for signal in ('visibilitychange','pagehide'):
  p.evaluate("""()=>{QUEST.missionId=1;S.busy=false;S.over=true;
    S.phase='Victory';document.getElementById('auto').checked=false;}""")
  assert p.evaluate(api+'.start(2)') is True,signal
  assert p.locator('#auto').is_checked()
  previous_replays=p.evaluate('window.__repeatCount')
  before_player=p.evaluate('JSON.stringify(P)')
  if signal=='visibilitychange':
   p.evaluate("""()=>{Object.defineProperty(document,'hidden',{
     configurable:true,value:true});
     try{document.dispatchEvent(new Event('visibilitychange'));}
     finally{delete document.hidden;}
   }""")
  else:
   p.evaluate("window.dispatchEvent(new Event('pagehide'))")
  assert p.evaluate(api+'.statusSnapshot().active') is False,signal
  assert not p.locator('#auto').is_checked(),signal
  assert p.evaluate('JSON.stringify(P)')==before_player,signal
  assert p.evaluate(api+'.poll()') is False,signal
  assert p.evaluate('window.__repeatCount')==previous_replays,signal
 # Stop Repeating belongs to the player even while a battle action is
 # running. The ongoing round may complete, but an Auto setting owned by
 # the repeat session must not keep driving later rounds.
 p.evaluate("""()=>{const a=document.getElementById('auto');
   a.addEventListener('change',()=>{S.auto=a.checked;});}""")
 p.locator('#bf9800-auto-repeat > summary').click()
 for initial_auto in (False,True):
  p.evaluate("""before=>{
    QUEST.missionId=1;S.busy=false;S.over=true;S.phase='Victory';
    S.auto=before;document.getElementById('auto').checked=before;
  }""",initial_auto)
  assert p.evaluate(api+'.start(2)') is True
  assert p.locator('#auto').is_checked()
  p.evaluate('S.busy=true')
  before_player=p.evaluate('JSON.stringify(P)')
  previous_replays=p.evaluate('window.__repeatCount')
  p.locator('#bf9800-stop').click()
  assert not p.evaluate(api+'.statusSnapshot().active')
  assert p.evaluate(api+'.statusSnapshot().reason')=='Stopped by player'
  assert p.locator('#auto').is_checked()==initial_auto
  assert p.evaluate('S.auto')==initial_auto
  assert p.evaluate('S.busy') is True
  assert p.evaluate('window.__repeatCount')==previous_replays
  assert p.evaluate('JSON.stringify(P)')==before_player
  p.evaluate('S.busy=false')
 # Re-injecting must not duplicate intervals, panels or listeners.
 p.add_script_tag(path=str(A/'bf9800_qol_cleared_quest_repeat.js'))
 assert p.locator('#bf9800-auto-repeat').count()==1
 assert p.evaluate('P.version')==7
 assert not errors,errors
 b.close()
print('PASS v98 bounded replay: one clear per stored receipt, counter jump disarms Auto, Android pause and v7 isolation')
