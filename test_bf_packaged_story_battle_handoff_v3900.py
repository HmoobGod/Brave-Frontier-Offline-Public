"""v39.00 archived story to active demo battle handoff package safety."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for name in ('bf3900_story_battle_handoff.js','bf3800_source_battle_backdrop.js',
              'bf3700_cinematic_reader.js'):
  assert 'assets/'+name in files,name
 src=z.read('assets/bf3900_story_battle_handoff.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_STORY_TO_BATTLE_HANDOFF_V3900 */')==1
 assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v39.00 original source dialogue to live demo battle navigation bundled safely')
