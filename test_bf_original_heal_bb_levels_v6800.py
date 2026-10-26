"""v68 original source level 1-10 healing BB base ranges and live cast."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_original_bb_support_v029.json').read_text('utf8'))
assert source['schema']=='bf-global-original-bb-support-v029'
heal_ids=(20041,30041,40041,50041)
for skill_id in heal_ids:
 levels=source['skills'][str(skill_id)]['levels']
 assert len(levels)==10
 for i,entry in enumerate(levels):
  assert entry=={'level':i+1,'effectCode':1500,'params':[600+30*i,800+30*i,50,50]}
module=(A/'bf6800_original_heal_bb_levels.js').read_text('utf8')
assert module.count('/* BF_GLOBAL_ORIGINAL_HEAL_BB_LEVELS_V6800 */')==1
assert len(module.encode('utf8'))<65536
assert all(x not in module for x in ('localStorage','saveProgress(', 'BFAndroid'))
rec=(A/'bf6700_burst_recipient_rec.js').read_text('utf8')
assert 'window.BFGlobalOriginalHealBBLevelsV6800?.baseHeal(base)??base' in rec
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf6700_burst_recipient_rec.js")')<java.index('readPackagedText("bf6800_original_heal_bb_levels.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
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
 p.add_script_tag(path=str(A/'bf6700_burst_recipient_rec.js'))
 p.add_script_tag(path=str(A/'bf6800_original_heal_bb_levels.js'))
 assert p.evaluate('P.version')==7
 assert p.locator('#bf6800-level').locator('option').count()==10
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.snapshot().level')==1
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(650,{rec:500})')==1150
 for uid in heal_ids:
  for level in range(1,11):
   assert p.evaluate(f'BFGlobalOriginalHealBBLevelsV6800.sourceFor({uid},{level})')=={
    'level':level,'effectCode':1500,'low':600+30*(level-1),'high':800+30*(level-1),'undecoded':[50,50]}
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.sourceFor(999999,1)') is None
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.selectLevel(11)') is False
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
   P:JSON.stringify(P),S:JSON.stringify(S)})""")
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.selectLevel(10)') is True
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.snapshot().range.high')==1070
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.baseHeal(600)')==870
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(650,{rec:500})')==1420
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(800,{rec:500})')==1570
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(800,{rec:NaN})')==800
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.selectLevel(0)') is False
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.snapshot().level')==10
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.source.levels.length')==10
 # Runtime source BB: level 10 should recover +870..1070 plus recipient REC.
 p.evaluate("""()=>{const caster=S.party[0];caster.unitId=20041;caster.rec=600;
   caster.maxHp=9000;caster.hp=2000;caster.bb=100;caster.action={kind:'burst',target:0};
   for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
     S.party[i].action={kind:'guard',target:0};
   for(const e of S.enemies){e.atk=0;e.hp=10000;e.maxHp=10000}
   document.getElementById('speed').value='4';}""")
 p.evaluate('BF_debug.execute()')
 delta=p.evaluate('S.party[0].hp')-2000
 assert 1465<=delta<=1670,('v68 live level 10 BB range not applied',delta)
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
   P:JSON.stringify(P)})""")
 assert before['save']==after['save'] and before['P']==after['P']
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.baseHeal(650)')==650
 assert p.locator('#bf6800-levels').is_hidden()
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800.snapshot().level')==1
 assert p.evaluate('BFGlobalBurstRecipientRecoveryV6700.healAmount(650,{rec:500})')==1150
 p.evaluate('()=>{window.__bf68prev=BFGlobalOriginalHealBBLevelsV6800}')
 p.add_script_tag(path=str(A/'bf6800_original_heal_bb_levels.js'))
 assert p.evaluate('BFGlobalOriginalHealBBLevelsV6800===window.__bf68prev') is True
 assert p.locator('#bf6800-levels').count()==1
 assert not errors,errors
 b.close()
print('PASS v68 all 40 archived Lv1-10 BB heal ranges, real Lv10 cast, fallback, reset, save and mode isolation')
