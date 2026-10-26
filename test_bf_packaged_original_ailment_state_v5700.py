"""v57 original status identity registry bundled without saved inventory changes."""
from pathlib import Path
from zipfile import ZipFile
import json
R=Path(__file__).resolve().parent
e=json.loads((R/'source_data/bf_global_2022_status_cure_evidence_v5700.json').read_text('utf8'))
assert len(e['ailments'])==6 and len(e['cures'])==5
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf5700_original_ailment_state.js' in z.namelist()
 js=z.read('assets/bf5700_original_ailment_state.js').decode('utf8')
 assert 'BF_GLOBAL_ORIGINAL_AILMENT_STATE_V5700' in js
 assert len(js.encode('utf8'))<65536
 assert 'itemId:50200' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf5600_source_life_potion.js")')<j.index('readPackagedText("bf5700_original_ailment_state.js")')
g=(R/'app/build.gradle').read_text('utf8')
# Inherited v57 verification tolerates newer demo versions, while the
# newest release gate checks the exact versionName.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=57
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v57 source cure scopes, stable offline APK, stable signer and v7 saves')
