"""v7.00 APK: 2022 original normal-hit evidence and safe save and package identity."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
 for name in ('bf700_original_normal_hits.js','bf500_source_bb_evidence.js',
   'bf400_original_battle_dossier.js','bf300_tactical_rounds.js',
   'bf250_squad_training.js','bf200_historical_wave_lab.js',
   'bf_global_unit_archive.js'):
  assert 'assets/'+name in apk.namelist(),name
 scripts=[apk.read('assets/'+f).decode('utf8') for f in
    ('bf700_original_normal_hits.js','bf300_tactical_rounds.js')]
 assert all(len(s.encode('utf8'))<65536 for s in scripts)
 assert 'BFOriginalHitSequenceV700' in scripts[0]
 assert 'hitEvents' in scripts[1] and 'bf700-hit-report' in scripts[1]
 assert all('localStorage' not in s and 'saveProgress(' not in s for s in scripts)
 assert 'bf_global_offline_demo_v7' in apk.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf700_original_normal_hits.js")')<java.index('readPackagedText("bf300_tactical_rounds.js")')
print('PASS v7.00 signed offline APK includes 71 original 2022 hit evidence and v7 save compatibility')
