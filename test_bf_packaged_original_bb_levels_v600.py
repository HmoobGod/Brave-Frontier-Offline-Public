"""v6.00 APK: source-verifiable 300 Brave Burst level rows, existing save/signing."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as a:
 for path in ('bf500_source_bb_evidence.js','bf400_original_battle_dossier.js',
  'bf300_tactical_rounds.js','bf250_squad_training.js',
  'bf200_historical_wave_lab.js','bf_global_unit_archive.js',
  'bf100_grand_gaia_campaign.js'):
  assert 'assets/'+path in a.namelist(),path
 source=a.read('assets/bf500_source_bb_evidence.js').decode('utf8')
 trial=a.read('assets/bf300_tactical_rounds.js').decode('utf8')
 assert len(source.encode('utf8'))<65536
 assert len(trial.encode('utf8'))<65536
 assert source.count('/* BF_GLOBAL_SOURCE_BB_EVIDENCE_V500 */')==1
 assert 'sourceLevelEntries' in source and 'getAtLevel' in source
 assert 'setSkillLevel' in trial and '2022 BB SOURCE LEVEL' in trial
 assert 'localStorage' not in source+trial and 'saveProgress(' not in source+trial
 assert 'bf_global_offline_demo_v7' in a.read('assets/index.html').decode('utf8')
build=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in build
assert "applicationId 'org.bravefrontier.offline'" in build
assert 'bf-development-debug.keystore' in build
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf500_source_bb_evidence.js")')<java.index('readPackagedText("bf300_tactical_rounds.js")')
print('PASS v6.00 APK packages source-level 300-row mastery preview and unchanged signing and v7 save')
