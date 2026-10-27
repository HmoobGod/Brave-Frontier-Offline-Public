"""v120: exact 2022 Global stat-endpoint fidelity of 2,291 archive source rows.
Source-only CI; presence in encyclopedia does NOT unlock playable units.
"""
import base64,gzip,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
D=R/'source_data'
meta=json.loads((D/'bf_global_original_unit_catalog_meta.json').read_text('utf8'))
assert meta['schema']=='bf-global-unit-archive-package-v1'
assert meta['catalogRecordCount']==2291
packed=base64.b64decode((D/'bf_global_original_unit_catalog.json.gz.b64').read_text('ascii'))
assert hashlib.sha256(packed).hexdigest()==meta['catalogGzipSha256']
raw=gzip.decompress(packed)
assert len(raw)==meta['catalogJsonBytes']
assert hashlib.sha256(raw).hexdigest()==meta['catalogJsonSha256']
archive=json.loads(raw)
assert archive['schema']=='bf-global-unit-archive-2022-v1'
units=archive['units']
assert len(units)==2291
# Independently derived from original owner mst-decoded.zip, authenticated
# F_UNIT_MST_1/2_Ver1084 source hashes. Not estimated/interpolated.
keys=('id','unitMaxLevel','unitBaseHp','unitLordHp','unitBaseAtk',
      'unitLordAtk','unitBaseDef','unitLordDef','unitBaseRec','unitLordRec')
rows=[]
for u in units:
    vals=[u.get(k) for k in keys]
    assert all(type(v)==int for v in vals),(u.get('id'),vals)
    assert vals[0]>0 and vals[1]>0 and all(v>0 for v in vals[2:])
    assert all(vals[k+1]>=vals[k] for k in (2,4,6,8)),u.get('id')
    rows.append(vals)
rows.sort(key=lambda row:row[0])
assert len({x[0] for x in rows})==2291
digest=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
assert digest=='a10b45bb5fa10f555cbbcfb31793f65b9a1a8c3f702611b5ea66d7a1be644914',digest
by_id={u['id']:u for u in units}
assert by_id[1]['unitMaxLevel']==500
assert sum(u['unitMaxLevel']==1 for u in units)==127
old=json.loads((D/'bf_global_2022_playable_lord_stat_endpoints_v116.json').read_text('utf8'))
assert len(old['rows'])==old['unitCount']==72
assert old['source']['archiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
for entry in old['rows']:
    uid=entry['unitId']
    assert by_id[uid]['unitMaxLevel']==entry['maxLevel'],uid
    for stat in ('hp','atk','def','rec'):
        cap=stat.capitalize()
        assert by_id[uid]['unitBase'+cap]==entry['base'][stat],(uid,stat,'base')
        assert by_id[uid]['unitLord'+cap]==entry['lordAtMax'][stat],(uid,stat,'lord')
assert by_id[10011]['unitMaxLevel']==12
assert by_id[10025]['unitMaxLevel']==100
assert by_id[60015]['unitLordHp']==5942
print('PASS v120: 2,291/2,291 original source ID, max level and 8 base/Lord endpoint fields; 72/72 playable joins; read-only')
