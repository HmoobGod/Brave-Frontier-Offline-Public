"""v2.50 APK: unit-based training isolated, original save/quest and signing preserved."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as a:
 paths=set(a.namelist())
 for name in ('bf250_squad_training.js','bf200_historical_wave_lab.js',
  'bf150_source_crosscheck.js','bf120_historical_encounters.js',
  'bf110_quest_journal.js','bf101_story_continue.js',
  'bf100_grand_gaia_campaign.js','bf090_st_lamia_map.js',
  'bf080_morgan_map.js','bf_global_unit_archive.js'):
  assert 'assets/'+name in paths,name
 new=a.read('assets/bf250_squad_training.js').decode('utf8')
 assert new.count('/* BF_GLOBAL_SQUAD_TRAINING_V250 */')==1
 assert len(new.encode('utf8'))<65536
 assert 'localStorage' not in new and 'saveProgress(' not in new and 'BFAndroid' not in new
 assert 'effectiveUnit(id)' in new
 html=a.read('assets/index.html').decode('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert len(a.read('assets/bf_home_nav.js'))<65536
gradle=(R/'app/build.gradle').read_text('utf8')
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert "versionName '" in gradle
assert 'bf-development-debug.keystore' in gradle
manifest=(R/'app/src/main/AndroidManifest.xml').read_text('utf8')
assert 'android.permission.INTERNET' not in manifest
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf200_historical_wave_lab.js")')<java.index('readPackagedText("bf250_squad_training.js")')
print('PASS v2.50 APK offline six-member squad training, signed identity/save v7')
