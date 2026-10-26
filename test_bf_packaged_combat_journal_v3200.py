"""v32.00 signed Android APK preserves all playable controls and in-session combat log."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for name in ('bf3200_combat_journal.js','bf3100_battle_focus.js',
              'bf3000_battle_results.js','bf2900_original_event_expressions.js'):
  assert 'assets/'+name in files,name
 src=z.read('assets/bf3200_combat_journal.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_PLAYABLE_COMBAT_JOURNAL_V3200 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf3100_battle_focus.js")')<j.index('readPackagedText("bf3200_combat_journal.js")')
print('PASS v32.00 session-only combat journal packaged and offline/save unchanged')
