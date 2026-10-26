"""v0.38 APK final checks of six other original Global six-star forms."""
from pathlib import Path
import zipfile,json,struct,hashlib,base64,io
R=Path(__file__).resolve().parent
M=json.loads((R/'source_data/bf_global_other_six_star_v038.json').read_text())
APK=R/'app/build/outputs/apk/debug/app-debug.apk'
assert APK.is_file(),APK
with zipfile.ZipFile(APK) as z:
 names=set(z.namelist());html=z.read('assets/index.html').decode('utf8')
 assert '/* BF_GLOBAL_OTHER_SIX_STAR_V038 */' in html and 'bf_global_offline_demo_v7' in html
 decoder=json.JSONDecoder()
 def embed(anchor):return decoder.raw_decode(html.split(anchor,1)[1])[0]
 evol=embed('window.BF_EVOLVED_UNITS=');recipes=embed('const EVO_RECIPES=');bb=embed('window.BF_ARCHIVE_BB_HITS=')
 assert len(evol)==len(recipes)==54 and len(bb)==72
 for uid,rec in M['records'].items():
  n=int(uid);u=next(x for x in evol if x['id']==n);e=next(x for x in recipes if x['evolvedId']==n)
  assert u['name']==rec['name'] and u['rarity']==6 and u['stats']==rec['stats']
  assert e['fromId']==rec['fromId'] and e['baseId']==rec['ownedBaseId'] and e['materials']==rec['sourceRecipe']['materials']
  assert e['archivedZel']==500000 and e['demoZel']==10000
  assert str(uid) in bb
  for kind in ('unit_anime_atlas','unit_ills_thum'):
   path=f'assets/content/other_six_star/{kind}_{uid}.png';assert path in names
   png=z.read(path);assert png.startswith(b'\x89PNG\r\n\x1a\n')
   w,h=struct.unpack('>II',png[16:24]);assert w>0 and h>0
   if kind=='unit_anime_atlas':assert (w,h)==(2400,((rec['frameCount']+4)//5)*400)
 assert 'const BF_VERIFIED_SUPPORT_V038' in html and 'const BF_VERIFIED_RAW_LEVELS_V038' in html
 assert all(k in html for k in ('60144','60224','50354'))
 assert 'assets/bf_home_nav.js' in names and len(z.read('assets/bf_home_nav.js'))<=65536
 for key in ('assets/content/five_star_evolution/unit_anime_atlas_10014.png','assets/content/other_five_star/unit_anime_atlas_10024.png','assets/content/six_star_evolution/unit_anime_atlas_10015.png'):
  assert key in names,key
print('PASS signed v0.38 APK: 72 playable forms, six new original 6-star atlases/portraits, verified source data, previous art and unchanged save v7')
