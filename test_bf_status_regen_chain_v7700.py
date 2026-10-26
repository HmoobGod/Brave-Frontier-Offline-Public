"""v77 integration: real chained enemyPhase hooks for original Nullifier and Regen."""
from pathlib import Path
import ast,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
tree=ast.parse((R/'test_bf_status_reinfliction_v6300.py').read_text('utf8'))
names=next(ast.literal_eval(f.iter) for f in ast.walk(tree)
 if isinstance(f,ast.For) and isinstance(f.target,ast.Name) and f.target.id=='name'
 and isinstance(f.iter,ast.Tuple))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
 executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
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
 for name in names:
  # Stub only the native enemy phase. Real source-status wrappers then attach
  # exactly as they do in Android, but no random monster attacks interfere.
  if name=='bf5800_poison_turn.js':
   p.evaluate("""()=>{window.__bfNativeEnemyPhase=window.enemyPhase;
    window.__mockEnemyCalls=0;
    window.enemyPhase=async function(){window.__mockEnemyCalls++;return 'phase';}}""")
  p.add_script_tag(path=str(A/name))
 for name in ('bf6400_status_remedy_command.js','bf6500_sickness_recovery.js',
              'bf7500_original_saint_light.js','bf7600_original_status_nullifier.js',
              'bf7700_original_party_regen.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('P.version')==7
 before=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 p.evaluate('S.party[1].maxHp=8000;S.party[1].hp=100')
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.useRegeneration(0)') is True
 assert p.evaluate('BFGlobalStatusNegationV7600.useNullifier(3)') is True
 assert p.evaluate('BFGlobalStatusNegationV7600.immune(1,1)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(1,1)') is False
 last=100
 for round_number in (1,2,3):
  assert p.evaluate('S.round')==round_number
  assert p.evaluate('async()=>window.enemyPhase()')=='phase'
  hp=p.evaluate('S.party[1].hp')
  gained=hp-last
  assert 800<=gained<=1000,(round_number,gained)
  last=hp
  # Even accidentally reentering the chained wrapped native hook in
  # the same round cannot make Regeneration apply a second time.
  assert p.evaluate('async()=>window.enemyPhase()')=='phase'
  assert p.evaluate('S.party[1].hp')==last
  if round_number<3:
   assert p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().active') is True
   assert p.evaluate('BFGlobalStatusNegationV7600.snapshot().active') is True
   p.evaluate('S.round++')
 assert p.evaluate('window.__mockEnemyCalls')==6
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.snapshot().active') is False
 assert p.evaluate('BFGlobalStatusNegationV7600.snapshot().active') is False
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(1,1)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(1,20200).removed')==[1]
 after=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after
 assert not errors,errors
 b.close()
print('PASS v77 native phase hook chain: 3 Regen ticks, Nullifier expiry, no double ticks, v7 isolation')
