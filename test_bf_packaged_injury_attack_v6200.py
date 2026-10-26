"""v62 Injury ATK status consequence inside signed and offline Android APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf5700_original_ailment_state.js','bf6000_paralysis_action_lock.js',
              'bf6100_weakness_defense.js','bf6200_injury_attack.js'):
  assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf6200_injury_attack.js').decode('utf8')
 assert 'BF_GLOBAL_INJURY_ATTACK_V6200' in js and len(js.encode('utf8'))<65536
 assert 'statusCode:4' in js and 'penaltyPercent:50' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf6100_weakness_defense.js")')<java.index('readPackagedText("bf6200_injury_attack.js")')
gradle=(R/'app/build.gradle').read_text('utf8')
# Inherited v62 regression accepts new version names while preserving floor.
lines=[x.strip() for x in gradle.splitlines() if x.strip().startswith('versionName ')]
assert len(lines)==1
release=lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=62
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v62 original-source Injury identity, community ATK effect and stable offline Android signer/save')
