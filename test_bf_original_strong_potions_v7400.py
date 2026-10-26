"""v74 two source-exact stronger healing items use one ally target and Guard actor."""
from pathlib import Path
import ast,json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
e=json.loads((R/'source_data/bf_global_2022_strong_potions_v7400.json').read_text('utf8'))
assert e['provenance']['fileSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
assert [(x['itemId'],x['itemTargetArea'],x['passiveSkillInfo']) for x in e['items']]==[
 (20001,1,'1000,1000,0,0'),(20002,1,'2000,2000,0,0')]
js=(A/'bf7400_original_strong_potions.js').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert all(v not in js for v in ('localStorage','saveProgress(', 'BFAndroid'))
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf4200_demo_potion_command.js")')<j.index('readPackagedText("bf7400_original_strong_potions.js")')
tree=ast.parse((R/'test_bf_source_party_heal_v4300.py').read_text('utf8'))
names=next(ast.literal_eval(f.iter) for f in ast.walk(tree)
 if isinstance(f,ast.For) and isinstance(f.target,ast.Name) and f.target.id=='name'
 and isinstance(f.iter,ast.Tuple))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
 args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
 key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in names:
  if name=='bf4200_demo_potion_command.js':
   p.add_script_tag(path=str(A/'bf4500_item_turn_reservations.js'))
  p.add_script_tag(path=str(A/name))
 p.add_script_tag(path=str(A/'bf7400_original_strong_potions.js'))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.source.items.map(x=>[x.itemId,x.healing])')==[[20001,1000],[20002,2000]]
 assert p.locator('#bf7400-potions').is_visible()
 assert p.locator('#bf7400-use').is_disabled()
 p.evaluate("""()=>{S.party[0].hp=S.party[0].maxHp;S.party[1].hp=Math.max(1,S.party[1].maxHp-2100);
 S.party[2].hp=0;S.party[3].hp=Math.max(1,S.party[3].maxHp-500)}""")
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),P:JSON.stringify(P)})""")
 hp=p.evaluate('S.party.map(x=>x.hp)')
 maxHp=p.evaluate('S.party.map(x=>x.maxHp)')
 assert 0 in p.evaluate('BFGlobalOriginalStrongPotionsV7400.snapshot().actors')
 assert 1 in p.evaluate('BFGlobalOriginalStrongPotionsV7400.snapshot().recipients')
 assert 2 not in p.evaluate('BFGlobalOriginalStrongPotionsV7400.snapshot().recipients')
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.usePotion(0,2,20001)') is False
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.usePotion(0,0,20001)') is False
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.usePotion(0,1,20001)') is True
 assert p.evaluate('S.party[1].hp')==min(maxHp[1],hp[1]+1000)
 assert p.evaluate('S.party[0].hp')==hp[0]
 assert p.evaluate('S.party[0].action.kind')=='guard'
 assert p.evaluate('S.party[1].action') is None
 assert p.evaluate("BFGlobalItemTurnReservationsV4500.snapshot().reservations[0].kind")=='strong-potion-demo'
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.usePotion(0,3,20002)') is False
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.usePotion(4,3,20001)') is False
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.snapshot().stock.map(x=>x.remaining)')==[0,1]
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.usePotion(4,3,20002)') is True
 assert p.evaluate('S.party[3].hp')==maxHp[3]
 assert p.evaluate('S.party[4].action.kind')=='guard'
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.snapshot().stock.map(x=>x.remaining)')==[0,0]
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().sourceRemaining')==1
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==3
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),P:JSON.stringify(P)})""")
 assert before==after,(before,after)
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.usePotion(5,1,20002)') is False
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalOriginalStrongPotionsV7400.snapshot().stock.map(x=>x.remaining)')==[1,1]
 p.evaluate('S.party[1].hp=Math.max(1,S.party[1].maxHp-1500)')
 p.evaluate('BFGlobalOriginalStrongPotionsV7400.refresh()')
 p.locator('#bf7400-potions summary').click()
 p.locator('#bf7400-item').select_option('20001')
 p.locator('#bf7400-actor').select_option('0')
 p.locator('#bf7400-target').select_option('1')
 hp=p.evaluate('S.party[1].hp')
 p.locator('#bf7400-use').click()
 assert p.evaluate('S.party[1].hp')-hp==min(1000,p.evaluate('S.party[1].maxHp')-hp)
 assert not errors,errors
 b.close()
print('PASS v74 original 2022 strong recovery potions #20001/#20002, exact healing, Guard, KO, mode, stock, save isolation')
