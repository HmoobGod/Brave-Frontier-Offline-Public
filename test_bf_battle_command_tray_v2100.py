"""v21.00: queue same real demo buttons for all alive units, native target/execute, save safety."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf2100_battle_command_tray.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_BATTLE_COMMAND_TRAY_V2100 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src and 'finish(true)' not in src
assert java.index('readPackagedText("bf2000_story_battle_hud.js")')<java.index('readPackagedText("bf2100_battle_command_tray.js")')
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
              'bf2100_battle_command_tray.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf2100-tray').is_visible()
 assert page.evaluate('BFGlobalBattleCommandsV2100.snapshot().alive')==6
 before=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("fake")') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="attack")')
 assert page.evaluate('BFGlobalBattleCommandsV2100.snapshot().queued')==6
 assert not page.locator('#bf2100-execute').is_disabled()
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("guard")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="guard")')
 page.evaluate('S.party[0].bb=100;update()')
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("burst")') is True
 assert page.evaluate('S.party[0].action.kind')=='burst'
 assert page.evaluate('S.party.slice(1).every(p=>p.action.kind==="attack")')
 assert page.evaluate('BFGlobalBattleCommandsV2100.snapshot().bbReady')==1
 slots=page.evaluate('BFGlobalBattleCommandsV2100.snapshot().foes.map(e=>e.slot)')
 assert slots
 assert page.evaluate('(slot)=>BFGlobalBattleCommandsV2100.setTarget(slot)',slots[-1]) is True
 assert page.evaluate('S.target')==slots[-1]
 assert page.evaluate('BFGlobalBattleCommandsV2100.setTarget(9999)') is False
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.executeTurn()') is False
 page.evaluate('S.busy=false')
 page.locator('#auto').check()
 assert page.evaluate('BFGlobalBattleCommandsV2100.snapshot().auto') is True
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("guard")') is False
 page.locator('#auto').uncheck()
 page.evaluate('BFGlobalBattleCommandsV2100.refresh()')
 after=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'queue commands cannot change progress or v7 save'
 # Original Execute button still powers shortcut, and cannot execute when incomplete.
 page.evaluate('S.party[0].action=null;update()')
 assert page.evaluate('BFGlobalBattleCommandsV2100.executeTurn()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is True
 page.evaluate('for(const e of S.enemies)e.hp=e.maxHp=999999')
 assert page.evaluate('BFGlobalBattleCommandsV2100.executeTurn()') is True
 assert page.evaluate('S.busy') is True
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is False
 page.evaluate('reset()')
 assert page.evaluate('S.busy') is False
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v21.00: native queue buttons, target switching, BB fallback, busy/auto guards, execute and v7 isolation')
