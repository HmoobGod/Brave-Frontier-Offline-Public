"""v43.00 signed APK contains source-indexed experimental party heal."""
from pathlib import Path
from zipfile import ZipFile
import re
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for p in ('bf4200_demo_potion_command.js','bf4300_source_party_heal.js'):
  assert 'assets/'+p in z.namelist()
 js=z.read('assets/bf4300_source_party_heal.js').decode('utf8')
 assert 'BF_GLOBAL_SOURCE_PARTY_HEAL_V4300' in js
 assert "passiveSkillInfo:'500,500,0,0'" in js
 assert 'archivedBaseHeal:500' in js
 assert '0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474' in js
 assert len(js.encode('utf8'))<65536
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
v=re.search(r"versionName '(\d+)\.00\.0-demo'",g)
assert v and int(v.group(1))>=43
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v43.00 packaged 2022 item party-scope prototype, unchanged offline identity and saves')