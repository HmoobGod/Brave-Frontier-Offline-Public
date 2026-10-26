"""v73 original Potion #20000 can heal an ally other than the actor."""
from pathlib import Path
import ast,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf4200_demo_potion_command.js').read_text('utf8')
assert 'function useSourcePotion(actorId,targetId=actorId)' in js
assert 'recipient.hp+=healed;' in js and 'caster.action=' in js
assert 'useSourcePotion(Number(sourceActor.value),Number(sourceTarget.value))' in js
assert "passiveSkillInfo:'100,120,0,0'" in js
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
tree=ast.parse((R/'test_bf_source_party_heal_v4300.py').read_text('utf8'))
names=next(ast.literal_eval(f.iter) for f in ast.walk(tree)
 if isinstance(f,ast.For) and isinstance(f.target,ast.Name) and f.target.id=='name'
 and isinstance(f.iter,ast.Tuple))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
 executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
 args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
 get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in names:
  if name=='bf4200_demo_potion_command.js':
   p.add_script_tag(path=str(A/'bf4500_item_turn_reservations.js'))
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 potion=p.evaluate('BFGlobalDemoPotionV4200')
 assert potion['source']['itemId']==20000
 assert p.locator('#bf7300-actor').count()==1
 assert p.locator('#bf7300-target').count()==1
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().sourceRemaining')==1
 assert p.locator('#bf7200-use').is_disabled()
 p.evaluate("""()=>{S.party[0].hp=S.party[0].maxHp;
   S.party[1].hp=Math.max(1,S.party[1].maxHp-300);
   S.party[2].hp=0;
   S.party[3].hp=Math.max(1,S.party[3].maxHp-60);}""")
 before=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 allhp=p.evaluate('S.party.map(x=>x.hp)')
 actors=p.evaluate('BFGlobalDemoPotionV4200.snapshot().sourceActors')
 targets=p.evaluate('BFGlobalDemoPotionV4200.snapshot().sourceTargets')
 assert 0 in actors and 0 not in targets
 assert 1 in targets and 2 not in targets
 assert p.evaluate('BFGlobalDemoPotionV4200.useSourcePotion(0,0)') is False
 assert p.evaluate('BFGlobalDemoPotionV4200.useSourcePotion(0,2)') is False
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().sourceRemaining')==1
 assert p.evaluate('BFGlobalDemoPotionV4200.useSourcePotion(0,1)') is True
 assert p.evaluate('S.party[0].hp')==allhp[0]
 heal=p.evaluate('S.party[1].hp')-allhp[1]
 assert 100<=heal<=120
 assert p.evaluate('S.party[2].hp')==allhp[2]
 assert p.evaluate('S.party[0].action.kind')=='guard'
 assert p.evaluate('S.party[1].action') is None
 assert p.evaluate("BFGlobalItemTurnReservationsV4500.snapshot().reservations[0].slot")==0
 assert p.evaluate("BFGlobalItemTurnReservationsV4500.snapshot().reservations[0].kind")=='original-potion-demo'
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().sourceRemaining')==0
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==3
 p.evaluate('S.party[0].action=null')
 assert p.evaluate('BFGlobalDemoPotionV4200.usePotion(0)') is False
 assert p.evaluate('BFGlobalDemoPotionV4200.useSourcePotion(0,1)') is False
 assert p.evaluate('BFGlobalDemoPotionV4200.usePotion(1)') is True
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==2
 after=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalDemoPotionV4200.useSourcePotion(4,1)') is False
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().sourceRemaining')==1
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==3
 # Verify UI selection operates independently of the legacy potion selector.
 p.evaluate('S.party[4].hp=Math.max(1,S.party[4].maxHp-400)')
 p.evaluate('BFGlobalDemoPotionV4200.refresh()')
 p.locator('#bf7300-actor').select_option('0')
 p.locator('#bf7300-target').select_option('4')
 hp=p.evaluate('S.party[4].hp')
 p.locator('#bf7200-use').click()
 assert 100<=p.evaluate('S.party[4].hp')-hp<=120
 assert p.evaluate('S.party[0].action.kind')=='guard'
 assert not errors,errors
 b.close()
print('PASS v73 original Potion one-ally target independent of acting unit, UI, stock, legacy, saves')