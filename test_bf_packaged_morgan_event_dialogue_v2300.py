"""v23.00 packaged original Morgan story and unchanged offline save."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for n in ('bf2300_morgan_event_dialogue.js','bf2200_original_event_reader.js',
    'bf2100_battle_command_tray.js','index.html'):
  assert 'assets/'+n in names
 source=z.read('assets/bf2300_morgan_event_dialogue.js').decode('utf8')
 assert source.count('/* BF_GLOBAL_2022_MORGAN_EVENT_DIALOGUE_V2300 */')==1
 assert len(source.encode('utf8'))<65536
 assert 'localStorage' not in source and 'saveProgress(' not in source
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v23.00 original Morgan dialogue packaged, offline save and signing configuration')
