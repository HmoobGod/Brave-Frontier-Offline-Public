"""Verify v46 signed Android APK packages source BB meter effect, without save migration."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf4500_item_turn_reservations.js','bf4200_demo_potion_command.js',
              'bf4300_source_party_heal.js','bf4400_source_atk_item.js',
              'bf4600_source_bb_gauge_item.js'):
  assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf4600_source_bb_gauge_item.js').decode('utf8')
 assert 'BF_GLOBAL_SOURCE_BB_GAUGE_ITEM_V4600' in js and len(js.encode('utf8'))<65536
 assert 'itemId:21000' in js and "passiveSkillInfo:'0,100'" in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
# Retain inherited v46 source packaging gates on future releases.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=46
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v46: source BB item, signed offline APK, v7 saved identity')
