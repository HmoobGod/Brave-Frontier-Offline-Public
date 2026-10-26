"""Verify the final *compiled Android APK*, not just test source, includes v0.36 data."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,re,struct
ROOT=Path(__file__).resolve().parent
apk=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert apk.exists(),f'Missing Android build: {apk}'
manifest=json.loads((ROOT/'source_data/bf_global_other_five_star_v036.json').read_text('utf8'))
ids={int(k) for k in manifest['records']}
assert ids=={10024,20024,30024,40024,50024,60024}
with ZipFile(apk) as z:
 names=set(z.namelist())
 html=z.read('assets/index.html').decode('utf-8')
 assert html.count('/* BF_GLOBAL_OTHER_FIVE_STAR_V036 */')==1
 assert 'bf_global_offline_demo_v7' in html
 dec=json.JSONDecoder()
 def embedded(anchor):
  assert html.count(anchor)==1
  return dec.raw_decode(html.split(anchor,1)[1])[0]
 evolved=embedded('window.BF_EVOLVED_UNITS=');recipes=embedded('const EVO_RECIPES=');bbs=embedded('window.BF_ARCHIVE_BB_HITS=')
 assert (len(evolved),len(recipes),len(bbs))==(54,54,72)
 byunit={x['id']:x for x in evolved};byrecipe={x['evolvedId']:x for x in recipes}
 for uid in ids:
  source=manifest['records'][str(uid)]
  unit=byunit[uid];recipe=byrecipe[uid]
  assert (unit['name'],unit['stats'],unit['rarity'])==(source['name'],source['stats'],5)
  assert recipe['materials']==source['sourceRecipe']['materials'] and recipe['archivedZel']==200000 and recipe['demoZel']==7500
  assert bbs[str(uid)]['damageFramesRaw']==source['bb']['damageFramesRaw']
  for prefix in ('unit_anime_atlas_','unit_ills_thum_'):
   image=f'assets/content/other_five_star/{prefix}{uid}.png'
   assert image in names,image
   data=z.read(image);assert data.startswith(b'\x89PNG\r\n\x1a\n')
   if prefix.startswith('unit_anime_'):
    w,h=struct.unpack('>II',data[16:24]);assert w==2400 and h==((source['frameCount']+4)//5)*400,(uid,w,h)
 for uid in (10014,20014,30014,40014,50014,60014):
  assert f'assets/content/five_star_evolution/unit_anime_atlas_{uid}.png' in names
 for uid in (10013,20013,30013,40013,50013,60023):
  assert f'assets/content/second_evolution/unit_anime_atlas_{uid}.png' in names
 assert 'BF_VERIFIED_SUPPORT_V036' in html and 'QUEST_DEMO_SPECIAL_MATERIALS' in html
 assert 'BF_VERIFIED_RAW_LEVELS_V036' in html
 assert 'window.BFOriginalFiveStarOther' in html
 assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
 assert len(z.read('assets/bf_home_nav.js'))<=65536
 print('PASS compiled Android APK: 60 forms, 6 source-based 5-star animations/BBs, demo catalyst schedule, previous art and v7 saves')
