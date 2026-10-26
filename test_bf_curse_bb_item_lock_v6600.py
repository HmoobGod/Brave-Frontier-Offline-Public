"""v66 Cure/Curse prevents source BB item from charging gauge or consuming DEMO stock."""
from pathlib import Path
import ast,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf4600_source_bb_gauge_item.js').read_text('utf8')
assert 'BFGlobalOriginalAilmentStateV5700?.codesFor(i).includes(5)' in js
source=ast.parse((R/'test_bf_status_reinfliction_v6300.py').read_text('utf8'))
names=next(ast.literal_eval(f.iter) for f in ast.walk(source)
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
 for name in names:p.add_script_tag(path=str(A/name))
 for name in ('bf6400_status_remedy_command.js','bf6500_sickness_recovery.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
  progress:JSON.stringify(P),hp:S.party.map(x=>x.hp)})""")
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.snapshot().remaining')==1
 assert 0 in p.evaluate('BFGlobalSourceBBGaugeItemV4600.snapshot().eligibleRecipients')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,5)') is True
 assert p.evaluate('BFGlobalCurseBBLockV5900.cursed(0)') is True
 assert 0 not in p.evaluate('BFGlobalSourceBBGaugeItemV4600.snapshot().eligibleRecipients')
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.useBBItem(1,0)') is False
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.snapshot().remaining')==1
 assert p.evaluate('S.party[0].bb')==0
 assert p.evaluate('S.party[1].action') is None
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20220).removed')==[5]
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.useBBItem(1,0)') is True
 assert p.evaluate('S.party[0].bb')==100
 assert p.evaluate('S.party[1].action.kind')=='guard'
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.snapshot().remaining')==0
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,5)') is True
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.useBBItem(2,0)') is False
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
  progress:JSON.stringify(P),hp:S.party.map(x=>x.hp)})""")
 assert before==after,(before,after)
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.snapshot().remaining')==1
 assert p.evaluate('BFGlobalCurseBBLockV5900.cursed(0)') is False
 assert 0 in p.evaluate('BFGlobalSourceBBGaugeItemV4600.snapshot().eligibleRecipients')
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.useBBItem(1,0)') is False
 assert not errors,errors
 b.close()
print('PASS v66 Curse blocks all BB item gauge charge, retains stock and actor action, cure restores eligible use, saves stable')
