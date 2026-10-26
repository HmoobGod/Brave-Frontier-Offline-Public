"""v48 Android APK contains guarded Auto toggle without save or signer migration."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf4500_item_turn_reservations.js','bf4700_source_full_revive.js',
              'bf4800_demo_auto_item_guard.js'):
  assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf4800_demo_auto_item_guard.js').decode('utf8')
 assert 'BF_GLOBAL_DEMO_AUTO_ITEM_GUARD_V4800' in js
 assert len(js.encode('utf8'))<65536
 assert 'stopImmediatePropagation' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf4700_source_full_revive.js")')<java.index('readPackagedText("bf4800_demo_auto_item_guard.js")')
g=(R/'app/build.gradle').read_text('utf8')
# Earlier package assertions accept compatible subsequent builds.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=48
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v48: Auto item-Guard protection APK, offline identity, v7 save key')
