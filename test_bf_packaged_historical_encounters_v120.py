"""APK v1.20: original 2014 historical source labels, unchanged save."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 js=z.read('assets/bf120_historical_encounters.js').decode('utf8')
 assert js.count('/* BF_HISTORICAL_GLOBAL_ENCOUNTERS_V120 */')==1
 assert '2014' in js and 'NOT confirmed' in js
 assert 'localStorage' not in js and 'saveProgress(' not in js
 assert 'assets/bf110_quest_journal.js' in names
 assert 'assets/bf101_story_continue.js' in names
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
 assert len(z.read('assets/bf_home_nav.js'))<65536
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf110_quest_journal.js")')<java.index('readPackagedText("bf120_historical_encounters.js")')
assert "versionName '" in (R/'app/build.gradle').read_text('utf8')
print('PASS v1.20 packaged historical research; save v7 maintained')
