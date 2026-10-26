"""v79 additive Injury penalty -50% ATK after positive source support effects."""
from pathlib import Path
import ast,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
module=(A/'bf6200_injury_attack.js').read_text('utf8')
assert module.count('BF_GLOBAL_INJURY_ATTACK_V6200')==1
assert 'Math.round(originalAtk*(multiplier-.5))' in module
assert 'desired/multiplier' in module
assert all(x not in module for x in ('localStorage','saveProgress(', 'BFAndroid'))
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
 atk:S.party.map(u=>u.atk),def:S.party.map(u=>u.def),rec:S.party.map(u=>u.rec)})""")
 base=before['atk']
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(3,4)') is True
 assert p.evaluate('BFGlobalInjuryAttackV6200.effectiveAttack(3)')==(base[3]+1)//2
 assert p.evaluate('BFGlobalSourceDoubleAtkV5100.useDoubleAtk(1,3)') is True
 assert p.evaluate('currentAtkBoost(S.party[3])')==100
 expected=int(base[3]*1.5+0.5)
 assert p.evaluate('BFGlobalInjuryAttackV6200.effectiveAttack(3)')==expected
 during=p.evaluate("""async()=>BFGlobalInjuryAttackV6200.withInjuryAttack(3,
 async()=>({actual:effectivePlayerAtk(S.party[3]),pct:currentAtkBoost(S.party[3])}))""")
 assert during=={'actual':expected,'pct':100}
 assert p.evaluate('S.party[3].atk')==base[3]
 assert p.evaluate('effectivePlayerAtk(S.party[3])')==base[3]*2
 # Source-backed +30% and +50% positive effects use the same additive
 # -50% Injury penalty without leaking base-stat changes.
 for slot,pct in ((0,30),(2,50)):
  p.evaluate(f'S.party[{slot}].atkBuff={{pct:{pct},untilRound:S.round+2}}')
  assert p.evaluate(f'BFGlobalOriginalAilmentStateV5700.inflict({slot},4)') is True
  expected=int(base[slot]*(1+pct/100-.5)+.5)
  assert p.evaluate(f'BFGlobalInjuryAttackV6200.effectiveAttack({slot})')==expected
  actual=p.evaluate(f"""async()=>BFGlobalInjuryAttackV6200.withInjuryAttack({slot},
  async()=>effectivePlayerAtk(S.party[{slot}]))""")
  assert actual==expected,(slot,pct,actual,expected)
  assert p.evaluate(f'S.party[{slot}].atk')==base[slot]
 # Exceptions restore live combat stats and do not mutate saved data.
 assert p.evaluate("""async()=>{
 try{await BFGlobalInjuryAttackV6200.withInjuryAttack(3,async()=>{throw Error('aborted-action')})}
 catch(e){return e.message==='aborted-action'}return false}""") is True
 assert p.evaluate('S.party.map(u=>u.atk)')==base
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(3,20210).removed')==[4]
 assert p.evaluate('BFGlobalInjuryAttackV6200.effectiveAttack(3)')==base[3]*2
 # Expired support boost removes only its bonus; the ailment continues.
 p.evaluate('S.round+=3')
 assert p.evaluate('BFGlobalInjuryAttackV6200.effectiveAttack(0)')==(base[0]+1)//2
 assert p.evaluate('BFGlobalInjuryAttackV6200.effectiveAttack(2)')==(base[2]+1)//2
 for slot in (0,2):
  assert p.evaluate(f'BFGlobalOriginalAilmentStateV5700.cure({slot},20210).removed')==[4]
 after=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),
 atk:S.party.map(u=>u.atk),def:S.party.map(u=>u.def),rec:S.party.map(u=>u.rec)})""")
 assert before==after,(before,after)
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalInjuryAttackV6200.snapshot().injuredSlots')==[]
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalInjuryAttackV6200.snapshot().injuredSlots')==[]
 assert not errors,errors
 b.close()
print('PASS v79 subtractive Injury penalty stacks additively with +30/+50/+100 ATK, existing stats, saves stable')
