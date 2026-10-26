"""v98: bounded cleared-mission automation driven only by verified result/replay."""
from pathlib import Path
import shutil
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
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011],squad:[10011],questClears:{1:1}};
   window.QUEST={missionId:1};
   window.S={mode:'archive',over:true,busy:false,phase:'Victory'};
   window.__repeatCount=0;
   const snapshot=()=>({missionId:QUEST.missionId,done:S.over,
     victory:S.over&&S.phase==='Victory',archive:S.mode==='archive',
     clears:P.questClears[QUEST.missionId]||0,canReplay:S.over&&!S.busy});
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
 assert p.evaluate(api+'.start(1)') is False
 assert p.evaluate(api+'.start(20)') is False
 assert p.evaluate(api+'.start(2)') is True
 assert p.evaluate('window.__repeatCount')==1
 assert p.locator('#auto').is_checked()
 assert p.evaluate(api+'.statusSnapshot().target')==2
 p.evaluate("""()=>{P.questClears[1]++;S.over=true;S.phase='Victory'}""")
 assert p.evaluate(api+'.poll()') is True
 assert p.evaluate('window.__repeatCount')==2
 assert p.evaluate(api+'.statusSnapshot().completed')==1
 p.evaluate("""()=>{P.questClears[1]++;S.over=true;S.phase='Victory'}""")
 assert p.evaluate(api+'.poll()') is True
 assert p.evaluate(api+'.statusSnapshot().active') is False
 assert p.evaluate(api+'.statusSnapshot().completed')==2
 assert not p.locator('#auto').is_checked()
 assert p.evaluate('window.__repeatCount')==2
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
 # Defeat stops repeats instead of replaying a loss.
 p.evaluate("""()=>{QUEST.missionId=1;S.over=true;S.phase='Victory'}""")
 assert p.evaluate(api+'.start(2)') is True
 p.evaluate("""()=>{S.over=true;S.phase='Defeat'}""")
 p.evaluate(api+'.poll()')
 assert p.evaluate(api+'.statusSnapshot().active') is False
 assert 'battle lost' in p.evaluate(api+'.statusSnapshot().reason')
 # Auto checkbox turning off is an immediate opt-out.
 p.evaluate("""()=>{S.over=true;S.phase='Victory'}""")
 assert p.evaluate(api+'.start(5)') is True
 p.locator('#auto').uncheck()
 assert p.evaluate(api+'.statusSnapshot().active') is False
 assert 'Auto Battle disabled' in p.evaluate(api+'.statusSnapshot().reason')
 # Re-injecting must not duplicate intervals, panels or listeners.
 p.add_script_tag(path=str(A/'bf9800_qol_cleared_quest_repeat.js'))
 assert p.locator('#bf9800-auto-repeat').count()==1
 assert p.evaluate('P.version')==7
 assert not errors,errors
 b.close()
print('PASS v98 bounded cleared-quest replay: two confirmed clears, stop/defeat/mode/auto and v7 isolation')
