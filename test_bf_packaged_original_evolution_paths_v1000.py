"""v10.00 offline APK retains all previous labs and original evolution source viewer."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as a:
 for name in ('bf1000_original_evolution_paths.js','bf900_optional_labs_hub.js',
    'bf800_archive_draft.js','bf700_original_normal_hits.js',
    'bf500_source_bb_evidence.js','bf400_original_battle_dossier.js',
    'bf300_tactical_rounds.js','bf250_squad_training.js',
    'bf_global_unit_archive.js'):
  assert 'assets/'+name in a.namelist(),name
 script=a.read('assets/bf1000_original_evolution_paths.js').decode('utf8')
 assert script.count('/* BF_GLOBAL_ORIGINAL_EVOLUTION_PATHS_V1000 */')==1
 assert len(script.encode('utf8'))<65536
 assert 'localStorage' not in script and 'saveProgress(' not in script
 assert 'bf_global_offline_demo_v7' in a.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf900_optional_labs_hub.js")')<java.index('readPackagedText("bf1000_original_evolution_paths.js")')
print('PASS v10.00 original evolution graph APK, source-only progress and native signing/save compatibility')
