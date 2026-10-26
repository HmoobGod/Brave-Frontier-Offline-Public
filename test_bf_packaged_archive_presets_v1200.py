"""v12.00 APK: stat-order controls and intact original save and signing."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for path in ('bf800_archive_draft.js','bf1000_original_evolution_paths.js',
  'bf900_optional_labs_hub.js','bf300_tactical_rounds.js'):
  assert 'assets/'+path in z.namelist(),path
 source=z.read('assets/bf800_archive_draft.js').decode('utf8')
 assert len(source.encode())<65536 and 'bf1200-presets' in source
 assert 'sortBy' in source and 'moveTo' in source
 assert 'localStorage' not in source and 'saveProgress(' not in source
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v12 Android archive presets, historical practice and save identity preserved')
