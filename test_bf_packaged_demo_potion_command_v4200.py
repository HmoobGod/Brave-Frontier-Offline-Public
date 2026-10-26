"""v42.00 signed APK keeps optional demo potion isolated from saved progress."""
from pathlib import Path
from zipfile import ZipFile
import re
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 assert 'assets/bf4200_demo_potion_command.js' in names
 assert 'assets/bf4100_live_quest_banner.js' in names
 js=z.read('assets/bf4200_demo_potion_command.js').decode('utf8')
 assert js.count('/* BF_GLOBAL_DEMO_POTION_COMMAND_V4200 */')==1
 assert len(js.encode('utf8'))<65536
 for forbidden in ('localStorage','saveProgress(', 'BFAndroid'):
  assert forbidden not in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
version=re.search(r"versionName '(\d+)\.00\.0-demo'",gradle)
assert version and int(version.group(1))>=42
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v42.00 packaged optional demo Potion, v7 save and development signature unchanged')