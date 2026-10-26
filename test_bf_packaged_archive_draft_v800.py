"""v8.00 APK: optional archive draft evidence and saved-game compatibility."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
 for name in ('bf800_archive_draft.js','bf700_original_normal_hits.js',
  'bf500_source_bb_evidence.js','bf400_original_battle_dossier.js',
  'bf300_tactical_rounds.js','bf250_squad_training.js',
  'bf_global_unit_archive.js'):
  assert 'assets/'+name in apk.namelist(),name
 script=apk.read('assets/bf800_archive_draft.js').decode('utf8')
 trial=apk.read('assets/bf300_tactical_rounds.js').decode('utf8')
 assert script.count('/* BF_GLOBAL_ARCHIVE_DRAFT_V800 */')==1
 assert len(script.encode('utf8'))<65536 and len(trial.encode('utf8'))<65536
 assert 'startDraft' in script and 'canStartDraft' in trial
 assert 'localStorage' not in script+trial and 'saveProgress(' not in script+trial
 assert 'bf_global_offline_demo_v7' in apk.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf300_tactical_rounds.js")')<java.index('readPackagedText("bf800_archive_draft.js")')
print('PASS v8.00 signed offline APK supports temporary 2022 archived unit drafts without owning or saving them')
