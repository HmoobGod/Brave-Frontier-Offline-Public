"""v50 complete recovered 2022 battle-item effect catalog (99 source rows)."""
from pathlib import Path
from zipfile import ZipFile
import gzip,hashlib,json
R=Path(__file__).resolve().parent
name='bf_global_2022_battle_item_effect_catalog_v5000.json.gz'
source=(R/'source_data'/name).read_bytes()
assert hashlib.sha256(source).hexdigest()=='c257f029c210cd402388fbe3fafb003da9f2e708a0beedfd89c09a811ebb7388'
raw=gzip.decompress(source)
catalog=json.loads(raw)
assert catalog['schema']=='bf-2022-battle-item-effects-v5100'
assert catalog['count']==99 and len(catalog['rows'])==99
assert all(len(r)==7 and all(isinstance(x,str) for x in r) for r in catalog['rows'])
by_id={int(r[0]):r for r in catalog['rows']}
assert len(by_id)==99
assert by_id[20600][1:]==['410','1','1','5','0,0,30,0,0,3','10']
assert by_id[50400][1:]==['400','1','2','5','0,50,0,0,0,3','5']
assert by_id[21000][1:]==['540','1','1','4','0,100','2']
assert by_id[52400][1:]==['610','1','1','12','100','2']
assert by_id[20200][1]=='530' and by_id[20200][5]=='1,0,0,0,0,0,0,0'
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 # Android AAPT expands .gz assets and removes their gzip suffix on package.
 # Verify semantic byte identity of the actual packaged data either way.
 compressed='assets/'+name
 expanded='assets/'+name[:-3]
 if compressed in z.namelist():
  assert z.read(compressed)==source
 else:
  assert expanded in z.namelist(),(expanded,z.namelist()[-20:])
  assert z.read(expanded)==raw
print('PASS v50 99 source item effects; APK catalog content verified after AAPT packaging')
