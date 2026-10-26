"""v37.00 original mobile story theater packaged safely in signed offline APK."""
from pathlib import Path
import re
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for name in ('bf3700_cinematic_reader.js','bf3600_event_composite.js',
              'bf3500_dialogue_timeline.js'):
  assert 'assets/'+name in files,name
 src=z.read('assets/bf3700_cinematic_reader.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_OPTIONAL_CINEMATIC_STORY_READER_V3700 */')==1
 assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
version=re.search(r"versionName '(\d+)\.00\.0-demo'",g)
assert version and int(version.group(1))>=37
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v37.00 original 2022 source cinematic reading mode packaged and save-safe')
