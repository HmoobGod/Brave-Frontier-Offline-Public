"""v2.00 signed offline APK: isolated historical research, source and v7 intact."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for name in ('bf200_historical_wave_lab.js','bf150_source_crosscheck.js',
  'bf120_historical_encounters.js','bf110_quest_journal.js',
  'bf101_story_continue.js','bf100_grand_gaia_campaign.js',
  'bf090_st_lamia_map.js','bf080_morgan_map.js','bf_global_unit_archive.js'):
  assert 'assets/'+name in names,name
 js=z.read('assets/bf200_historical_wave_lab.js').decode('utf8')
 assert len(js.encode('utf8'))<65536
 assert js.count('/* BF_GLOBAL_ARCHIVE_TRIALS_V200 */')==1
 assert '/* BF200_DATA_READY */' in js and 'BF200_DATA_PLACEHOLDER' not in js
 assert 'localStorage' not in js and 'saveProgress(' not in js and 'BFAndroid' not in js
 html=z.read('assets/index.html').decode('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert 'id="bf-global-unit-catalog-data"' in html
 assert len(z.read('assets/bf_home_nav.js'))<65536
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
manifest=(R/'app/src/main/AndroidManifest.xml').read_text('utf8')
assert 'android.permission.INTERNET' not in manifest
assert 'usesCleartextTraffic="false"' in manifest
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf150_source_crosscheck.js")')<java.index('readPackagedText("bf200_historical_wave_lab.js")')
print('PASS v2.00 bundled historical trial, no internet, original package/signing/v7 save')
