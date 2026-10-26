"""v36.00 composite event scene bundled; save identity, signing and offline intact."""
from pathlib import Path
import re
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for name in ('bf3600_event_composite.js','bf3500_dialogue_timeline.js',
              'bf3400_source_scene_placement.js','bf2900_original_event_expressions.js'):
  assert 'assets/'+name in files,name
 src=z.read('assets/bf3600_event_composite.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_ORIGINAL_EVENT_COMPOSITE_STAGE_V3600 */')==1
 assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
version=re.search(r"versionName '(\d+)\.00\.0-demo'",g)
assert version and int(version.group(1))>=36
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v36.00 composite source story actor art bundled; offline save v7')
