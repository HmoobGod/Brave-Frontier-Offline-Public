"""v24.00 verified original St Lamia dialogue packaged."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for f in ('bf2400_st_lamia_event_dialogue.js','bf2300_morgan_event_dialogue.js',
           'bf2200_original_event_reader.js','index.html'):
  assert 'assets/'+f in files
 js=z.read('assets/bf2400_st_lamia_event_dialogue.js').decode('utf8')
 assert js.count('/* BF_GLOBAL_2022_ST_LAMIA_EVENT_DIALOGUE_V2400 */')==1
 assert len(js.encode('utf8'))<65536
 assert 'localStorage' not in js and 'saveProgress(' not in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v24.00 St Lamia reader packed and original APK identity retained')
