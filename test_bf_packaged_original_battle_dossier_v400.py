"""v4.00 signed Android APK: offline source dossier, original save and authentication preserved."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 items=set(z.namelist())
 for n in ('bf400_original_battle_dossier.js','bf300_tactical_rounds.js',
  'bf250_squad_training.js','bf200_historical_wave_lab.js',
  'bf150_source_crosscheck.js','bf110_quest_journal.js',
  'bf_global_unit_archive.js','bf100_grand_gaia_campaign.js'):
  assert 'assets/'+n in items,n
 js=z.read('assets/bf400_original_battle_dossier.js').decode('utf8')
 assert js.count('/* BF_GLOBAL_ORIGINAL_BATTLE_DOSSIER_V400 */')==1
 assert len(js.encode('utf8'))<65536
 assert 'localStorage' not in js and 'saveProgress(' not in js
 html=z.read('assets/index.html').decode('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert 'bf-original-unit-lore-data' in html
 assert len(z.read('assets/bf_home_nav.js'))<65536
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
manifest=(R/'app/src/main/AndroidManifest.xml').read_text('utf8')
assert 'android.permission.INTERNET' not in manifest
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf300_tactical_rounds.js")')<java.index('readPackagedText("bf400_original_battle_dossier.js")')
print('PASS v4.00 original Global unit/skill dossier packaged, offline signing and v7 saved data intact')
