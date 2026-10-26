"""v77 source Regeneration Light: 3 turns, ally scope, non-KO, no saved data edits."""
from pathlib import Path
import ast,json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_2022_regeneration_light_v7700.json').read_text('utf8'))
assert source['provenance']['tableSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
item=source['item']
assert (item['itemId'],item['itemTargetArea'],item['skillTypeId'],item['passiveSkillInfo'])==(
 20102,2,3,'800,1000,0,3,0')
js=(A/'bf7700_original_party_regen.js').read_text('utf8')
assert 'BF_GLOBAL_ORIGINAL_PARTY_REGEN_V7700' in js and len(js.encode('utf8'))<65536
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf7600_original_status_nullifier.js")')<java.index('readPackagedText("bf7700_original_party_regen.js")')
tree=ast.parse((R/'test_bf_status_reinfliction_v6300.py').read_text('utf8'))
names=next(ast.literal_eval(f.iter) for f in ast.walk(tree)
 if isinstance(f,ast.For) and isinstance(f.target,ast.Name) and f.target.id=='name'
 and isinstance(f.iter,ast.Tuple))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
 args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda x:errors.append(str(x)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in names:p.add_script_tag(path=str(A/name))
 for name in ('bf6400_status_remedy_command.js','bf6500_sickness_recovery.js',
   'bf7500_original_saint_light.js','bf7600_original_status_nullifier.js',
   'bf7700_original_party_regen.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('P.version')==7
 base=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),P:JSON.stringify(P)})""")
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.source.itemId')==20102
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().remaining')==1
 p.evaluate("""()=>{S.party[1].maxHp=8000;S.party[1].hp=100;
 S.party[2].hp=0;}""")
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.useRegeneration(2)') is False
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.useRegeneration(0)') is True
 assert p.evaluate('S.party[0].action.kind')=='guard'
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().remaining')==0
 assert 2 not in p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().targetSlots')
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.useRegeneration(4)') is False
 baseHp=p.evaluate('S.party[1].hp')
 total=0
 for step in range(3):
  if step:p.evaluate('S.round++')
  events=p.evaluate('BFGlobalOriginalPartyRegenV7700.processTurn()')
  h=next(x['healed'] for x in events if x['slot']==1)
  assert 800<=h<=1000,(step,h)
  total+=h
  assert p.evaluate('BFGlobalOriginalPartyRegenV7700.processTurn()')==[]
 assert p.evaluate('S.party[1].hp')==baseHp+total
 assert p.evaluate('S.party[2].hp')==0
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().active') is False
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().remaining')==0
 assert p.evaluate('BFGlobalSourcePartyHealV4300.snapshot().remaining')==1
 end=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),P:JSON.stringify(P)})""")
 assert base==end
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.useRegeneration(3)') is False
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().remaining')==1
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().active') is False
 p.evaluate('S.party[1].maxHp=8000;S.party[1].hp=100')
 p.evaluate('BFGlobalOriginalPartyRegenV7700.refresh()')
 p.locator('#bf7700-party-regen summary').click()
 p.locator('#bf7700-actor').select_option('0')
 p.locator('#bf7700-use').click()
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().active') is True
 # Clear a wave without an enemy phase, then advance past the buff end.
 p.evaluate('S.round+=4')
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().active') is False
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.processTurn()')==[]
 assert not errors,errors
 b.close()
print('PASS v77 gradual 3-turn original party recovery identity, no double ticks, KO, Guard, reset, saves')
