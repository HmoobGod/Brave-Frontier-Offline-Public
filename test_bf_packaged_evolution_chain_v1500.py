"""v15.00 APK: strictly recorded offline evolution route planner."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as a:
 for file in ('bf1500_evolution_chain.js','bf1400_evolution_material_planner.js',
  'bf1000_original_evolution_paths.js','bf800_archive_draft.js',
  'bf900_optional_labs_hub.js','bf_global_unit_archive.js'):
  assert 'assets/'+file in a.namelist(),file
 script=a.read('assets/bf1500_evolution_chain.js').decode('utf8')
 assert len(script.encode('utf8'))<65536
 assert script.count('/* BF_GLOBAL_EVOLUTION_CHAIN_V1500 */')==1
 assert 'findRoute' in script and 'reachable' in script
 assert 'localStorage' not in script and 'saveProgress(' not in script
 assert 'bf_global_offline_demo_v7' in a.read('assets/index.html').decode('utf8')
build=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in build
assert "applicationId 'org.bravefrontier.offline'" in build
assert 'bf-development-debug.keystore' in build
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf1400_evolution_material_planner.js")')<java.index('readPackagedText("bf1500_evolution_chain.js")')
print('PASS v15 original archived evolution chain and unchanged offline Android package/save')
