"""v112 authentic 2022 leader skill source for all 72 playable forms, read-only."""
from pathlib import Path
import json,re,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_2022_playable_leader_catalog_v112.json').read_text('utf8'))
assert source['schema']=='bf-global-2022-all-72-playable-unit-leader-profiles-v112'
assert source['source']['zipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert source['source']['leaderMaster']['sha256']=='65e591557264d656be2408e9c426ef35050b960f1736a488da8f0a55a5e845fe'
assert source['totalForms']==72 and source['distinctLeaderIds']==36
assert source['skillTypesCount']=={'2':30,'31':25,'31@29':1,'31@32':1,'31@34':1,'31@48':1,'31@49':1,'5':12}
assert len(source['rows'])==72 and len({x['unitId'] for x in source['rows']})==72
js=(A/'bf11200_all_playable_leader_source.js').read_text('utf8')
assert js.count('BF_GLOBAL_ALL_PLAYABLE_LEADER_SOURCE_V11200')==1
assert len(js.encode('utf8'))<65536
match=re.search(r'const extra=(\[\[.+?\]\]);',js)
assert match
raw=json.loads(match.group(1))
expected=[[x['unitId'],x['rarity'],x['element'],x['leaderSkillId'],x['skillTypeRaw'],x['passiveSkillInfoRaw']] for x in source['rows'] if x['unitId']%10000>=21]
assert raw==expected
assert not any(x in js for x in ['saveProgress(', 'localStorage', 'S.party=', 'P.squad=', 'Math.random', 'fetch(', 'XMLHttpRequest'])
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11100_original_starter_leader_combat.js")')<java.index('readPackagedText("bf11200_all_playable_leader_source.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content('<html><body><section id="squadpicker"></section></body></html>')
 p.evaluate('''()=>{window.P={version:7,roster:[10011,20011],squad:[10011,20011]};window.S={mode:'archive',party:[]};window.effectiveUnit=id=>({id});}''')
 saved=p.evaluate('JSON.stringify(P)')
 p.add_script_tag(path=str(A/'bf11000_source_starter_leader_skills.js'))
 p.add_script_tag(path=str(A/'bf11200_all_playable_leader_source.js'))
 assert p.evaluate('BFGlobalPlayableLeadersV11200.snapshot().count')==72
 assert p.evaluate('BFGlobalPlayableLeadersV11200.lookup(10011).skillTypeRaw')=='2'
 assert p.evaluate('BFGlobalPlayableLeadersV11200.lookup(10021).skillTypeRaw')=='31'
 assert p.evaluate('BFGlobalPlayableLeadersV11200.lookup(10041).passiveSkillInfoRaw')=='1,10'
 assert p.evaluate('BFGlobalPlayableLeadersV11200.lookup(60025).skillTypeRaw')=='31@29'
 assert p.evaluate('BFGlobalPlayableLeadersV11200.lookup(10025).passiveSkillInfoRaw')=='50,0,0,0,0,0@0.5'
 assert p.evaluate('BFGlobalPlayableLeadersV11200.lookup(9999999)') is None
 assert p.locator('#bf11200-form option').count()==72
 p.locator('#bf11200-playable-leaders > summary').click()
 p.locator('#bf11200-form').select_option('60025')
 assert '31@29' in p.locator('#bf11200-raw').inner_text()
 assert 'RAW ONLY' in p.locator('#bf11200-raw').inner_text()
 assert p.evaluate('JSON.stringify(P)')==saved
 p.add_script_tag(path=str(A/'bf11200_all_playable_leader_source.js'))
 assert p.locator('#bf11200-playable-leaders').count()==1
 assert not errors,errors
 b.close()
print('PASS v112 72 original 2022 leader records, 36 LS, raw type2/5/31/compound, no gameplay/save mutation')
