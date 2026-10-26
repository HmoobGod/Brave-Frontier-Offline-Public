"""v76 source + historical original status Nullifier prevents all six ailments for 3 turns."""
from pathlib import Path
import ast,json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
e=json.loads((R/'source_data/bf_global_2022_status_nullifier_v7600.json').read_text('utf8'))
assert e['provenance']['sourceSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
assert (e['item']['itemId'],e['item']['itemTargetArea'],e['item']['passiveSkillInfo'])==(
 20250,2,'100,100,100,100,100,100,3,0')
js=(A/'bf7600_original_status_nullifier.js').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
ail=(A/'bf5700_original_ailment_state.js').read_text('utf8')
assert 'BFGlobalStatusNegationV7600?.immune(slot,code)' in ail
turns=(A/'bf4500_item_turn_reservations.js').read_text('utf8')
assert "'nullifier-demo'" in turns
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf5700_original_ailment_state.js")')<java.index('readPackagedText("bf7600_original_status_nullifier.js")')
# Load the exact prereqs like v63's full gameplay test, plus source-v75.
src=ast.parse((R/'test_bf_status_reinfliction_v6300.py').read_text('utf8'))
names=next(ast.literal_eval(f.iter) for f in ast.walk(src)
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
              'bf7500_original_saint_light.js','bf7600_original_status_nullifier.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('P.version')==7
 original=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 progress:JSON.stringify(P),hp:S.party.map(x=>x.hp),bb:S.party.map(x=>x.bb)})""")
 assert p.evaluate('BFGlobalStatusNegationV7600.source.itemId')==20250
 assert p.evaluate('BFGlobalStatusNegationV7600.snapshot().remaining')==1
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(2,5)') is True
 assert p.evaluate('BFGlobalStatusNegationV7600.useNullifier(0)') is True
 assert p.evaluate('BFGlobalStatusNegationV7600.snapshot().active') is True
 assert p.evaluate('BFGlobalStatusNegationV7600.snapshot().protectedSlots.length')==6
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(2)')==[5]
 for slot in (0,1,2,3,4,5):
  for code in (1,2,3,4,5,6):
   assert p.evaluate(f'BFGlobalOriginalAilmentStateV5700.inflict({slot},{code})') is False,(slot,code)
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(2)')==[5]
 assert p.evaluate('S.party[0].action.kind')=='guard'
 assert p.evaluate('BFGlobalStatusNegationV7600.snapshot().remaining')==0
 assert p.evaluate('BFGlobalStatusNegationV7600.useNullifier(1)') is False
 assert p.evaluate('BFGlobalStatusNegationV7600.expireAfterTurn()')==[]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalStatusNegationV7600.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalStatusNegationV7600.immune(1,4)') is True
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalStatusNegationV7600.expireAfterTurn()')==[0,1,2,3,4,5]
 assert p.evaluate('BFGlobalStatusNegationV7600.snapshot().active') is False
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(1,1)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(1,20200).removed')==[1]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(2,20220).removed')==[5]
 restored=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 progress:JSON.stringify(P),hp:S.party.map(x=>x.hp),bb:S.party.map(x=>x.bb)})""")
 assert original==restored
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalStatusNegationV7600.useNullifier(1)') is False
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalStatusNegationV7600.snapshot().remaining')==1
 assert p.evaluate('BFGlobalStatusNegationV7600.snapshot().active') is False
 assert not errors,errors
 b.close()
print('PASS v76 source Nullifier 3-turn all-ally ailments prevention, retains existing statuses, Guard, cures, save')
