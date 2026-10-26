"""Check Android Build APK: six authenticated original 5-star starter forms and saves."""
from __future__ import annotations
import json,zipfile,re,io,base64,hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
APK=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert APK.is_file(),f'Missing Android build output: {APK}'
M=json.loads((ROOT/'source_data/bf_global_six_five_star_v035.json').read_text('utf8'))
ids={int(k) for k in M['records']};assert ids=={10014,20014,30014,40014,50014,60014}
with zipfile.ZipFile(APK) as z:
 files=set(z.namelist());html=z.read('assets/index.html').decode('utf8')
 assert html.count('/* BF_GLOBAL_FIVE_STAR_STARTERS_V035 */')==1
 assert html.count('/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */')==1
 assert 'bf_global_offline_demo_v7' in html
 def embedded(anchor):
  assert html.count(anchor)==1
  return json.JSONDecoder().raw_decode(html[html.index(anchor)+len(anchor):])[0]
 evolved=embedded('window.BF_EVOLVED_UNITS=');recipes=embedded('const EVO_RECIPES=');bb=embedded('window.BF_ARCHIVE_BB_HITS=')
 assert len(evolved)==54 and len(recipes)==54 and len(bb)==72
 assert ids.issubset({x['id'] for x in evolved if x['rarity']==5}), 'Original six 5-star starters must all remain packaged'
 assert ids.issubset({x['evolvedId'] for x in recipes if x['targetRarity']==5}), 'Original six 5-star starter recipes must remain intact'
 assert 'QUEST_DEMO_TIER4_MATERIALS=' in html
 for id in ids:
  r=M['records'][str(id)];unit=next(x for x in evolved if x['id']==id)
  recipe=next(x for x in recipes if x['evolvedId']==id)
  assert unit['name']==r['name'] and unit['stats']==r['stats'] and unit['originalMaxLevel']==80
  assert recipe['materials']==r['sourceRecipe']['materials'] and recipe['demoZel']==7500 and recipe['archivedZel']==200000
  assert bb[str(id)]['bbId']==id and bb[str(id)]['targetAreaRaw']=='2'
  for prefix in ('unit_anime_atlas','unit_ills_thum'):
   name=f'assets/content/five_star_evolution/{prefix}_{id}.png'
   assert name in files,name
   image=z.read(name);assert image.startswith(b'\x89PNG\r\n\x1a\n')
   w,h=struct.unpack('>II',image[16:24]);assert w>0 and h>0
   if prefix=='unit_anime_atlas':assert (w,h)==(2400,400*((r['frameCount']+4)//5))
 assert 'assets/bf_home_nav.js' in files and len(z.read('assets/bf_home_nav.js'))<=65536
 assert sum(n.startswith('assets/content/unit_archive/') and n.endswith('.png') for n in files)==127
print('PASS APK packaged 60 playable forms, six new source-authenticated 5-star atlases/portraits, 127 archived thumbnails, v7 saves')
