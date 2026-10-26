"""v31.00 deterministic demo foe priority and queued squad attacks through existing controls."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf3100_battle_focus.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_PLAYABLE_FOCUS_ACTIONS_V3100 */')==1
assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf3000_battle_results.js")')<java.index('readPackagedText("bf3100_battle_focus.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
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
 'bf2900_original_event_expressions.js','bf3000_battle_results.js',
 'bf3100_battle_focus.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf3100-focus').is_visible()
 assert page.evaluate('BFGlobalBattleFocusV3100.snapshot().canQueue') is True
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("invalid")') is False
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("low","fake")') is False
 # Original source-gated mission selection, no fabricated foe wave table.
 page.evaluate('()=>{P.questClears[1]=1;renderQuestList();BFQuestAreas.choose(QUESTS.find(q=>q.missionId===2))}')
 before=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('S.enemies.length')==3
 page.evaluate("""()=>{const es=S.enemies;
 es[0].hp=390;es[0].atk=800;es[0].def=50;
 es[1].hp=75;es[1].atk=100;es[1].def=180;
 es[2].hp=760;es[2].atk=300;es[2].def=5;update()}""")
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("lowest-hp").slot')==1
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("highest-atk").slot')==0
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("lowest-def").slot')==2
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("highest-atk")') is True
 assert page.evaluate('S.target')==0
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="attack"&&p.action.target===1)')
 page.evaluate('S.party[0].bb=100;update()')
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-def","burst")') is True
 assert page.evaluate('S.party[0].action.kind')=='burst'
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.target===2)')
 assert page.evaluate('P.version')==7
 after=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 # The fixture explicitly selects a mission, so compare save for implicit writes, not transient P.lastMission.
 assert after['save']==before['save']
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("highest-atk")') is False
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp")') is False
 page.evaluate('S.busy=false')
 page.locator('#auto').check()
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp")') is False
 page.locator('#auto').uncheck()
 page.evaluate('finish(false)')
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("lowest-def")') is False
 assert not errors,errors
 browser.close()
print('PASS v31.00: three enemy focus strategies, native queue/BB, phase gates and no implicit saved rewards')
