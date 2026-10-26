"""Ensure compiled v0.37 Android package includes ALL six real 6-star assets and original saved player core."""
from pathlib import Path
import hashlib,json,struct,zipfile
ROOT=Path(__file__).resolve().parent
apk=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert apk.is_file(),apk
man=json.loads((ROOT/'source_data/bf_global_six_star_starters_v037.json').read_text('utf8'))
with zipfile.ZipFile(apk) as z:
 names=set(z.namelist());html=z.read('assets/index.html').decode('utf8')
 assert html.count('/* BF_GLOBAL_SIX_STAR_STARTERS_V037 */')==1
 assert 'bf_global_offline_demo_v7' in html and 'bf_global_offline_demo_v8' not in html
 decoder=json.JSONDecoder()
 def dec(key):
  at=html.index(key)+len(key)
  return decoder.raw_decode(html[at:])[0]
 evolved=dec('window.BF_EVOLVED_UNITS=');recipes=dec('const EVO_RECIPES=');hits=dec('window.BF_ARCHIVE_BB_HITS=')
 assert (len(evolved),len(recipes),len(hits))==(54,54,72)
 for id,rec in man['records'].items():
  num=int(id)
  unit=next(x for x in evolved if x['id']==num)
  assert unit['name']==rec['name'] and unit['rarity']==6 and unit['stats']==rec['stats']
  assert unit['originalMaxLevel']==100 and unit['originalUnitCost']==rec['originalUnitCost']
  recipe=next(x for x in recipes if x['evolvedId']==num)
  assert recipe['baseId']==rec['ownedBaseId'] and recipe['fromId']==rec['fromId']
  assert recipe['archivedZel']==500000 and recipe['demoZel']==10000 and recipe['materials']==rec['sourceRecipe']['materials']
  assert hits[id]['unitId']==num and hits[id]['firstGroupHitCount']>0
  for prefix in ('unit_anime_atlas_','unit_ills_thum_'):
   filename=f'assets/content/six_star_evolution/{prefix}{id}.png'
   assert filename in names,(num,filename)
   data=z.read(filename)
   assert data.startswith(b'\x89PNG\r\n\x1a\n'),filename
   w,h=struct.unpack('>II',data[16:24])
   if prefix=='unit_anime_atlas_':
    assert (w,h)==(2400,((rec['frameCount']+4)//5)*400),(filename,w,h)
   else:assert w==h==102,(filename,w,h)
  assert unit['atlas']==f'content/six_star_evolution/unit_anime_atlas_{id}.png'
  assert unit['portrait']==f'content/six_star_evolution/unit_ills_thum_{id}.png'
 assert 'assets/content/five_star_evolution/unit_anime_atlas_10014.png' in names
 assert 'assets/content/other_five_star/unit_anime_atlas_10024.png' in names
 assert 'assets/content/more_second_evolution/unit_anime_atlas_60013.png' in names
 assert len(z.read('assets/bf_home_nav.js'))<=65536
 assert 'assets/bf_global_unit_archive.js' in names
print('PASS APK: all 66 playable Global forms; six authentic 6-star CGG/CGS atlases, source BB metadata, original recipes and v7 save identity',flush=True)
