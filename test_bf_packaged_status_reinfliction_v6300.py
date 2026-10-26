"""v63 source-status lifecycle remains intact in signed offline Android APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf5700_original_ailment_state.js','bf5800_poison_turn.js',
              'bf5900_curse_bb_lock.js','bf6000_paralysis_action_lock.js',
              'bf6100_weakness_defense.js','bf6200_injury_attack.js'):
  assert 'assets/'+name in z.namelist(),name
 for name in ('bf5800_poison_turn.js','bf5900_curse_bb_lock.js',
              'bf6000_paralysis_action_lock.js'):
  js=z.read('assets/'+name).decode('utf8')
  assert 'tokenFor(slot,' in js and 'removeCode(slot,' in js
 registry=z.read('assets/bf5700_original_ailment_state.js').decode('utf8')
 assert 'tokenFor(slot,code)' in registry and 'removeCode(slot,code)' in registry
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
version_lines=[line.strip() for line in gradle.splitlines() if line.strip().startswith('versionName ')]
assert len(version_lines)==1
version=version_lines[0].split("'")[1]
assert version.endswith('.00.0-demo') and int(version.split('.')[0])>=63
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v63 status token lifecycle, shared cures and stable signed/offline Android save identity')
