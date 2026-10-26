"""Android packaged HTML, original sprites and original Global source integrity."""
from pathlib import Path
import base64,hashlib,io,json,struct,zipfile
ROOT=Path(__file__).resolve().parent
M=json.loads((ROOT/'source_data/bf_global_more_second_stage_v034.json').read_text())
asset=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert asset.is_file(),asset
IDS={60013,10023,20023,30023,40023,50023}
with zipfile.ZipFile(asset) as apk:
 files=set(apk.namelist());s=apk.read('assets/index.html').decode('utf-8')
 assert s.count('/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */')==1
 assert s.count('/* BF_GLOBAL_SECOND_EVOLUTIONS_V033 */')==1
 assert 'bf_global_offline_demo_v7' in s
 dec=json.JSONDecoder()
 def obj(anchor):
    return dec.raw_decode(s.split(anchor,1)[1])[0]
 evolved=obj('window.BF_EVOLVED_UNITS=');recipes=obj('const EVO_RECIPES=');bb=obj('window.BF_ARCHIVE_BB_HITS=')
 assert len(evolved)==len(recipes)==54 and len(bb)==72
 assert {x['id'] for x in evolved}.issuperset(IDS)
 for uid in IDS:
    info=M['records'][str(uid)]
    row=next(r for r in evolved if r['id']==uid)
    rec=next(r for r in recipes if r['evolvedId']==uid)
    assert row['name']==info['name'] and row['stats']==info['stats']
    assert row['originalMaxLevel']==info['originalMaxLevel'] and row['rarity']==4
    assert rec['baseId']==info['ownedBaseId'] and rec['fromId']==info['fromId']
    assert rec['archivedZel']==100000 and rec['demoZel']==5000
    assert rec['materials']==info['sourceRecipe']['materials']
    assert bb[str(uid)]['bbId']==uid
    for stem in ('unit_anime_atlas','unit_ills_thum'):
      p=f'assets/content/more_second_evolution/{stem}_{uid}.png'
      assert p in files,p
      data=apk.read(p)
      assert data[:8]==b'\x89PNG\r\n\x1a\n'
      if stem=='unit_anime_atlas':
          width,height=struct.unpack('>II',data[16:24]);assert width==2400 and height==((info['frameCount']+4)//5)*400
      else: assert struct.unpack('>II',data[16:24])==(102,102)
 assert b'bf-global-original' in apk.read('assets/bf_global_unit_archive.js')
 assert len(apk.read('assets/bf_home_nav.js'))<=65536
 assert 'assets/content/extra_evolution/unit_anime_atlas_10042.png' in files
 assert 'assets/content/second_evolution/unit_anime_atlas_10013.png' in files
print('PASS v0.34 compiled Android APK: 54 playable forms; 6 new original battle atlases, recipes/skills, previous sprites and save v7')
