"""v58 poison-turn source and external-reference isolation in offline APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf5700_original_ailment_state.js','bf5800_poison_turn.js'):
  assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf5800_poison_turn.js').decode('utf8')
 assert 'BF_GLOBAL_POISON_TURN_V5800' in js
 assert len(js.encode('utf8'))<65536
 assert 'Math.floor(p.maxHp/10)' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf5700_original_ailment_state.js")')<j.index('readPackagedText("bf5800_poison_turn.js")')
g=(R/'app/build.gradle').read_text('utf8')
# Inherited v58 package gate permits new version names, while current test pins v59.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=58
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v58 poison tick module and preserved signed offline v7 Android identity')
