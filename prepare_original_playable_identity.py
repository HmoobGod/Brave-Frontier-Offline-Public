"""Restore original 2022 Global playable unit names and read-only identity details.

Corrects placeholder names across the existing 18 base and 12 evolved forms.
No unit creation, stage progression, stats, saves, damage or summon rates change.
The archived max level/cost are *informational*: DEMO training still uses its
existing levels/rules until actual experience tables are independently restored.
Checks the SHA-256 of the already-committed original master catalog and all
existing baseline stats before mutation; idempotent and fails closed.
"""
from __future__ import annotations
import base64,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
source=ROOT/'source_data'
html_path=ROOT/'app/src/main/assets/index.html'
meta=json.loads((source/'bf_global_original_unit_catalog_meta.json').read_text())
compressed=base64.b64decode((source/'bf_global_original_unit_catalog.json.gz.b64').read_text('ascii'))
assert hashlib.sha256(compressed).hexdigest()==meta['catalogGzipSha256']
raw=gzip.decompress(compressed)
assert hashlib.sha256(raw).hexdigest()==meta['catalogJsonSha256']
archive={str(x['id']):x for x in json.loads(raw)['units']}
manifest=json.loads((source/'bf_global_original_playable_identity_v031.json').read_text())
assert manifest['schema']=='bf-global-original-playable-identity-v031'
assert manifest['count']==len(manifest['records'])==30
assert manifest['provenance']['catalogJsonSha256']==meta['catalogJsonSha256']
assert manifest['provenance']['sourceArchiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
records=manifest['records']
for uid,row in records.items():
    src=archive[uid]
    assert row['name']==src['name'] and src['nameSource']=='2022_Global_English'
    assert row['element']==src['element'] and row['rarity']==src['rarity']
    assert row['maxLevel']==src['unitMaxLevel'] and row['cost']==src['unitCost']
    assert row['baseStats']=={x:src['unitBase'+x.title()] for x in ('hp','atk','def','rec')}
    assert row['lordStats']=={x:src['unitLord'+x.title()] for x in ('hp','atk','def','rec')}

html=html_path.read_text('utf-8')
assert 'bf_global_offline_demo_v7' in html
start_marker='/* BF_ORIGINAL_GLOBAL_PLAYABLE_IDENTITY_V031 */'
anchor='const STARTERS=window.BF_STARTER_UNITS; // Entire 12-unit demo catalog.'
assert html.count(anchor)==1
if start_marker in html:
    assert html.count(start_marker)==1 and 'window.BFOriginalPlayableIdentity' in html
    print('PASS existing original Global playable names and profile references are intact.')
else:
    js='''/* BF_ORIGINAL_GLOBAL_PLAYABLE_IDENTITY_V031 */
// Original 2022 Global names, elements, caps and stat endpoints. Source
// level caps are READ-ONLY until original unit EXP mechanics are recovered.
// Saves, damage stats, roster IDs, rarity, summoning and artwork do not change.
const BF_ORIGINAL_PLAYABLE_IDENTITY=Object.freeze(__DATA__);
for(const unit of [...window.BF_STARTER_UNITS,...window.BF_EVOLVED_UNITS]){
 const identity=BF_ORIGINAL_PLAYABLE_IDENTITY[String(unit.id)];
 if(!identity)throw Error('Missing original unit identity: '+unit.id);
 unit.name=identity.name;
 unit.originalMaxLevel=identity.maxLevel;
 unit.originalUnitCost=identity.cost;
 unit.originalLordStats=identity.lordStats;
}
window.BFOriginalPlayableIdentity=Object.freeze({
 count:30,
 forUnit:id=>BF_ORIGINAL_PLAYABLE_IDENTITY[String(id)]||null
});
'''.replace('__DATA__',json.dumps(records,separators=(',',':'),ensure_ascii=True))
    html=html.replace(anchor,js+anchor)
    print('Staged 30 source-backed original Global playable names.')
# Show archived cap and cost without deceptively capping DEMO training.
old="detail.textContent=(owned?'':'🔒 Not owned · ')+visible.element+' · ★'+visible.rarity+' · Lv.'+demoLevel(P.unitExp[unit.id])+' · '+visible.stats.hp+' base HP';"
new="detail.textContent=(owned?'':'🔒 Not owned · ')+visible.element+' · ★'+visible.rarity+' · Demo Lv.'+demoLevel(P.unitExp[unit.id])+' · Original cap Lv.'+visible.originalMaxLevel+' · Original cost '+visible.originalUnitCost+' · '+visible.stats.hp+' source base HP';"
assert html.count(old)+html.count(new)==1,'Unexpected existing squad picker UI anchor'
html=html.replace(old,new)
assert html.count(start_marker)==1
html_path.write_text(html,'utf-8')
print('PASS v0.31: 30 original English names, stat provenance and informational caps staged; save v7 unchanged')
