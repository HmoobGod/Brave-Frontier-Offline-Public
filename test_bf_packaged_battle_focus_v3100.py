"""v31.00 Android APK includes safe tactical focus and preserves existing offline state."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for name in ('bf3100_battle_focus.js','bf3000_battle_results.js',
              'bf2100_battle_command_tray.js','bf2900_original_event_expressions.js'):
  assert 'assets/'+name in files,name
 src=z.read('assets/bf3100_battle_focus.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_PLAYABLE_FOCUS_ACTIONS_V3100 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf3000_battle_results.js")')<j.index('readPackagedText("bf3100_battle_focus.js")')
print('PASS v31.00 targeting through existing demo combat controls with intact offline identity')
