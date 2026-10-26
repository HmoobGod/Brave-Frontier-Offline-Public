"""v1.01 APK integrity: additive 106-mission story continuation."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 script=z.read('assets/bf101_story_continue.js').decode('utf-8')
 assert script.count('/* BF_GRAND_GAIA_CONTINUE_V101 */')==1
 assert 'QUESTS.length!==106' in script and 'questUnlocked(q)' in script
 assert 'CONTINUE STORY' in script
 assert 'localStorage' not in script and 'saveProgress(' not in script
 for name in ('bf100_grand_gaia_campaign.js','bf090_st_lamia_map.js','bf080_morgan_map.js'):
  assert 'assets/'+name in files
 assert len(z.read('assets/bf_home_nav.js'))<65536
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf-8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
assert java.index('readPackagedText("bf100_grand_gaia_campaign.js")')<java.index('readPackagedText("bf101_story_continue.js")')
assert "versionName '" in (R/'app/build.gradle').read_text('utf-8')
print('PASS v1.01 packaged three-region Continue Story, existing save v7')
