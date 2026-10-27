"""v110 APK contains authentic 2022 starter leader records, no live buff hooks."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 name='assets/bf11000_source_starter_leader_skills.js'
 assert name in z.namelist()
 js=z.read(name).decode('utf8')
 assert 'BF_GLOBAL_2022_STARTER_LEADER_SKILL_SOURCE_V11000' in js
 assert 'nativeBattleStatsModified:false' in js
 assert 'byUnit.size!==30' in js
 assert 'saveProgress(' not in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10900_stlamia_encounter_refs.js")')<java.index('readPackagedText("bf11000_source_starter_leader_skills.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '110.00.0-demo'" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v110 packaged 2022 starter leader source, native v7 save and signing identity')
