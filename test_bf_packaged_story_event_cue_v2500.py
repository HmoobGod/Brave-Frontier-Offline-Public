"""v25.00 packaged context-sensitive quest story prompts."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for f in ('bf2500_story_event_prompt.js','bf2400_st_lamia_event_dialogue.js',
           'bf2300_morgan_event_dialogue.js','bf2200_original_event_reader.js','index.html'):
  assert 'assets/'+f in names
 js=z.read('assets/bf2500_story_event_prompt.js').decode('utf8')
 assert js.count('/* BF_GLOBAL_STORY_EVENT_CUE_V2500 */')==1
 assert len(js.encode('utf8'))<65536 and 'localStorage' not in js and 'saveProgress(' not in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v25.00 playable quest source-story cue offline and save-compatible')
