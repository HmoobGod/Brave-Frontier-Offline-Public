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
 assert p.locator('#bf9800-repeat-count option').count()==4
 assert p.locator('#bf9800-repeat-count').input_value()=='2'
 assert p.evaluate(api+'.start(0)') is False
 assert p.evaluate(api+'.start(20)') is False
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
