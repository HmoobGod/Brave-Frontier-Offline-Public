"""v110: first 30 starter-form original Global leader-skill source records.
Static source provenance + live squad read-only preview, fail closed on unknown.
"""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_2022_starter_leader_skill_audit_v110.json').read_text('utf8'))
assert source['schema']=='bf-global-2022-starter-leader-skill-audit-v110'
prov=source['provenance']
assert prov['zipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert prov['leaderMaster']['sha256']=='65e591557264d656be2408e9c426ef35050b960f1736a488da8f0a55a5e845fe'
assert prov['unitMaster1']['sha256']=='1146f09489a07b9187cd3f04bf7dc3ef3bb74e35385869534671af95bf8ea645'
assert prov['unitMaster2']['sha256']=='0696ccda59fccf48598c5267eaeb8a306e994618384151cead38cec6a9195b2b'
rows=source['rows']
assert len(rows)==30 and len({r['unitId'] for r in rows})==30
assert len({r['lsId'] for r in rows})==18
for e in range(1,7):
 for i in range(5):
  r=rows[(e-1)*5+i]
  atk=(25 if i<2 else 50);hp=(10 if i==4 else 0)
  assert r=={'unitId':e*10000+i+11,'element':e,
             'lsId':100+(e-1)*10+(0 if i<2 else 1 if i<4 else 2),
             'skillTypeId':2,
             'rawPassive':f'{e},0,{atk},0,0,0,{hp}',
             'atkPercent':atk,'hpPercent':hp}
js=(A/'bf11000_source_starter_leader_skills.js').read_text('utf8')
assert js.count('BF_GLOBAL_2022_STARTER_LEADER_SKILL_SOURCE_V11000')==1
assert len(js.encode('utf8'))<65536
assert 'byUnit.size!==30' in js
assert 'nativeBattleStatsModified:false' in js
assert not any(x in js for x in ('localStorage','saveProgress(', 'P.squad=', 'S.party=',
                                'awardDemoRewards(', 'Math.random','fetch(','XMLHttpRequest'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.count('readPackagedText("bf11000_source_starter_leader_skills.js")')==1
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content('<html><body><section id="squadpicker">SQUAD</section></body></html>')
 p.evaluate("""()=>{
  window.P={version:7,roster:[10011,10012,20011,40011,30011,60015],
    squad:[10011,10012,20011,40011,60015],questClears:{1:2}};
  window.S={mode:'archive',busy:false,party:[]};
  window.effectiveUnit=id=>({id,name:'unit '+id});
 }""")
 initial=p.evaluate('JSON.stringify(P)')
 p.add_script_tag(path=str(A/'bf11000_source_starter_leader_skills.js'))
 api='BFGlobalStarterLeaderSourceV11000'
 assert p.evaluate(api+'.source.sourceLeaderSkills')==18
 assert p.evaluate(api+'.lookup(10011).atkPercent')==25
 assert p.evaluate(api+'.lookup(10015).hpPercent')==10
 assert p.evaluate(api+'.lookup(20013).atkPercent')==50
 assert p.evaluate(api+'.lookup(60015).lsId')==152
 assert p.evaluate(api+'.lookup(1)') is None
 assert p.evaluate(api+'.lookup(999999)') is None
 assert p.evaluate(api+'.bonusFor(10011,10012).atkPercent')==25
 assert p.evaluate(api+'.bonusFor(10011,20011).atkPercent')==0
 assert p.evaluate(api+'.bonusFor(10015,10011).hpPercent')==10
 assert p.evaluate(api+'.bonusFor(10015,60015).hpPercent')==0
 assert p.evaluate(api+'.bonusFor(10011,10023)') is None
 a=p.evaluate(api+'.snapshot()')
 assert a['leaderBase']==10011 and a['leaderId']==10011
 assert a['leaderSupported'] is True
 assert [u['effect']['atkPercent'] for u in a['slots']]==[25,25,0,0,0]
 assert a['nativeLeaderBuffsApplied'] is False
 p.locator('#bf11000-leader-audit > summary').click()
 p.wait_for_function("document.querySelector('#bf11000-targets').children.length===5")
 assert 'ATK +25%' in p.locator('#bf11000-targets').inner_text()
 p.evaluate("""()=>{P.squad=[60015,10011,20011]}""")
 a=p.evaluate(api+'.snapshot()')
 assert a['leaderId']==60015
 assert a['slots'][0]['effect']['atkPercent']==50
 assert a['slots'][0]['effect']['hpPercent']==10
 assert a['slots'][1]['effect']['atkPercent']==0
 p.evaluate("""()=>{P.squad=[123456,10011]}""")
 assert p.evaluate(api+'.snapshot().leaderSupported') is False
 assert p.evaluate(api+'.snapshot().slots[1].effect') is None
 p.evaluate("""()=>{P.squad=[10011,123456]}""")
 assert p.evaluate(api+'.snapshot().slots[1].effect') is None
 p.evaluate("""()=>{P.squad=[10011,10012,20011,40011,60015]}""")
 assert p.evaluate('JSON.stringify(P)')==initial
 p.add_script_tag(path=str(A/'bf11000_source_starter_leader_skills.js'))
 assert p.locator('#bf11000-leader-audit').count()==1
 assert not errors,errors
 b.close()
print('PASS v110 original 30 starter leader profiles, elements, HP/ATK, squad preview, fail-closed and v7 save integrity')
