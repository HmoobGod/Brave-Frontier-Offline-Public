"""v61 community-grounded Weakness DEF reduction in offline signed Android APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf5700_original_ailment_state.js','bf5800_poison_turn.js',
              'bf5900_curse_bb_lock.js','bf6000_paralysis_action_lock.js',
              'bf6100_weakness_defense.js'):
  assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf6100_weakness_defense.js').decode('utf8')
 assert 'BF_GLOBAL_WEAKNESS_DEFENSE_V6100' in js and len(js.encode('utf8'))<65536
 assert 'penaltyPercent:50' in js and 'statusCode:2' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf6000_paralysis_action_lock.js")')<j.index('readPackagedText("bf6100_weakness_defense.js")')
g=(R/'app/build.gradle').read_text('utf8')
# Inherited v61 package check retains its minimum version in later APKs.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=61
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v61 Weakness effect and unchanged signed offline v7 package')
