"""v92 original 2022 offensive BB Lv1-10 source modifiers in actual battle."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
data=json.loads((R/'source_data/bf_global_original_bb_power_v030.json').read_text('utf8'))
assert data['schema']=='bf-global-original-offensive-bb-power-v030'
assert data['provenance']['mstZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert len(data['skills'])==24
for uid,entry in data['skills'].items():
 assert entry['skillId']==int(uid)
 assert len(entry['levels'])==10
 assert all(v['level']==i and v['effectCode'] in (1500,1800,2000) and
            0<=v['damageModifierPct']<=400 for i,v in enumerate(entry['levels'],1))
assert [v['damageModifierPct'] for v in data['skills']['10011']['levels']]==[30,35,40,45,50,55,60,65,70,75]
assert data['skills']['10021']['levels'][-1]['damageModifierPct']==240
js=(A/'bf9200_source_offensive_bb_levels.js').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert js.count('BF_GLOBAL_SOURCE_OFFENSIVE_BB_LEVELS_V9200')==1
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid','fetch(','XMLHttpRequest'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf6800_original_heal_bb_levels.js")')<java.index('readPackagedText("bf9200_source_offensive_bb_levels.js")')
assert java.index('readPackagedText("bf9100_innate_status_resistance.js")')<java.index('readPackagedText("bf9200_source_offensive_bb_levels.js")')
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
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_script_tag(path=str(A/'bf6700_burst_recipient_rec.js'))
 p.add_script_tag(path=str(A/'bf6800_original_heal_bb_levels.js'))
 assert p.evaluate('BFOriginalBBPower.count')==24
 assert p.evaluate('bbDamageMultiplier({unitId:10011},true)')==1.3
 p.add_script_tag(path=str(A/'bf9200_source_offensive_bb_levels.js'))
 api='BFGlobalSourceOffensiveBBLevelsV9200'
 assert p.evaluate(api+'.source.supportedOffensiveSkills')==24
 assert p.evaluate(api+'.snapshot().level')==1
 assert p.evaluate('bbDamageMultiplier({unitId:10011},true)')==1.3
 assert p.evaluate('bbDamageMultiplier({unitId:10021},true)')==2.5
 assert p.evaluate('bbDamageMultiplier({unitId:10011},false)')==1
 assert p.evaluate(api+'.sourceFor(10011,11)') is None
 assert p.evaluate(api+'.sourceFor(0,1)') is None
 assert p.evaluate('bbDamageMultiplier({unitId:999999999},true)')==2.1
 for level in range(1,11):
  assert p.evaluate(f'BFGlobalOriginalHealBBLevelsV6800.selectLevel({level})') is True
  got=p.evaluate('bbDamageMultiplier({unitId:10011},true)')
  assert abs(got-(1+data['skills']['10011']['levels'][level-1]['damageModifierPct']/100))<1e-9,(level,got)
 assert p.evaluate('bbDamageMultiplier({unitId:10011},true)')==1.75
 assert p.evaluate('bbDamageMultiplier({unitId:10021},true)')==3.4
 before=p.evaluate("""()=>({progress:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 def burst_damage(level):
  p.locator('#reset').click()
  assert p.evaluate(f'BFGlobalOriginalHealBBLevelsV6800.selectLevel({level})') is True
  p.evaluate("""()=>{S.enemies.forEach((e,i)=>{if(i>0)e.hp=0;else{
   e.hp=20000;e.maxHp=20000;e.def=0;e.atk=0}});
   S.party[0].unitId=10011;S.party[0].atk=800;S.party[0].bb=100;
   S.party[0].action={kind:'burst',target:0};
   for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
    S.party[i].action={kind:'guard',target:0};
   document.getElementById('speed').value='4';window.__old92=Math.random;Math.random=()=>0.5}""")
  p.evaluate('BF_debug.execute()')
  val=20000-p.evaluate('S.enemies[0].hp')
  p.evaluate('Math.random=window.__old92')
  return val
 low=burst_damage(1);high=burst_damage(10)
 assert low>0 and high>low*1.15,(low,high)
 after=p.evaluate("""()=>({progress:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,(before,after)
 p.locator('#mode').select_option('training')
 assert p.evaluate('bbDamageMultiplier({unitId:10011},true)')==1.3
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate(api+'.snapshot().level')==1
 assert p.evaluate('bbDamageMultiplier({unitId:10011},true)')==1.3
 p.evaluate('window.__v92=window.bbDamageMultiplier')
 p.add_script_tag(path=str(A/'bf9200_source_offensive_bb_levels.js'))
 assert p.evaluate('window.__v92===window.bbDamageMultiplier')
 assert p.locator('#bf9200-offensive-note').count()==1
 assert not errors,errors
 b.close()
print('PASS v92 240 source levels, playable Lv10 burst power, neutral unsupported fallback, training and v7 saves')
