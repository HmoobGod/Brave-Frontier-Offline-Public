"""v80 original Weakness -50% subtractively with +30/+50/+100% DEF support."""
from pathlib import Path
import ast,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf6100_weakness_defense.js').read_text('utf8')
assert 'BF_GLOBAL_WEAKNESS_DEFENSE_V6100' in js
assert 'documentedDefBuff(slot)' in js and 'documented.baseDef*(.5+documented.pct/100)' in js
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
tree=ast.parse((R/'test_bf_status_reinfliction_v6300.py').read_text('utf8'))
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
 for name in names:p.add_script_tag(path=str(A/name))
 for name in ('bf6400_status_remedy_command.js','bf6500_sickness_recovery.js',
              'bf7500_original_saint_light.js','bf7600_original_status_nullifier.js',
              'bf7700_original_party_regen.js','bf7800_live_battle_status.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 before=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),
 hp:S.party.map(u=>u.hp),def:S.party.map(u=>u.def),atk:S.party.map(u=>u.atk)})""")
 initial=before['def']
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(3,2)') is True
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.effectiveDefense(3)')==(initial[3]+1)//2
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(3,20210).removed')==[2]
 # Unique source buff owners: v49 single +30%, v52 double +100%,
 # v53 party +50% (unbuffed remaining squad only).
 assert p.evaluate('BFGlobalSourceDefItemV4900.useDefItem(0,3)') is True
 assert p.evaluate('BFGlobalSourceDoubleDefV5200.useDoubleDef(1,4)') is True
 assert p.evaluate('BFGlobalSourcePartyDefV5300.usePartyDef(2)') is True
 records=p.evaluate("""()=>({
  single:BFGlobalSourceDefItemV4900.snapshot().activeBuffs,
  double:BFGlobalSourceDoubleDefV5200.snapshot().activeBuffs,
  party:BFGlobalSourcePartyDefV5300.snapshot().activeBuffs
 })""")
 assert [x['slot'] for x in records['single']]==[3]
 assert [x['slot'] for x in records['double']]==[4]
 assert 5 in [x['slot'] for x in records['party']]
 buffed=p.evaluate('S.party.map(u=>u.def)')
 assert buffed[3]>=initial[3] and buffed[4]>=initial[4] and buffed[5]>=initial[5]
 for slot in (3,4,5):assert p.evaluate(f'BFGlobalOriginalAilmentStateV5700.inflict({slot},2)') is True
 values={3:30,4:100,5:50}
 expected={slot:int(initial[slot]*(0.5+pct/100)+.5) for slot,pct in values.items()}
 for slot in values:
  assert p.evaluate(f'BFGlobalWeaknessDefenseV6100.effectiveDefense({slot})')==expected[slot]
 seen=p.evaluate("""async()=>BFGlobalWeaknessDefenseV6100.withWeaknessDefense(async()=>({
  s3:S.party[3].def,s4:S.party[4].def,s5:S.party[5].def
 }))""")
 assert seen=={'s3':expected[3],'s4':expected[4],'s5':expected[5]},(seen,expected)
 assert p.evaluate('S.party.map(u=>u.def)')==buffed
 assert p.evaluate("""async()=>{
 try{await BFGlobalWeaknessDefenseV6100.withWeaknessDefense(async()=>{throw Error('aborted-enemy-phase')})}
 catch(e){return e.message==='aborted-enemy-phase'}return false}""") is True
 assert p.evaluate('S.party.map(u=>u.def)')==buffed
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(4,20210).removed')==[2]
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.effectiveDefense(4)')==buffed[4]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(3)')==[2]
 # Source buffs expire independently. Weakness remains until its own turn hook.
 p.evaluate('S.round+=3')
 p.evaluate("""()=>{BFGlobalSourceDefItemV4900.snapshot();
 BFGlobalSourceDoubleDefV5200.snapshot();BFGlobalSourcePartyDefV5300.snapshot();}""")
 assert p.evaluate('S.party.map(u=>u.def)')==initial
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.effectiveDefense(3)')==(initial[3]+1)//2
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.effectiveDefense(5)')==(initial[5]+1)//2
 for slot in (3,5):
  assert p.evaluate(f'BFGlobalOriginalAilmentStateV5700.cure({slot},20210).removed')==[2]
 after=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),
 hp:S.party.map(u=>u.hp),def:S.party.map(u=>u.def),atk:S.party.map(u=>u.atk)})""")
 assert before==after,(before,after)
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.snapshot().weakenedSlots')==[]
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.snapshot().weakenedSlots')==[]
 assert not errors,errors
 b.close()
print('PASS v80 additive Weakness penalty with +30/+50/+100 DEF original item bonuses, no stat/save leakage')
