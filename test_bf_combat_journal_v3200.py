"""v32.00 captures native demo combat history in memory across one reset, no save changes."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf3200_combat_journal.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_PLAYABLE_COMBAT_JOURNAL_V3200 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf3100_battle_focus.js")')<java.index('readPackagedText("bf3200_combat_journal.js")')
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
  'bf2900_original_event_expressions.js','bf3000_battle_results.js',
  'bf3100_battle_focus.js','bf3200_combat_journal.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf3200-journal').is_visible()
 assert page.evaluate('BFGlobalCombatJournalV3200.snapshot().capacity')==400
 assert page.evaluate('BFGlobalCombatJournalV3200.show("previous")') is False
 assert page.evaluate('BFGlobalCombatJournalV3200.show("bogus")') is False
 before=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('()=>{for(let i=0;i<30;i++)msg("COMBAT_JOURNAL_ENTRY_"+i)}')
 page.wait_for_function('BFGlobalCombatJournalV3200.snapshot().current >= 30')
 assert page.evaluate('document.querySelector("#log").children.length')<=9
 report=page.evaluate('BFGlobalCombatJournalV3200.report("current")')
 assert 'COMBAT_JOURNAL_ENTRY_0' in report and 'COMBAT_JOURNAL_ENTRY_29' in report
 assert 'Source enemy identities and AI are not restored' in report
 page.evaluate('finish(false)')
 page.evaluate('reset()')
 page.wait_for_function('BFGlobalCombatJournalV3200.snapshot().previous >= 30')
 assert page.evaluate('BFGlobalCombatJournalV3200.show("previous")') is True
 assert 'COMBAT_JOURNAL_ENTRY_0' in page.locator('#bf3200-report').input_value()
 assert 'COMBAT_JOURNAL_ENTRY_29' in page.locator('#bf3200-report').input_value()
 page.evaluate('BFGlobalCombatJournalV3200.show("current")')
 assert 'COMBAT_JOURNAL_ENTRY_29' not in page.locator('#bf3200-report').input_value()
 after=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'journal and defeat/restart must not change saved progression'
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v32.00: retained complete 30+ event log across reset, accurate previous run, v7 isolation')
