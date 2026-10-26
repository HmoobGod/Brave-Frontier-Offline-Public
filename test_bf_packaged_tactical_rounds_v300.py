"""v3.00 APK: all historical research kept and coordinated tactical rounds packaged."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 paths=set(z.namelist())
 for name in ('bf300_tactical_rounds.js','bf250_squad_training.js',
   'bf200_historical_wave_lab.js','bf150_source_crosscheck.js',
   'bf120_historical_encounters.js','bf110_quest_journal.js',
   'bf101_story_continue.js','bf100_grand_gaia_campaign.js',
   'bf090_st_lamia_map.js','bf080_morgan_map.js','bf_global_unit_archive.js'):
  assert 'assets/'+name in paths,name
 script=z.read('assets/bf300_tactical_rounds.js').decode('utf8')
 assert script.count('/* BF_GLOBAL_TACTICAL_ROUNDS_V300 */')==1
 assert len(script.encode('utf8'))<65536
 assert 'localStorage' not in script and 'saveProgress(' not in script
 assert 'stepRound' in script and 'autoPlan' in script
 html=z.read('assets/index.html').decode('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert len(z.read('assets/bf_home_nav.js'))<65536
build=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in build
assert "applicationId 'org.bravefrontier.offline'" in build
assert 'bf-development-debug.keystore' in build
manifest=(R/'app/src/main/AndroidManifest.xml').read_text('utf8')
assert 'android.permission.INTERNET' not in manifest
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf250_squad_training.js")')<java.index('readPackagedText("bf300_tactical_rounds.js")')
print('PASS v3.00 packaged source-backed tactical trials, no network and existing signing and save v7')
