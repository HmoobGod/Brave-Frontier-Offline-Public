"""v72 original 2022 Potion #20000 base 100-120 alongside legacy +500 demo."""
from pathlib import Path
import ast,json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
data=json.loads((R/'source_data/bf_global_2022_original_potion_v7200.json').read_text('utf8'))
assert data['provenance']['sourceSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
i=data['item']
assert (i['itemId'],i['itemTargetArea'],i['skillTypeId'])==(20000,1,2)
assert i['passiveSkillInfo']=='100,120,0,0' and data['semantics']['sourceBaseRange']==[100,120]
js=(A/'bf4200_demo_potion_command.js').read_text('utf8')
assert 'original-potion-demo' in js and 'useSourcePotion' in js
assert "passiveSkillInfo:'100,120,0,0'" in js
assert 'Math.floor(Math.random()*(original.baseHigh-original.baseLow+1))' in js
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
ledger=(A/'bf4500_item_turn_reservations.js').read_text('utf8')
assert "'original-potion-demo'" in ledger
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf4500_item_turn_reservations.js")')<j.index('readPackagedText("bf4200_demo_potion_command.js")')
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
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
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
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().source.itemId')==20000
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().sourceRemaining')==1
 assert p.locator('#bf7200-use').is_disabled()
 p.evaluate('S.party[0].hp-=300')
 p.evaluate('S.party[1].hp-=700')
 before=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 before_hp=p.evaluate('S.party[0].hp')
 assert p.evaluate('BFGlobalDemoPotionV4200.useSourcePotion(0)') is True
 amount=p.evaluate('S.party[0].hp')-before_hp
 assert 100<=amount<=120,amount
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().sourceRemaining')==0
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==3
 assert p.evaluate('S.party[0].action.kind')=='guard'
 assert p.evaluate("BFGlobalItemTurnReservationsV4500.snapshot().reservations[0].kind")=='original-potion-demo'
 p.evaluate('S.party[0].action=null')
 assert p.evaluate('BFGlobalDemoPotionV4200.usePotion(0)') is False
 assert p.evaluate('BFGlobalDemoPotionV4200.useSourcePotion(0)') is False
 legacy_hp=p.evaluate('S.party[1].hp')
 assert p.evaluate('BFGlobalDemoPotionV4200.usePotion(1)') is True
 assert p.evaluate('S.party[1].hp')==legacy_hp+500
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==2
 assert p.locator('#bf7200-legacy').count()==1
 after=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,(before,after)
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalDemoPotionV4200.useSourcePotion(1)') is False
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().sourceRemaining')==1
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==3
 assert not errors,errors
 b.close()
print('PASS v72 source Potion #20000 100..120 DEMO healing, retained legacy +500, Guard and saved data isolation')
