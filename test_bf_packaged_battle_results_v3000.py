"""v30.00 APK battle-result actions and original archive scripts carried intact."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assets=set(z.namelist())
 for f in ('bf3000_battle_results.js','bf2900_original_event_expressions.js',
           'bf2800_dialogue_speaker_cues.js','bf2700_original_event_stage.js',
           'bf2600_original_event_portraits.js','bf2500_story_event_prompt.js'):
  assert 'assets/'+f in assets,f
 src=z.read('assets/bf3000_battle_results.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_DEMO_BATTLE_RESULTS_V3000 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf2900_original_event_expressions.js")')<java.index('readPackagedText("bf3000_battle_results.js")')
print('PASS v30.00 playable results buttons packed, save version and offline/signing preserved')
