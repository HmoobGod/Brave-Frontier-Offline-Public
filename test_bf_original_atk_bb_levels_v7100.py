"""v71 archived ATK support-BB skill levels and live buff gameplay."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
evidence=json.loads((R/'source_data/bf_global_original_bb_support_v029.json').read_text('utf8'))
expected={40021:[30,31,32,33,34,35,36,37,38,40],
          40022:[40,41,42,43,44,45,46,47,48,50]}
for uid,values in expected.items():
 entry=evidence['skills'][str(uid)]
 assert entry['name'] in ("Thunder's Command","Thunder's Rage")
 assert len(entry['levels'])==10
 for i,(lv,pct) in enumerate(zip(entry['levels'],values)):
  assert lv=={'level':i+1,'effectCode':1300 if uid==40021 else 1600,
              'params':[0,pct,0,0,0,3,90]}
js=(A/'bf7100_original_atk_bb_levels.js').read_text('utf8')
html=(A/'index.html').read_text('utf8')
assert js.count('/* BF_GLOBAL_ORIGINAL_ATK_BB_LEVELS_V7100 */')==1
assert len(js.encode('utf8'))<65536
assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
assert html.count('BFGlobalOriginalAtkBBLevelsV7100?.boostFor(p.unitId)')==1
assert html.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf6900_elemental_combat.js")')<java.index('readPackagedText("bf7100_original_atk_bb_levels.js")')
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
 for name in ('bf6700_burst_recipient_rec.js','bf6800_original_heal_bb_levels.js',
              'bf6900_elemental_combat.js','bf7100_original_atk_bb_levels.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.snapshot().level')==1
 assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.boostFor(40021)')==30
 assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.boostFor(40022)')==40
 assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.sourceFor(40021,11)') is None
 assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.sourceFor(0,1)') is None
 for level in range(1,11):
  assert p.evaluate(f'BFGlobalOriginalHealBBLevelsV6800.selectLevel({level})') is True
  assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.boostFor(40021)')==expected[40021][level-1]
  assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.boostFor(40022)')==expected[40022][level-1]
 p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.refresh()')
 assert '+40%' in p.locator('#bf7100-atk-preview').inner_text()
 before=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),
  atk:S.party.map(x=>x.atk)})""")
 # Lv10 archived 40021 buff must apply +40%, not inherited Lv1 +30%.
 p.evaluate("""()=>{const caster=S.party[0];caster.unitId=40021;caster.bb=100;
   caster.action={kind:'burst',target:0};
   for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
    S.party[i].action={kind:'guard',target:0};
   for(const e of S.enemies){e.hp=10000;e.maxHp=10000;e.atk=0}
   document.getElementById('speed').value='4'}""")
 p.evaluate('BF_debug.execute()')
 buffs=p.evaluate('S.party.filter(x=>x.active&&x.hp>0).map(x=>x.atkBuff?.pct??0)')
 assert buffs and all(x==40 for x in buffs),buffs
 assert p.evaluate('S.party.map(x=>x.atk)')==before['atk']
 after=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before['P']==after['P'] and before['save']==after['save']
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.boostFor(40021)') is None
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.boostFor(40021)')==30
 assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100.boostFor(40022)')==40
 p.evaluate('window.__bf70prev=BFGlobalOriginalAtkBBLevelsV7100')
 p.add_script_tag(path=str(A/'bf7100_original_atk_bb_levels.js'))
 assert p.evaluate('BFGlobalOriginalAtkBBLevelsV7100===window.__bf70prev') is True
 assert p.locator('#bf7100-atk-preview').count()==1
 assert not errors,errors
 b.close()
print('PASS v71 all 20 source ATK levels, live Lv10 buff, v68/v69 source continuity, save and reset isolation')
