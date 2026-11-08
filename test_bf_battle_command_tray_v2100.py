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
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)+'\n'+str(e.stack)))
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
 # The player can distribute manual attacks across all live enemies without
 # executing a turn, changing quest progress, or touching the canonical save.
 assert page.locator('#bf2100-spread').is_visible()
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadAttacks()') is True
 assigned=page.evaluate('S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action?.kind,p.action?.target])')
 living=page.evaluate('S.enemies.filter(e=>e.hp>0).map(e=>e.slot)')
 assert len(living)>=2
 assert assigned==[['attack',living[i%len(living)]] for i in range(len(assigned))],assigned
 assert not page.evaluate('S.busy')
 # After an enemy falls, the native target list may exclude that dead slot
 # instead of retaining a disabled placeholder. The tray must select the
 # intended surviving target through the real native button either way.
 page.evaluate("""()=>{const e=S.enemies[0];
   S.enemies=[{...e,slot:0,name:'Defeated',hp:0,maxHp:100},
              {...e,slot:1,name:'Survivor A',hp:100,maxHp:100},
              {...e,slot:2,name:'Survivor B',hp:200,maxHp:200}];
   update()}""")
 assert page.evaluate('BFGlobalBattleCommandsV2100.setTarget(0)') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.setTarget(2)') is True
 assert page.evaluate('S.target')==2
 assert page.evaluate('BFGlobalBattleCommandsV2100.setTarget(1)') is True
 assert page.evaluate('S.target')==1
 assert page.evaluate('S.enemies[0].hp')==0
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadAttacks()') is True
 assigned=page.evaluate('S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action?.kind,p.action?.target])')
 assert assigned==[['attack',1 if i%2==0 else 2] for i in range(len(assigned))],assigned
 assert page.evaluate('S.enemies[0].hp')==0
 # A broken live foe (or duplicate slot) makes the native button-to-enemy
 # mapping unsafe. Fail before clicking, without exposing corrupt temporary
 # records to the browser renderer between evaluation tasks.
 invalid_results=page.evaluate("""()=>{const original=S.enemies;
   const selected=S.target,seed=original[1];
   const good={...seed,slot:2,hp:100,maxHp:200};
   const cases=[
     [{...seed,slot:1,hp:40,maxHp:0},good],
     [{...seed,slot:1,hp:Infinity,maxHp:100},good],
     [{...seed,slot:-1,hp:40,maxHp:100},good],
     [{...seed,slot:2,hp:40,maxHp:100},good],
     [{...seed,slot:1,hp:40},good]
   ];
   try{
     return cases.map(foes=>{
       S.enemies=foes;
       return BFGlobalBattleCommandsV2100.setTarget(2);
     });
   }finally{S.enemies=original;S.target=selected;}
 }""")
 assert invalid_results==[False]*5,invalid_results
 assert page.evaluate('S.enemies[0].hp')==0
 # Source-backed elemental matchup option uses the original 2022 six-element
 # relationship, but never invents unknown demo enemy/ally elements or damage.
 assert page.locator('#bf2100-elements').is_visible()
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementPlan()') is None
 page.add_script_tag(path=str(A/'bf6900_elemental_combat.js'))
 assert page.evaluate('BFGlobalElementalCombatV6900.normalize("Fire")')=='Fire'
 assert page.evaluate('UNIT_BY_ID.get(10011).element')=='Fire'
 page.evaluate("""()=>{S.party.forEach(p=>{if(p.active)p.unitId=10011});
   S.enemies[1].element='Earth';S.enemies[2].element='Water';update()}""")
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementPlan().length')==6
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementPlan().every(x=>x.target===1&&!x.reserved)')
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementAttacks()') is True
 assigned=page.evaluate('S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action?.kind,p.action?.target])')
 assert assigned==[['attack',1] for _ in assigned],assigned
 assert not page.evaluate('S.busy')
 # An unknown source ally must fail before any player orders change.
 saved_orders=page.evaluate('S.party.map(p=>JSON.stringify(p.action))')
 # The live renderer reads UNIT_BY_ID for animation on every RAF. Never
 # expose a deliberately invalid unit ID across separate evaluate calls.
 # Run the negative preflight and immediately restore source identity.
 unknown=page.evaluate("""()=>{const old=S.party[0].unitId;
   const before=S.party.map(p=>JSON.stringify(p.action));
   try{
     S.party[0].unitId=999999;
     return {noPlan:BFGlobalBattleCommandsV2100.elementPlan()===null,
       rejected:BFGlobalBattleCommandsV2100.elementAttacks()===false,
       unchanged:before.every((order,i)=>order===JSON.stringify(S.party[i].action))};
   }finally{S.party[0].unitId=old;}
 }""")
 assert unknown=={'noPlan':True,'rejected':True,'unchanged':True},unknown
 assert page.evaluate('S.party.map(p=>JSON.stringify(p.action))')==saved_orders
 # With no advantageous foe, the option refuses to overwrite previous orders.
 page.evaluate("S.enemies[1].element='Water';update()")
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementPlan()') is None
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementAttacks()') is False
 assert page.evaluate('S.party.map(p=>JSON.stringify(p.action))')==saved_orders
 # Restore a favorable foe before testing busy / Auto rejection.
 page.evaluate("S.enemies[1].element='Earth';update()")
 # Still only commands queued: this source-level action cannot award rewards.
 assert not page.evaluate('S.busy')
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadAttacks()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementAttacks()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.executeTurn()') is False
 page.evaluate('S.busy=false')
 page.locator('#auto').check()
 assert page.evaluate('BFGlobalBattleCommandsV2100.snapshot().auto') is True
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("guard")') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadAttacks()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementAttacks()') is False
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
print('PASS v21.00: native queue, spread and source-backed element attacks, KO target, busy/auto guards, v7 isolation')
