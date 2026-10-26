"""v44.00 signed APK includes optional source %ATK item, unchanged v7 identity."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf4200_demo_potion_command.js','bf4300_source_party_heal.js','bf4400_source_atk_item.js'):
  assert 'assets/'+name in z.namelist()
 js=z.read('assets/bf4400_source_atk_item.js').decode('utf8')
 assert 'BF_GLOBAL_SOURCE_ATK_ITEM_V4400' in js and len(js.encode('utf8'))<65536
 assert 'itemId:20400' in js and 'atkPercent:30' in js and 'durationTurns:3' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
# Inherited v44 package gate must permit later releases while rejecting
# rollback below v44; the current release's own gate checks its exact version.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=44
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v44.00 packaged source ATK item, signed offline and save identity unchanged')