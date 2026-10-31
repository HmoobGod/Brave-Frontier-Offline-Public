"""v220: verify the actual compiled APK contains 15 new original JPGs and adapter."""
from pathlib import Path
import hashlib,zipfile
import prepare_bf_original_2022_dungeon_backdrops_v22000 as v220
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
APK=R/'app/build/outputs/apk/debug/app-debug.apk'
manifest,old,new=v220.verified_catalog()
assert len(old)==29 and len(new)==77
with zipfile.ZipFile(APK) as apk:
 assert apk.testzip() is None
 for meta in manifest['imageSources']:
  asset=A/'content/dungeon'/meta['file']
  data=asset.read_bytes()
  assert len(data)==meta['sizeBytes'] and hashlib.sha256(data).hexdigest()==meta['sha256']
  assert apk.read('assets/content/dungeon/'+meta['file'])==data
 for name in ('bf19100_original_2022_dungeon_backdrops.js',
              'bf22000_original_2022_additional_dungeon_backdrops.js',
              'bf3800_source_battle_backdrop.js'):
  assert apk.read('assets/'+name)==(A/name).read_bytes(),name
 js=apk.read('assets/bf22000_original_2022_additional_dungeon_backdrops.js').decode('utf8')
 assert 'rows.length!==77' in js and 'saveProgress(' not in js
 oldjs=apk.read('assets/bf19100_original_2022_dungeon_backdrops.js').decode('utf8')
 assert 'rows.length!==29' in oldjs
 v38=apk.read('assets/bf3800_source_battle_backdrop.js').decode('utf8')
 assert 'BFGlobalOriginalDungeonBackdropsV22000?.lookup?.(q.missionId)' in v38
 assert 'BFGlobalOriginalDungeonBackdropsV19100?.lookup?.(q.missionId)' in v38
 assert apk.read('assets/index.html')==(A/'index.html').read_bytes()
 java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
 assert java.index('readPackagedText("bf19100_original_2022_dungeon_backdrops.js")')<java.index('readPackagedText("bf22000_original_2022_additional_dungeon_backdrops.js")')
 assert 'bf_global_offline_demo_v7' in (A/'index.html').read_text('utf8')
print('PASS v220 packaged APK: all 22 original 2022 JPGs, 106 mission source lookups, no native wave/AI claims')
