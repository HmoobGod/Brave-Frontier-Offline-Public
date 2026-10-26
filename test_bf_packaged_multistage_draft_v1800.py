"""v18.00 APK packages fully documented 2022 multi-stage draft batch without network."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
 names=set(apk.namelist())
 for file in ('bf1800_multistage_draft.js','bf1700_batch_draft_evolution.js',
  'bf1600_draft_evolution.js','bf1500_evolution_chain.js',
  'bf1400_evolution_material_planner.js','bf800_archive_draft.js',
  'bf300_tactical_rounds.js','bf_global_unit_archive.js'):
  assert 'assets/'+file in names,file
 s=apk.read('assets/bf1800_multistage_draft.js').decode('utf8')
 assert s.count('/* BF_GLOBAL_MULTISTAGE_DRAFT_BATCH_V1800 */')==1
 assert len(s.encode('utf8'))<65536
 assert 'function analyze(' in s and 'function apply(' in s and 'function undo(' in s
 assert 'localStorage' not in s and 'saveProgress(' not in s
 assert 'bf_global_offline_demo_v7' in apk.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf1700_batch_draft_evolution.js")')<java.index('readPackagedText("bf1800_multistage_draft.js")')
print('PASS v18.00 Android APK: source-verified multi-stage evolution batch; offline signing and saved v7 preserved')
