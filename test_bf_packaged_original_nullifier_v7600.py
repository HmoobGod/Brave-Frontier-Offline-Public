"""v76 signed offline APK exposes source Nullifier without saved inventory changes."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf7600_original_status_nullifier.js' in z.namelist()
 js=z.read('assets/bf7600_original_status_nullifier.js').decode('utf8')
 assert 'BF_GLOBAL_ORIGINAL_STATUS_NULLIFIER_V7600' in js
 assert 'itemId:20250' in js and 'itemTargetArea:2' in js
 assert "'100,100,100,100,100,100,3,0'" in js
 assert 'BFGlobalStatusNegationV7600?.immune(slot,code)' in z.read('assets/bf5700_original_ailment_state.js').decode('utf8')
 assert "'nullifier-demo'" in z.read('assets/bf4500_item_turn_reservations.js').decode('utf8')
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
version_lines=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(version_lines)==1 and version_lines[0].split("'")[1].endswith('.00.0-demo')
assert int(version_lines[0].split("'")[1].split('.')[0])>=76
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v76 source Nullifier status negation in signed offline APK and original v7 save')
