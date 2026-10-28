"""v166: original 2022 Global 10% type5 leader mitigation, known enemies only."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
manifest=json.loads((R/'source_data/bf_global_2022_playable_leader_catalog_v112.json').read_text('utf8'))
english=json.loads((R/'source_data/bf_global_2022_playable_leader_english_v114.json').read_text('utf8'))
expected={10041:(500,'Fire','1,10'),10042:(500,'Fire','1,10'),
 20041:(502,'Water','2,10'),20042:(502,'Water','2,10'),
 30041:(504,'Earth','3,10'),30042:(504,'Earth','3,10'),
 40041:(506,'Thunder','4,10'),40042:(506,'Thunder','4,10'),
 50041:(508,'Light','5,10'),50042:(508,'Light','5,10'),
 60041:(510,'Dark','6,10'),60042:(510,'Dark','6,10')}
rows={r['unitId']:r for r in manifest['rows'] if r['skillTypeRaw']=='5'}
assert len(rows)==12 and set(rows)==set(expected)
desc={r['leaderSkillId']:r['originalEnglishDescription'] for r in english['records']}
for uid,(ls,element,raw) in expected.items():
 r=rows[uid]
 assert r['leaderSkillId']==ls and r['passiveSkillInfoRaw']==raw
 assert desc[ls]=='10% reduction in damage from '+element+' Types'
js=(A/'bf16600_original_type5_element_resist.js').read_text('utf8')
core=(A/'index.html').read_text('utf8')
assert js.count('BF_GLOBAL_ORIGINAL_TYPE5_ELEMENT_RESIST_V16600')==1
assert len(js.encode())<12000
assert core.count('BFGlobalOriginalElementResistV16600?.scaleIncoming(')==1
assert core.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
assert 'prototypeDamage(enemy.atk,target.def,target.guard ? .5 : 1)' in core
assert not any(s in js for s in ('saveProgress(', 'localStorage', 'P.squad=', 'P.roster=', 'Math.random', 'fetch(', 'XMLHttpRequest'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11400_original_global_leader_english.js")')<java.index('readPackagedText("bf16600_original_type5_element_resist.js")')
assert java.index('readPackagedText("bf6900_elemental_combat.js")')<java.index('readPackagedText("bf16600_original_type5_element_resist.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
  getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
  removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
  get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};
  HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content(core,wait_until='load',timeout=90000)
 for file in ['bf11000_source_starter_leader_skills.js',
              'bf11200_all_playable_leader_source.js',
              'bf11400_original_global_leader_english.js',
              'bf6900_elemental_combat.js',
              'bf16600_original_type5_element_resist.js']:
  p.add_script_tag(path=str(A/file))
 api='BFGlobalOriginalElementResistV16600'
 assert p.evaluate('!!window.'+api)
 assert p.evaluate(api+'.source.sourceQualifiedForms')==12
 assert p.locator('#bf16600-resist').count()==1
 assert 'Type5 10% elemental' in p.locator('#bf11400-original-leader-english small').text_content()
 before=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 for uid,(ls,element,_) in expected.items():
  p.evaluate("""id=>{if(!P.roster.includes(id))P.roster.push(id);
     P.squad[0]=id;document.getElementById('mode').value='archive';reset()}""",uid)
  l=p.evaluate(api+'.leader()')
  assert l and l['unitId']==uid and l['leaderId']==ls and l['resistedElement']==element,l
  assert p.evaluate(api+".scaleIncoming(100,'"+element+"',S.party[1])")==90
  assert p.evaluate(api+".scaleIncoming(1,'"+element+"',S.party[1])")==1
  assert p.evaluate(api+".scaleIncoming(100,null,S.party[1])")==100
  assert p.evaluate(api+".scaleIncoming(100,'"+element+"',{active:true,hp:100})")==100
  other='Dark' if element!='Dark' else 'Fire'
  assert p.evaluate(api+".scaleIncoming(100,'"+other+"',S.party[1])")==100
  # No cumulative effect: only one reduction per incoming hit.
  assert p.evaluate(api+".scaleIncoming(100,'"+element+"',S.party[1])")==90
 p.evaluate("document.getElementById('mode').value='training';reset()")
 assert p.evaluate(api+'.leader()') is None
 assert p.evaluate(api+".scaleIncoming(100,'Dark',S.party[1])")==100
 p.evaluate("document.getElementById('mode').value='archive';P.squad[0]=10011;reset()")
 assert p.evaluate(api+'.leader()') is None
 assert p.evaluate(api+".scaleIncoming(100,'Fire',S.party[1])")==100
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before
 p.evaluate('window.__priorV166=window.'+api)
 p.add_script_tag(path=str(A/'bf16600_original_type5_element_resist.js'))
 assert p.evaluate('window.__priorV166===window.'+api)
 assert not errors,errors
 b.close()
print('PASS v166 12 authentic type5 Global forms: exact 10% known-element incoming hit, six skills, training and unknown-enemy fallback, no save writes')
