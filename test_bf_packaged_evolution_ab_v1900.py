"""v19.00 signed Android APK contains matched simulated evolution A/B battles."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for f in ('bf1900_evolution_ab.js','bf1800_multistage_draft.js',
  'bf1700_batch_draft_evolution.js','bf1600_draft_evolution.js',
  'bf1500_evolution_chain.js','bf800_archive_draft.js',
  'bf300_tactical_rounds.js','bf_global_unit_archive.js'):
  assert 'assets/'+f in names,f
 src=z.read('assets/bf1900_evolution_ab.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_EVOLUTION_AB_TRIALS_V1900 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'function simulate(' in src and 'function run(' in src
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf1800_multistage_draft.js")')<java.index('readPackagedText("bf1900_evolution_ab.js")')
print('PASS v19.00 packaged A/B evolution combat remains offline and preserves v7 save and Android signing')
