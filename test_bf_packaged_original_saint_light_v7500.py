"""v75 signed offline APK contains exact Saint Light source-scope base 1000."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf7500_original_saint_light.js' in z.namelist()
 js=z.read('assets/bf7500_original_saint_light.js').decode('utf8')
 assert 'BF_GLOBAL_ORIGINAL_SAINT_LIGHT_V7500' in js
 assert 'itemId:20101' in js and 'baseHeal:1000' in js
 assert "'saint-light-demo'" in z.read('assets/bf4500_item_turn_reservations.js').decode('utf8')
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
version_lines=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(version_lines)==1 and version_lines[0].split("'")[1].endswith('.00.0-demo')
assert int(version_lines[0].split("'")[1].split('.')[0])>=75
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v75 source Saint Light party heal and original Android offline identity')
