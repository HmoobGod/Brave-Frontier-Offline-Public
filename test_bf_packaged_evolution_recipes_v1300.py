"""v13.00 APK: recovered evolution recipes displayed without spending materials."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as a:
 for file in ('bf1000_original_evolution_paths.js','bf800_archive_draft.js',
  'bf900_optional_labs_hub.js','bf300_tactical_rounds.js'):
  assert 'assets/'+file in a.namelist(),file
 js=a.read('assets/bf1000_original_evolution_paths.js').decode('utf8')
 assert len(js.encode('utf8'))<65536 and 'sourceRecipes' in js
 assert 'localStorage' not in js and 'saveProgress(' not in js
 assert 'bf_global_offline_demo_v7' in a.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v13 source evolution recipes packaged with existing Android signature and save')
