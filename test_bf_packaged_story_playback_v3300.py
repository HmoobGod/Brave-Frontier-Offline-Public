"""v33.00 original offline story playback APK validates source-linked scene layers."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for name in ('bf3300_story_playback.js','bf3200_combat_journal.js','bf3100_battle_focus.js',
              'bf2900_original_event_expressions.js','bf2700_original_event_stage.js'):
  assert 'assets/'+name in files,name
 src=z.read('assets/bf3300_story_playback.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_ORIGINAL_SCENE_PLAYBACK_V3300 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v33.00 original story player uses original in-app controls and existing offline ID')
