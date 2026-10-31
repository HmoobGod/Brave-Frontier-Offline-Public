"""v222 source-only: 31 original type-2 material item identities and image hashes."""
from collections import Counter
from pathlib import Path
import hashlib, json, os, zipfile
R = Path(__file__).resolve().parent
M = json.loads((R / 'source_data/bf_global_2022_evolution_item_art_catalog_v222.json').read_text('utf8'))
def digest(b): return hashlib.sha256(b).hexdigest()
assert M['schema'] == 'bf-global-2022-original-evolution-item-material-art-catalog-v222'
assert M['sourceArchiveSha256'] == '69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert M['sourceItemMasterSha256'] == '0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
assert M['sourceEvolutionMasterSha256'] == 'fbaae982125b78e5a203095d0bb6d8892d210c4a632aa9e2e24f70ba0e480deb'
assert M['sourceBF1ItemPackSha256'] == '735c50613f55a84d8a3717a4ee53ef513c694031aa44963c43e24b597f134e2c'
assert (M['originalEvolutionTransitions'],M['unitMaterialSlotsType1'],M['distinctUnitMaterialIdsType1'])==(1342,7107,85)
assert (M['itemMaterialSlotsType2'],M['distinctItemMaterialIdsType2'],M['legendStoneSlotCount'])==(333,31,279)
rows=M['rows']
assert len(rows)==31 and all(type(row) is list and len(row)==6 for row in rows)
assert digest(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode())==M['canonicalRowsSha256']=='3c96e0a37f8fb9cf11b924f6ebb487edd2034f02c7c11f27d9991c6efd13065c'
assert [r[0] for r in rows]==sorted({r[0] for r in rows})
assert len({r[2] for r in rows})==31 and sum(r[3] for r in rows)==333
assert sum(r[4] for r in rows)==M['originalItemImageTotalBytes']==180761
assert all(type(r[0]) is int and r[0]>0 and type(r[1]) is str and r[1]
 and type(r[2]) is str and r[2].startswith('item_thum_') and r[2].endswith('.png') and '/' not in r[2] and '\\' not in r[2]
 and type(r[3]) is int and r[3]>0 and type(r[4]) is int and r[4]>500 and type(r[5]) is str and len(r[5])==64
 and all(c in '0123456789abcdef' for c in r[5]) for r in rows)
assert next(r for r in rows if r[0]==110100)==[110100,'神越の魂石','item_thum_111000.png',279,6370,'c3decdc9ce4403cf12bf022b0ff233f802b11883105d125a6c0877d85135e0e7']
assert M['readOnlySourceCatalog'] is True
for flag in ('other30ImagesPackagedInApp','changesGameplay','changesInventory','changesSaves','unlocksPlayableEvolutions'): assert M[flag] is False
master=os.getenv('BF_ORIGINAL_2022_MST_ZIP')
if master:
 raw=Path(master).read_bytes(); assert digest(raw)==M['sourceArchiveSha256']
 with zipfile.ZipFile(master) as z:
  item_bytes=z.read(M['sourceItemMaster']);evo_bytes=z.read(M['sourceEvolutionMaster'])
 assert digest(item_bytes)==M['sourceItemMasterSha256'] and digest(evo_bytes)==M['sourceEvolutionMasterSha256']
 items={int(x['itemId']):x for x in json.loads(item_bytes)}
 evol=json.loads(evo_bytes); assert len(evol)==1342
 typ1=Counter();typ2=Counter()
 for entry in evol:
  for i in range(1,11):
   typ=int(entry[f'evoMaterialType{i}']);mid=int(entry[f'evoMaterialId{i}'])
   if mid>0:
    if typ==1:typ1[mid]+=1
    elif typ==2:typ2[mid]+=1
    else: raise AssertionError(('unrecognized original material type',typ,mid))
 assert len(typ1)==85 and sum(typ1.values())==7107
 assert len(typ2)==31 and sum(typ2.values())==333
 assert all((items[r[0]]['itemName'],items[r[0]]['itemThumbnail'],typ2[r[0]])==(r[1],r[2],r[3]) for r in rows)
pack=os.getenv('BF_ORIGINAL_2022_ITEM_PACK_ZIP')
if pack:
 raw=Path(pack).read_bytes();assert digest(raw)==M['sourceBF1ItemPackSha256']
 with zipfile.ZipFile(pack) as z:
  assert z.testzip() is None
  for r in rows:
   b=z.read('content/item/'+r[2]);assert len(b)==r[4] and digest(b)==r[5] and b[:8]==b'\x89PNG\r\n\x1a\n',r[0]
print('PASS v222: 31 original type-2 items, 333 slots; type-1 unit materials remain distinct; no gameplay changes')
