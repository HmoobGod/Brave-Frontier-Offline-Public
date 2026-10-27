"""v116: prepare *read-only* 2022 Lord stat endpoints for 72 playable forms.

The 2022 master provides unitBaseHp/Atk/Def/Rec, unitLordHp/Atk/Def/Rec,
max level, EXP pattern, and raw six type modifiers. It does NOT establish
a full stat-growth interpolation, type-roll RNG, or EXP level thresholds.
"""
from pathlib import Path
import json,hashlib

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json'
LEADERS=ROOT/'source_data/bf_global_2022_playable_leader_catalog_v112.json'
CAPS=ROOT/'source_data/bf_global_2022_playable_level_caps_v115.json'
OUT=ROOT/'app/src/main/assets/bf11600_original_lord_stats_data.js'
v=json.loads(SRC.read_text('utf8'))
leaders=json.loads(LEADERS.read_text('utf8'))
caps=json.loads(CAPS.read_text('utf8'))
assert v['schema']=='bf-global-2022-playable-lord-stat-endpoints-v116'
assert v['unitCount']==len(v['rows'])==leaders['totalForms']==caps['supportedForms']==72
assert v['rawUnitTypeCount']==len(v['unitTypeRaw'])==6
assert v['source']['archiveSha256']==leaders['source']['zipSha256']==caps['provenance']['archiveSha256']
assert v['source']['units']==leaders['source']['unitMasters']
assert v['source']['typeMaster']=={
 'file':'3-mst-translated/F_UNIT_TYPE_MST_Ver52.json',
 'sha256':'69cc9a357b1915d31f852346e144fd6b4a0e61c9d7d64e0ac9c1a60297a10301'}
rows={int(x['unitId']):x for x in v['rows']}
assert len(rows)==72 and set(rows)=={x['unitId'] for x in leaders['rows']}
first=caps['firstStarterCapByElement']
for element in range(1,7):
 for i in range(5):
  assert rows[element*10000+11+i]['maxLevel']==first[str(element)][i]
  assert rows[element*10000+21+i]['maxLevel']==caps['secondStarterCap'][i]
 for i in range(2):
  assert rows[element*10000+41+i]['maxLevel']==caps['alternateCap'][i]
for id,row in rows.items():
 assert row['unitId']==id and row['expPatternId'] in (10,15,20)
 assert row['maxLevel'] in (12,30,40,60,80,100)
 for key in ('base','lordAtMax'):
  assert sorted(row[key])==['atk','def','hp','rec']
  assert all(isinstance(n,int) and 1<=n<=100000 for n in row[key].values())
 for key in ('hp','atk','def','rec'):
  assert row['lordAtMax'][key]>=row['base'][key],(id,key)
assert rows[10011]['base']=={'hp':1030,'atk':500,'def':410,'rec':320}
assert rows[10011]['lordAtMax']=={'hp':1948,'atk':700,'def':574,'rec':448}
assert rows[10015]['lordAtMax']['hp']==5313
assert rows[50011]['maxLevel']==30 and rows[60015]['lordAtMax']['hp']==5942
assert [x['unitTypeId'] for x in v['unitTypeRaw']]==[1,2,3,4,5,6]
assert v['unitTypeRaw'][1]['unitTypeHpRaw']=='5,10'
assert v['unitTypeRaw'][5]['unitTypeChanceRaw']=='0.00'

# Embed the audit payload as an immutable, versioned JS constant. No source
# interpolation and no mutation of game HTML or saved progress at this stage.
payload={
  'schema':v['schema'],'unitCount':72,'rawUnitTypeCount':6,
  'source':v['source'],'rows':v['rows'],'unitTypeRaw':v['unitTypeRaw'],
  'liveStatsChanged':False,'saveFieldsAdded':0,
  'nativeGrowthAndRoundingVerified':False
}
encoded=json.dumps(payload,separators=(',',':'),ensure_ascii=True)
js=("/* BF_GLOBAL_2022_LORD_STATS_DATA_V11600 */\n"+
    "(()=>{'use strict';if(window.BFGlobalOriginalLordStatsDataV11600)return;"+
    "window.BFGlobalOriginalLordStatsDataV11600=Object.freeze("+encoded+");"+
    "})();\n")
if OUT.exists() and OUT.read_text('utf8')==js:
 print('PASS v116 prepared original base/Lord reference unchanged')
else:
 OUT.write_text(js,'utf8')
 print('PASS v116 prepared original 72×8 stat endpoints and 6 raw types')
print('v116 reference JS sha256',hashlib.sha256(js.encode('utf8')).hexdigest())
