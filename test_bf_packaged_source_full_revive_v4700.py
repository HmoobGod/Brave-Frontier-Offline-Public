"""v47 original #52400 full-revive prototype safely packaged in offline Android."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf4500_item_turn_reservations.js','bf4200_demo_potion_command.js',
              'bf4300_source_party_heal.js','bf4400_source_atk_item.js',
              'bf4600_source_bb_gauge_item.js','bf4700_source_full_revive.js'):
  assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf4700_source_full_revive.js').decode('utf8')
 assert 'BF_GLOBAL_SOURCE_FULL_REVIVE_ITEM_V4700' in js and len(js.encode('utf8'))<65536
 assert 'itemId:52400' in js and "passiveSkillInfo:'100'" in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
# Prior-release packaging test applies to v47 and all successors.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=47
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v47 full revive source item, signed offline APK and stable v7 saved identity')
