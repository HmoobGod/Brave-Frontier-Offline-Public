"""Authenticates v224 source-only mission reward / exchange references; no rewards granted."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import os
import zipfile

ROOT = Path(__file__).resolve().parent
CAT = json.loads((ROOT/'source_data/bf_global_2022_material_acquisition_evidence_v224.json').read_text('utf-8'))
ART = json.loads((ROOT/'source_data/bf_global_2022_evolution_item_art_catalog_v222.json').read_text('utf-8'))
SHA=lambda x: hashlib.sha256(x).hexdigest()
CANON=lambda x: json.dumps(x,ensure_ascii=False,separators=(',',':')).encode('utf-8')
assert CAT['schema']=='bf-global-2022-typed-evolution-item-mission-and-exchange-source-v224'
assert CAT['sourceArchiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert ART['canonicalRowsSha256']==CAT['sourceCatalogRowsSha256']=='3c96e0a37f8fb9cf11b924f6ebb487edd2034f02c7c11f27d9991c6efd13065c'
assert (CAT['missionRewardReferenceCount'],CAT['missionReferenceDistinctIds'],CAT['exchangeOfferCount'],CAT['exchangeDistinctItemIds'])==(10,9,152,15)
assert CAT['exchangeItemTokenFieldCounts']==[[4,36],[5,116]]
for k in ('readOnlySourceEvidence',): assert CAT[k] is True
for k in ('changesGameplay','changesInventory','changesSaveSchema','grantsItems','enablesPurchases','enablesEvolution'): assert CAT[k] is False
assert len(CAT['uncertainties'])>=3
assert len(CAT['sourceTables'])==6 and len({x['file'] for x in CAT['sourceTables']})==6
assert all(x['file'].startswith('3-mst-translated/F_') and x['file'].endswith('.json') and len(x['sha256'])==64 for x in CAT['sourceTables'])
items={r[0] for r in ART['rows']};assert len(items)==31
missions=CAT['missionMaterialReferences']
assert len(missions)==10 and [r[0] for r in missions]==sorted(r[0] for r in missions)
assert SHA(CANON(missions))==CAT['missionRowsSha256']=='0e8c4d0738b40c8730d18cc9b18b7aea588b3e34b8c9620ded1161af2b07a87a'
for mid,name,token,rewards in missions:
 assert type(mid) is int and mid>0 and type(name) is str and name and token in rewards.split(',')
 parts=token.split(':');assert len(parts)==5 and parts[0]=='4' and int(parts[1]) in items
assert len({r[0] for r in missions})==9
counts=CAT['exchangeItemOfferCounts']
assert counts==sorted(counts) and len(counts)==15 and sum(q for _,q in counts)==152 and all(k in items and q>0 for k,q in counts)
assert [k for k,v in counts if k==110100 and v==124]==[110100]
assert SHA(CANON(counts))==CAT['exchangeCountsSha256']=='6e2e44d093f585caa98b899e6f45b599337a7272e1d9c05fdb210fda5348d401'
ids=CAT['exchangeOfferIds'];assert len(ids)==152 and len({a for a,b in ids})==152
assert ids==sorted(ids) and Counter(b for a,b in ids)==dict(counts)
assert SHA(CANON(ids))==CAT['exchangeOfferIdsSha256']=='33a77f04f0c09820f63ddba20d346fc67a7a28062480e0f551a4d96725ae2fad'
assert len(CAT['legendStoneHistoricalOfferExamples'])==5
for r in CAT['legendStoneHistoricalOfferExamples']:
 assert len(r)==8 and r[1]==110100 and [r[0],r[1]] in ids and r[4].startswith('4:110100:')
archive=os.environ.get('BF_ORIGINAL_2022_MST_ZIP')
if archive:
 p=Path(archive);assert SHA(p.read_bytes())==CAT['sourceArchiveSha256']
 with zipfile.ZipFile(p) as z:
  data={x['file']:json.loads(b) for x in CAT['sourceTables'] if (b:=z.read(x['file'])) and SHA(b)==x['sha256']}
 assert len(data)==6
 source_missions=[];source_offers=[];format_counts=Counter()
 for table in CAT['sourceTables']:
  for r in data[table['file']]:
   if 'F_MISSION_MST_' in table['file']:
    raw=r.get('missionRewards') or ''
    for tok in raw.split(','):
     x=tok.split(':')
     if len(x)==5 and x[0]=='4' and x[1].isdigit() and int(x[1]) in items:
      source_missions.append([int(r['missionId']),r['missionName'],tok,raw])
   else:
    tok=r.get('exchangeHallItem') or '';x=tok.split(':')
    if len(x) in (4,5) and x[0]=='4' and x[1].isdigit() and int(x[1]) in items:
     source_offers.append([int(r['exchangeHallId']),int(x[1])]);format_counts[len(x)]+=1
 assert sorted(source_missions,key=lambda r:(r[0],r[2]))==missions
 assert sorted(source_offers)==ids and sorted(map(list,format_counts.items()))==CAT['exchangeItemTokenFieldCounts']
 assert all(x['count']==len(data[x['file']]) for x in CAT['sourceTables'])
print('PASS v224 source-only: 10 mission material references / 9 missions, 152 historical exchange references / 15 items, 36 four-field variants, fail closed; no inventory or save effects')
