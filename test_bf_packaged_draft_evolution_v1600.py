"""v16.00 packaged temporary Global source evolution trial, offline save and signing."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for n in ('bf1600_draft_evolution.js','bf1500_evolution_chain.js',
  'bf1400_evolution_material_planner.js','bf1000_original_evolution_paths.js',
  'bf800_archive_draft.js','bf900_optional_labs_hub.js',
  'bf300_tactical_rounds.js','bf_global_unit_archive.js'):
  assert 'assets/'+n in names,n
 script=z.read('assets/bf1600_draft_evolution.js').decode('utf8')
 draft=z.read('assets/bf800_archive_draft.js').decode('utf8')
 assert script.count('/* BF_GLOBAL_ARCHIVE_DRAFT_EVOLUTION_V1600 */')==1
 assert len(script.encode('utf8'))<65536 and len(draft.encode('utf8'))<65536
 assert 'recipeRoute' in script and 'function evolve(' in script and 'function undo(' in script
 assert 'function replaceDraft' in draft
 assert 'localStorage' not in script and 'saveProgress(' not in script
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf1500_evolution_chain.js")')<java.index('readPackagedText("bf1600_draft_evolution.js")')
print('PASS v16.00 Android APK original source-only temporary evolution and v7 signing/save unchanged')
