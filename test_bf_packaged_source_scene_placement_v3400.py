"""v34.00 source scene stage positions bundled without changing saves or Android identity."""
from pathlib import Path
import re
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for name in ('bf3400_source_scene_placement.js','bf3300_story_playback.js',
              'bf2900_original_event_expressions.js','bf2800_dialogue_speaker_cues.js'):
  assert 'assets/'+name in files,name
 src=z.read('assets/bf3400_source_scene_placement.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_SOURCE_SCENE_PLACEMENT_V3400 */')==1
 assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
version=re.search(r"versionName '(\d+)\.00\.0-demo'",g)
assert version and int(version.group(1))>=34, "v34 or newer Android version required"
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v34.00 archived event actor source positions bundled, v7 signing and offline preserved')
