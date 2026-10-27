"""v114 2022 original Global English LS strings: exact 36 names/descriptions."""
from pathlib import Path
import json,re,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_2022_playable_leader_english_v114.json').read_text('utf8'))
assert source['schema']=='bf-global-original-leader-english-v114'
assert source['source']['archiveSha256']=='4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
assert source['source']['names']['nestedSha256']=='145f04664ae89e3f507c70186c63f8dbd15c4ef6953ead2f93ea30c3368b91c3'
assert source['source']['descriptions']['nestedSha256']=='5e9d92095b1417f3cd619cfb9c36eb518945c33cd3bce181854da57ad7f87c47'
assert source['leaderSkillCount']==36 and source['originalPlayableFormCount']==72
records=source['records']
assert len(records)==36 and len({r['leaderSkillId'] for r in records})==36
assert next(x for x in records if x['leaderSkillId']==500)['originalEnglishDescription']=='10% reduction in damage from Fire Types'
assert next(x for x in records if x['leaderSkillId']==1400)['originalEnglishDescription']=='Small boost in Battle Crystals produced during Spark'
assert next(x for x in records if x['leaderSkillId']==1411)['originalEnglishDescription']=='Small reduction in BB gauge amount consumed during BB & large boost to drop rate of BC produced during Spark'
js=(A/'bf11400_original_global_leader_english.js').read_text('utf8')
assert js.count('BF_GLOBAL_ORIGINAL_LEADER_ENGLISH_V11400')==1
assert len(js.encode())<16000
match=re.search(r'const originalRows=(\[\[.*?\]\]);',js)
assert match
assert json.loads(match.group(1))==[[r['leaderSkillId'],r['originalEnglishName'],r['originalEnglishDescription']] for r in records]
assert not any(x in js for x in ('saveProgress(', 'localStorage', 'S.party=', 'P.squad=', 'Math.random', 'fetch(', 'XMLHttpRequest', 'window.enemyPhase=','window.performUnit='))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11300_all_playable_leader_recipients.js")')<java.index('readPackagedText("bf11400_original_global_leader_english.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content('<html><body><section id="squadpicker"></section></body></html>')
 p.evaluate("""()=>{window.P={version:7,roster:[10011,20011],squad:[10011,20011]};
  window.S={mode:'archive',party:[]};window.effectiveUnit=id=>({id});}""")
 before=p.evaluate('JSON.stringify(P)')
 p.add_script_tag(path=str(A/'bf11000_source_starter_leader_skills.js'))
 p.add_script_tag(path=str(A/'bf11200_all_playable_leader_source.js'))
 p.add_script_tag(path=str(A/'bf11400_original_global_leader_english.js'))
 api='BFGlobalOriginalLeaderEnglishV11400'
 assert p.evaluate(api+'.source.names')==36
 assert p.evaluate(api+'.forUnit(10041).name')=="Fire's Protection"
 assert p.evaluate(api+'.forUnit(30021).description')=='Small boost in Battle Crystals produced during Spark'
 assert p.evaluate(api+'.forUnit(10025).name')=='Intense Edge'
 assert p.evaluate(api+'.forUnit(10011).combatImplemented') is True
 assert p.evaluate(api+'.forUnit(10021).combatImplemented') is False
 assert p.evaluate(api+'.forUnit(123456)') is None
 assert p.locator('#bf11200-form option').count()==72
 p.locator('#bf11200-playable-leaders > summary').click()
 assert 'Fire Spirit' in p.locator('#bf11200-form option').first.text_content()
 p.locator('#bf11200-form').evaluate("""el=>{el.value='50021';el.dispatchEvent(new Event('change'));}""")
 assert 'Fighting Light' in p.locator('#bf11400-original-name').inner_text()
 assert 'Battle Crystals produced during Spark' in p.locator('#bf11400-original-description').inner_text()
 p.locator('#bf11200-form').evaluate("""el=>{el.value='10041';el.dispatchEvent(new Event('change'));}""")
 assert "Fire's Protection" in p.locator('#bf11400-original-name').inner_text()
 assert '10% reduction in damage from Fire Types' in p.locator('#bf11400-original-description').inner_text()
 assert p.evaluate(api+'.snapshot().addsCombatEffects') is False
 assert p.evaluate('JSON.stringify(P)')==before
 p.add_script_tag(path=str(A/'bf11400_original_global_leader_english.js'))
 assert p.locator('#bf11400-original-leader-english').count()==1
 assert not errors,errors
 b.close()
print('PASS v114 exact original 2022 Global English 36 LS / 72 forms, Spark/BC/mitigation distinction, no save writes')
