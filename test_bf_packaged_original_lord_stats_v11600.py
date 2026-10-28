"""v116 packaged APK includes authentic 72-form Lord stat reference without battle mutations."""
from pathlib import Path
import json,hashlib
from zipfile import ZipFile
R=Path(__file__).resolve().parent
assets=R/'app/src/main/assets'
manifest=json.loads((R/'source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json').read_text('utf8'))
assert manifest['unitCount']==72 and manifest['rawUnitTypeCount']==6
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf11600_original_lord_stats_data.js',
              'bf11600_original_lord_stats_reference.js'):
  actual=z.read('assets/'+name)
  expected=(assets/name).read_bytes()
  assert hashlib.sha256(actual).digest()==hashlib.sha256(expected).digest()
  assert b'localStorage' not in actual and b'saveProgress(' not in actual
 assert b'BF_GLOBAL_2022_LORD_STATS_DATA_V11600' in z.read('assets/bf11600_original_lord_stats_data.js')
 assert b'BF_GLOBAL_2022_LORD_STATS_REFERENCE_V11600' in z.read('assets/bf11600_original_lord_stats_reference.js')
 assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
 assert hashlib.sha256(z.read('assets/index.html')).digest()==hashlib.sha256((assets/'index.html').read_bytes()).digest()
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11500_original_unit_level_caps.js")')<java.index(
 'readPackagedText("bf11600_original_lord_stats_data.js")')<java.index(
 'readPackagedText("bf11600_original_lord_stats_reference.js")')
g=(R/'app/build.gradle').read_text('utf8')
# v116 source proof survives later verified APK version labels.
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(116,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v116 signed APK original unit stat endpoints, source-byte match, offline signing identity, v7 save')
