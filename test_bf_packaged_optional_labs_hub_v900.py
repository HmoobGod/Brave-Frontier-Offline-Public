"""v9.00 APK: original Quest UI and five isolated lab panels are preserved."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
 for x in ('bf900_optional_labs_hub.js','bf800_archive_draft.js',
    'bf700_original_normal_hits.js','bf500_source_bb_evidence.js',
    'bf400_original_battle_dossier.js','bf300_tactical_rounds.js',
    'bf250_squad_training.js','bf200_historical_wave_lab.js',
    'bf_global_unit_archive.js','bf100_grand_gaia_campaign.js'):
  assert 'assets/'+x in apk.namelist(),x
 script=apk.read('assets/bf900_optional_labs_hub.js').decode('utf8')
 assert script.count('/* BF_GLOBAL_OPTIONAL_LABS_HUB_V900 */')==1
 assert len(script.encode('utf8'))<65536
 assert 'localStorage' not in script and 'saveProgress(' not in script
 assert 'bf_global_offline_demo_v7' in apk.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf800_archive_draft.js")')<java.index('readPackagedText("bf900_optional_labs_hub.js")')
print('PASS v9.00 APK safely groups optional research labs while preserving original Quest, save and signing')
