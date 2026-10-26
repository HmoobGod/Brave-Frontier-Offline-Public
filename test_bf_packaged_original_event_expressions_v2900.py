"""v29.00 signed APK full original 2022 facial-expression provenance and signing."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
import json
R=Path(__file__).resolve().parent
archive=R/'source_assets/bf1/event/BF1_Global_Original_Event_Expressions_2022_v2900.zip'
with ZipFile(archive) as z:
 meta=json.loads(z.read('EXPRESSIONS_MANIFEST.json'))
 assert len(meta['files'])==19 and meta['frames']==405
 with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
  files=set(apk.namelist())
  for name,props in meta['files'].items():
   dest='assets/content/event/'+name
   assert dest in files,dest
   original=z.read('content/event/'+name)
   deployed=apk.read(dest)
   assert deployed==original and sha256(deployed).hexdigest()==props['sha256'],dest
  for name in ('bf2900_original_event_expressions.js','bf2800_dialogue_speaker_cues.js',
      'bf2700_original_event_stage.js','bf2600_original_event_portraits.js'):
   assert 'assets/'+name in files
  script=apk.read('assets/bf2900_original_event_expressions.js').decode('utf8')
  assert script.count('/* BF_GLOBAL_ORIGINAL_DIALOGUE_EXPRESSIONS_V2900 */')==1
  assert 'BF2900_DATA_PLACEHOLDER' not in script and len(script.encode())<65536
  assert 'localStorage' not in script and 'saveProgress(' not in script
  assert 'bf_global_offline_demo_v7' in apk.read('assets/index.html').decode('utf8')
  assert sha256(apk.read('assets/content/dungeon/dungeon_battle_10200.jpg')).hexdigest()=='50b7833e5045b5ffbf23056d33ee13d1e96654e9665e6b4d770fe6f8baef473b'
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v29.00 19 original 2022 expression PNGs byte-identical, correct script data, offline v7 identity')
