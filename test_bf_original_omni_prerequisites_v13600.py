"""v136: exact original 2022 Global Omni upgrade reference gate.

No non-2022 formulas, no paid evolution, no changes to v7 saves or the 72
existing playable forms. The raw owner's 2022 source files were verified
against the 59 MB original archive before normalizing this source manifest.
"""
from pathlib import Path
import json,hashlib,collections,base64,gzip
R=Path(__file__).resolve().parent
m=json.loads((R/'source_data/bf_global_2022_omni_prerequisites_v136.json').read_text('utf8'))
assert m['schema']=='bf-global-2022-omni-source-prerequisites-v136'
assert m['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert m['sourceFileSha256']=={
 'omniLevels':'db16370d5c4d93a7010027cf9c7deed1e76a052f377303491a393bf0a489890b',
 'omniRecipes':'3010172d8fb7b3d799766f87290a1511b067312e86fa1b4e7b5ede5e51cfd657',
 'omniCosts':'8f00b1a50fa0951e85040505af1f2d168ec6f311754cf83358ccbd36d74fa346'}
L=m['levels'];P=m['recipes'];C=m['methodCosts']
assert (len(L),len(P),len(C))==(18,70,36)
canonical=json.dumps([L,P,C],separators=(',',':'))
assert hashlib.sha256(canonical.encode()).hexdigest()==m['canonicalTableSha256']=='c9434f360bb0e35edce2182c145f2e99e4e32c60bc9b446606a0d04d42a7a27b'
assert len({(r[0],r[1]) for r in L})==18
assert len({(r[0],r[1],r[2]) for r in C})==36
assert sorted({r[0] for r in L})==[45,47,48,50,54,60]
assert collections.Counter(r[1] for r in L)=={1:6,2:6,3:6}
assert all(len(r)==4 and len(r[2])==4 and all(isinstance(x,int) for x in r[2]) for r in L)
assert collections.Counter(r[3] for r in P)=={'ITEM':34,'ELE_SHARD':18,'DUPLICATE':18}
assert all((r[0],r[1],r[2]) in {(c[0],c[1],c[2]) for c in C} for r in P)
assert all(r[3] in ('ITEM','ELE_SHARD','DUPLICATE') and r[5]>0 for r in P)
assert all(len(r[4])==6 and set(r[4])==set(range(800901,800907)) for r in P if r[3]=='ELE_SHARD')
assert all(len(r[4])==1 and r[4][0] in (800907,800908) for r in P if r[3]=='ITEM')
assert all(r[4]==[0] for r in P if r[3]=='DUPLICATE')
assert m['runtimeEnabled'] is False and m['sourceItemJoinVerified'] is True
# The six original 8★ starter forms have source unitCost 45, not six
# additional owned/playable units. Their exact v127 prerequisite is intact.
v127=json.loads((R/'source_data/bf_global_2022_starter_7_8_source_readiness_v127.json').read_text('utf8'))
rows=v127['rows']; assert len(rows)==12
assert {r['unitId'] for r in rows if r['rarity']==8}=={10017,20017,30017,40017,50017,60017}
assert all(r['unitCost']==45 for r in rows if r['rarity']==8)
# Original full archival ID join, unaffected by optional Omni study.
archive=json.loads(gzip.decompress(base64.b64decode((R/'source_data/bf_global_original_unit_catalog.json.gz.b64').read_text('ascii'))))
assert len(archive['units'])==2291
archiveById={u['id']:u for u in archive['units']}
assert all(archiveById[r['unitId']]['unitCost']==45 for r in rows if r['rarity']==8)
# CI insists the original Android package/load/save is unchanged.
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
html=(R/'app/src/main/assets/index.html').read_text('utf8')
assert 'bf13600_omni_prerequisites.js' not in java
assert 'bf_global_offline_demo_v7' in html
assert not (R/'app/src/main/assets/bf13600_omni_prerequisites.js').exists()
print('PASS v136: original 2022 Global Omni 18 level/70 typed recipe/36 cost records, 6 archived 8★ joins, no v7 mutation')
