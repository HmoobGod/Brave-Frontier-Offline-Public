"""v28.00 exact source speaker cues packaged, offline original Global event stage."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for f in ('bf2800_dialogue_speaker_cues.js','bf2700_original_event_stage.js',
           'bf2600_original_event_portraits.js','bf2500_story_event_prompt.js'):
  assert 'assets/'+f in files,f
 src=z.read('assets/bf2800_dialogue_speaker_cues.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_SOURCE_SPEAKER_CUES_V2800 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert all('assets/content/event/navi_chara'+str(i)+'_0.png' in files for i in (1,2,3))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf2700_original_event_stage.js")')<java.index('readPackagedText("bf2800_dialogue_speaker_cues.js")')
print('PASS v28.00 original 2022 event source speaker cues and existing offline identity')
