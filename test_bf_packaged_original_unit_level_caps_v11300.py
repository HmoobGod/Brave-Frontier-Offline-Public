"""v113 signed APK: original 2022 Global max-level metadata, save-safe hooks."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
import json
R=Path(__file__).resolve().parent
manifest=json.loads((R/'source_data/bf_global_2022_playable_level_caps_v113.json').read_text('utf8'))
assert manifest['supportedForms']==72
asset='bf11300_original_unit_level_caps.js'
data=(R/'app/src/main/assets'/asset).read_bytes()
assert b'BF_GLOBAL_ORIGINAL_UNIT_LEVEL_CAPS_V11300' in data
assert b'demoExpThresholdsUnchanged:true' in data
assert b'saveFieldsAdded:0' in data
assert b'localStorage' not in data and b'saveProgress(' not in data
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 blob=z.read('assets/'+asset)
 assert sha256(blob).digest()==sha256(data).digest()
 assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
 assert b'function playerUnit(i){' in z.read('assets/index.html')
 assert sha256(z.read('assets/index.html')).digest()==sha256(
    (R/'app/src/main/assets/index.html').read_bytes()).digest()
main=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert main.index('readPackagedText("bf11200_all_playable_leader_source.js")')<main.index(
 'readPackagedText("bf11300_original_unit_level_caps.js")')
assert 'window.BFGlobalOriginalUnitLevelCapsV11300?.apply?.(unit,i)' in (
 R/'app/src/main/assets/bf11100_original_starter_leader_combat.js').read_text('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '113.00.0-demo'" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v113 signed Android APK original 72 max level caps, source byte match, original signing, v7 save')
