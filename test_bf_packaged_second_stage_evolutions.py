"""The final Android APK must package exact 2022 source-backed v0.33 art and data."""
from pathlib import Path
from PIL import Image
from io import BytesIO
from zipfile import ZipFile
import json,re,hashlib
ROOT=Path(__file__).resolve().parent
meta=json.loads((ROOT/'source_data/bf_global_second_stage_evolutions_v033.json').read_text())
ids={int(x) for x in meta['records']}
assert ids=={10013,20013,30013,40013,50013,60023}
apk=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert apk.is_file()
with ZipFile(apk) as package:
 files=set(package.namelist())
 html=package.read('assets/index.html').decode('utf-8')
 assert html.count('/* BF_GLOBAL_SECOND_EVOLUTIONS_V033 */')==1
 assert html.count('/* BF_GLOBAL_SIX_EVOLUTIONS_V032 */')==1
 assert html.count('const BF_VERIFIED_POWER_V033=')==1
 assert 'bf_global_offline_demo_v7' in html
 assert 'QUEST_DEMO_TIER3_MATERIALS' in html
 assert 'const recipe=EVO_RECIPES.find(r=>r.baseId===Number(bid) && r.evolvedId===value);' in html
 for path in ['assets/content/unit_archive/unit_ills_thum_10011.png','assets/content/extra_evolution/unit_anime_atlas_10042.png']:
  assert path in files
 for uid in ids:
  record=meta['records'][str(uid)]
  for kind in ('unit_anime_atlas','unit_ills_thum'):
   path=f'assets/content/second_evolution/{kind}_{uid}.png'
   assert path in files,path
   raw=package.read(path)
   assert raw.startswith(b'\x89PNG\r\n\x1a\n'),path
   image=Image.open(BytesIO(raw))
   assert image.width>0 and image.height>0
   if kind=='unit_anime_atlas':assert image.width==2400
   if kind=='unit_ills_thum':
    expected=record['sourceFilesSha256'][f'content/unit/img/unit_ills_thum_{uid}.png']
    assert hashlib.sha256(raw).hexdigest()==expected
 dec=json.JSONDecoder()
 evolved,_=dec.raw_decode(html.split('window.BF_EVOLVED_UNITS=',1)[1]);assert len(evolved)==54
 recipes,_=dec.raw_decode(html.split('const EVO_RECIPES=',1)[1]);assert len(recipes)==54
 bb,_=dec.raw_decode(html.split('window.BF_ARCHIVE_BB_HITS=',1)[1]);assert len(bb)==72
 for uid in ids:
  r=meta['records'][str(uid)]
  unit=next(x for x in evolved if x['id']==uid)
  rec=next(x for x in recipes if x['evolvedId']==uid)
  assert unit['name']==r['name'] and unit['stats']==r['stats']
  assert (rec['baseId'],rec['fromId'],rec['archivedZel'])==(r['ownedBaseId'],r['fromId'],100000)
  assert rec['materials']==r['sourceRecipe']['materials']
  assert bb[str(uid)]['bbId']==uid and bb[str(uid)]['targetAreaRaw']=='2'
print('PASS packaged v0.33: six source-verified 4-star animated forms, 54 playable, archived BB/recipe source and saved v7 identity')
