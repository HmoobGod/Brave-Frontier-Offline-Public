"""v59 curse-BB source effect safely packaged with v57-v58 status modules."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf5700_original_ailment_state.js','bf5800_poison_turn.js','bf5900_curse_bb_lock.js'):
  assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf5900_curse_bb_lock.js').decode('utf8')
 assert 'BF_GLOBAL_CURSE_BB_LOCK_V5900' in js and len(js.encode('utf8'))<65536
 assert 'preventGaugeGain' in js and 'blockBurst' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf5800_poison_turn.js")')<j.index('readPackagedText("bf5900_curse_bb_lock.js")')
g=(R/'app/build.gradle').read_text('utf8')
# Historical v59 package gate must remain valid for later releases.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=59
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v59 curse BB lock and unchanged offline signed Android v7 identity')
