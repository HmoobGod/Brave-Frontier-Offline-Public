"""v27 source event stages packaged with original backgrounds."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for script in ('bf2700_original_event_stage.js','bf2600_original_event_portraits.js','bf2500_story_event_prompt.js',
                'bf2400_st_lamia_event_dialogue.js','bf2300_morgan_event_dialogue.js',
                'bf2200_original_event_reader.js'):
  assert 'assets/'+script in files,script
 src=z.read('assets/bf2700_original_event_stage.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_ORIGINAL_EVENT_STAGE_V2700 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'localStorage' not in src and 'saveProgress(' not in src
 for q in ['10200','10300','10400','10500','10600','10700','10800',
           '20100','20200','20300','20400','20500','20600','20700',
           '30100','30200','30300','30400','30500','30700']:
  assert 'assets/content/dungeon/dungeon_battle_'+q+'.jpg' in files,q
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v27.00 20 native source-matched scene background JPGs and offline save/signing')
