"""v54 original Hope Light battle effect safely packaged in Android APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf4500_item_turn_reservations.js','bf5300_source_party_def_item.js',
              'bf5400_source_hope_light.js'):
  assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf5400_source_hope_light.js').decode('utf8')
 assert 'BF_GLOBAL_SOURCE_HOPE_LIGHT_V5400' in js and len(js.encode('utf8'))<65536
 assert 'itemId:50100' in js and "passiveSkillInfo:'1500,1500,0,0'" in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf5300_source_party_def_item.js")')<j.index('readPackagedText("bf5400_source_hope_light.js")')
g=(R/'app/build.gradle').read_text('utf8')
# Inherited v54 regression may run against later version names.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=54
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v54 original Hope Light + offline signed Android save-compatible identity')
