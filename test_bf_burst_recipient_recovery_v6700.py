"""v67 original recipient REC contribution to Lv1 healing; safe fallback."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf6700_burst_recipient_rec.js').read_text('utf8')
html=(A/'index.html').read_text('utf8')
assert js.count('/* BF_GLOBAL_BURST_RECIPIENT_RECOVERY_V6700 */')==1
assert len(js.encode())<65536
assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
assert html.count('BFGlobalBurstRecipientRecoveryV6700?.healAmount(base,ally)')==1
assert 'source Lv1 base healing range' in html and 'bf_global_offline_demo_v7' in html
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'readPackagedText("bf6700_burst_recipient_rec.js")' in java
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
 p.set_content(html,wait_until='load',timeout=90000)
 p.add_script_tag(path=str(A/'bf6700_burst_recipient_rec.js'))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.source.archivedSkillIds')==[20041,30041,40041,50041]
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(600,S.party[0])')==600+p.evaluate('Math.round(S.party[0].rec)')
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(800,{rec:500})')==1300
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(600,{rec:100.5})')==701
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(800,{rec:NaN})')==800
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(800,{rec:-1})')==800
 before=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 p.evaluate('S.party[0].rec=1000')
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(650,S.party[0])')==1650
 p.evaluate('S.party[0].rec=500')
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(650,S.party[0])')==1150
 p.evaluate('S.party[0].rec=1000')
 after=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before['p']==after['p'] and before['save']==after['save']
 # Native integration: Cure Light Lv1 base 600..800 plus recipient REC.
 # Keep enemies alive but harmless (their DEMO minimum 1 damage is bounded).
 p.evaluate("""()=>{S.party[0].unitId=20041;S.party[0].rec=600;
 S.party[0].maxHp=9000;
 for(const e of S.enemies){e.atk=0;e.hp=10000;e.maxHp=10000}
 }""")
 def run_burst():
  p.evaluate("""()=>{const caster=S.party[0];caster.hp=2000;caster.bb=100;
  caster.action={kind:'burst',target:0};
  for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
   S.party[i].action={kind:'guard',target:0};
  const speed=document.getElementById('speed');if(speed)speed.value='4'}""")
  p.evaluate('BF_debug.execute()')
  return p.evaluate('S.party[0].hp')-2000
 normal=run_burst()
 assert 1198<=normal<=1400,('recipient REC not applied to live healing',normal)
 # v65 source Sickness halves the same REC stat during BB execution.
 p.add_script_tag(path=str(A/'bf5700_original_ailment_state.js'))
 p.evaluate('window.BFGlobalStatusRemedyCommandV6400={}') # only satisfy v65 dependency
 p.add_script_tag(path=str(A/'bf6500_sickness_recovery.js'))
 assert p.evaluate('!!BFGlobalSicknessRecoveryV6500') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,3)') is True
 sick=run_burst()
 assert 898<=sick<=1100,('Sickness did not halve heal recipient REC',sick)
 assert p.evaluate('S.party[0].rec')==600
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20210).removed')==[3]
 # When optional calculator is absent, original base-only path remains legal.
 p.evaluate('delete window.BFGlobalBurstRecipientRecoveryV6700')
 fallback=run_burst()
 assert 598<=fallback<=800,('missing-module fallback changed original demo',fallback)
 p.add_script_tag(path=str(A/'bf6700_burst_recipient_rec.js'))
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(650,{rec:1000})')==650
 p.locator('#mode').select_option('archive')
 p.evaluate('()=>{window.__bf67old=BFGlobalBurstRecipientRecoveryV6700}')
 p.add_script_tag(path=str(A/'bf6700_burst_recipient_rec.js'))
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700===window.__bf67old') is True
 assert not errors,errors
 b.close()
print('PASS v67 original burst heal recipient REC term, fallback/isolation/rounding, v7 save unchanged')
