"""v11 APK includes formation controls and preserves signing and save v7."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for n in ('bf800_archive_draft.js','bf1000_original_evolution_paths.js',
  'bf900_optional_labs_hub.js','bf300_tactical_rounds.js'):
  assert 'assets/'+n in z.namelist(),n
 js=z.read('assets/bf800_archive_draft.js').decode('utf8')
 assert 'moveTo' in js and 'bf1100-order' in js and len(js.encode())<65536
 assert 'localStorage' not in js and 'saveProgress(' not in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g and "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v11 signed offline APK and archive formation UI')
