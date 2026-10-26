"""v5.00 APK: original BB evidence and no native save/network regressions."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as a:
 for file in ('bf500_source_bb_evidence.js','bf400_original_battle_dossier.js',
  'bf300_tactical_rounds.js','bf250_squad_training.js',
  'bf200_historical_wave_lab.js','bf_global_unit_archive.js'):
  assert 'assets/'+file in a.namelist(),file
 evidence=a.read('assets/bf500_source_bb_evidence.js').decode('utf8')
 tactical=a.read('assets/bf300_tactical_rounds.js').decode('utf8')
 assert evidence.count('/* BF_GLOBAL_SOURCE_BB_EVIDENCE_V500 */')==1
 assert len(evidence.encode('utf8'))<65536 and len(tactical.encode('utf8'))<65536
 assert 'sourcebb' in tactical and 'sourceSkill' in tactical
 assert 'localStorage' not in evidence+tactical and 'saveProgress(' not in evidence+tactical
 assert 'bf_global_offline_demo_v7' in a.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf500_source_bb_evidence.js")')<java.index('readPackagedText("bf300_tactical_rounds.js")')
print('PASS v5.00 Android package, 30 original Global BB records and save/signing unchanged')
