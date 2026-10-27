"""v116 source-backed Lord endpoints: 72 playable 2022 forms, read-only."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
manifest=json.loads((R/'source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json').read_text('utf8'))
leaders=json.loads((R/'source_data/bf_global_2022_playable_leader_catalog_v112.json').read_text('utf8'))
caps=json.loads((R/'source_data/bf_global_2022_playable_level_caps_v115.json').read_text('utf8'))
assert manifest['schema']=='bf-global-2022-playable-lord-stat-endpoints-v116'
assert len(manifest['rows'])==manifest['unitCount']==leaders['totalForms']==72
assert len(manifest['unitTypeRaw'])==manifest['rawUnitTypeCount']==6
assert manifest['source']['archiveSha256']==leaders['source']['zipSha256']
assert manifest['source']['units']==leaders['source']['unitMasters']
assert manifest['source']['typeMaster']['sha256']=='69cc9a357b1915d31f852346e144fd6b4a0e61c9d7d64e0ac9c1a60297a10301'
rows={r['unitId']:r for r in manifest['rows']}
assert len(rows)==72==len(set(rows))
assert set(rows)=={r['unitId'] for r in leaders['rows']}
for e in range(1,7):
 for n in range(5):
  assert rows[e*10000+11+n]['maxLevel']==caps['firstStarterCapByElement'][str(e)][n]
  assert rows[e*10000+21+n]['maxLevel']==caps['secondStarterCap'][n]
 for n in range(2):
  assert rows[e*10000+41+n]['maxLevel']==caps['alternateCap'][n]
for r in rows.values():
 assert r['expPatternId'] in (10,15,20)
 for k in ('hp','atk','def','rec'):
  assert type(r['base'][k])==int and r['base'][k]>0
  assert type(r['lordAtMax'][k])==int and r['lordAtMax'][k]>=r['base'][k]
assert rows[10011]['base']=={'hp':1030,'atk':500,'def':410,'rec':320}
assert rows[10011]['lordAtMax']=={'hp':1948,'atk':700,'def':574,'rec':448}
assert rows[10015]['lordAtMax']['hp']==5313
assert rows[60015]['lordAtMax']['hp']==5942
assert [x['unitTypeId'] for x in manifest['unitTypeRaw']]==list(range(1,7))
assert manifest['unitTypeRaw'][1]['unitTypeHpRaw']=='5,10'
assert manifest['unitTypeRaw'][5]['unitTypeChanceRaw']=='0.00'

generated=(A/'bf11600_original_lord_stats_data.js').read_text('utf8')
module=(A/'bf11600_original_lord_stats_reference.js').read_text('utf8')
assert 'BF_GLOBAL_2022_LORD_STATS_DATA_V11600' in generated
assert module.count('BF_GLOBAL_2022_LORD_STATS_REFERENCE_V11600')==1
assert 'nativeMidlevelGrowthVerified:false' in module
assert not any(token in module for token in (
 'localStorage','saveProgress(', 'P.unitExp=', 'P.squad=', 'P.roster=',
 'S.party=','window.playerUnit=', 'Math.random','fetch(', 'XMLHttpRequest'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11500_original_unit_level_caps.js")')<java.index(
 'readPackagedText("bf11600_original_lord_stats_data.js")')<java.index(
 'readPackagedText("bf11600_original_lord_stats_reference.js")')

with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda err:errors.append(str(err)))
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 initial=p.evaluate('JSON.stringify(P)')
 p.add_script_tag(path=str(A/'bf11600_original_lord_stats_data.js'))
 p.add_script_tag(path=str(A/'bf11600_original_lord_stats_reference.js'))
 api='BFGlobalOriginalLordStatsV11600'
 assert p.evaluate(api+'.source.formCount')==72
 assert p.evaluate(api+'.source.typeCount')==6
 assert p.evaluate(api+'.source.liveBattleStatsModified') is False
 assert p.evaluate(api+'.source.nativeMidlevelGrowthVerified') is False
 assert p.evaluate(api+'.unitTypesRaw.length')==6
 for uid in rows:
  assert p.evaluate(f'{api}.lookup({uid}).maxLevel')==rows[uid]['maxLevel']
 assert p.evaluate(api+'.lookup(10011).base.hp')==1030
 assert p.evaluate(api+'.lookup(10011).lordAtMax.hp')==1948
 assert p.evaluate(api+'.lookup(10015).lordAtMax.hp')==5313
 assert p.evaluate(api+'.lookup(60015).lordAtMax.hp')==5942
 assert p.evaluate(api+'.lookup(999999)') is None
 assert p.evaluate(api+'.endpoint(10011,1).stats.hp')==1030
 assert p.evaluate(api+'.endpoint(10011,12).stats.hp')==1948
 assert p.evaluate(api+'.endpoint(10011,2)') is None
 assert p.evaluate(api+'.endpoint(10015,50)') is None
 assert p.evaluate(api+'.endpoint(10015,100).stats.hp')==5313
 assert p.evaluate(api+'.endpoint(10015,101)') is None
 snap=p.evaluate(api+'.snapshot()')
 assert len(snap['slots'])<=6
 assert snap['source']['savedProgressModified'] is False
 assert p.locator('#bf11600-original-lord-stats').count()==1
 p.locator('#bf11600-original-lord-stats').evaluate('(el)=>el.open=true')
 p.evaluate(api+'.refresh()')
 assert p.locator('#bf11600-rows > div').count()==len(snap['slots'])
 assert p.evaluate('JSON.stringify(P)')==initial
 p.add_script_tag(path=str(A/'bf11600_original_lord_stats_reference.js'))
 assert p.locator('#bf11600-original-lord-stats').count()==1
 assert not errors,errors
 b.close()
print('PASS v116 original 2022 base/Lord stat endpoints, 72 forms, type rows, no interpolation/save/combat mutation')
