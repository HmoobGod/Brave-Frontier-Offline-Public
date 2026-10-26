"""v51 source single-ally double ATK item installed in stable signed/offline APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf4500_item_turn_reservations.js','bf4900_source_def_item.js',
              'bf5100_source_double_atk_item.js'):
  assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf5100_source_double_atk_item.js').decode('utf8')
 assert 'BF_GLOBAL_SOURCE_DOUBLE_ATK_ITEM_V5100' in js
 assert len(js.encode('utf8'))<65536
 assert 'itemId:50401' in js and "passiveSkillInfo:'0,100,0,0,0,3'" in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf5000_source_party_atk_item.js")')<j.index('readPackagedText("bf5100_source_double_atk_item.js")')
g=(R/'app/build.gradle').read_text('utf8')
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=51
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v51 original single-ally double ATK item, offline APK, v7 save, signing')
