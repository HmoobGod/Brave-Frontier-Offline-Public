"""v81 packaged original crystal drop core, isolated from live demo rewards."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf8100_original_crystal_drop_core.js' in z.namelist()
 assert 'assets/bf700_original_normal_hits.js' in z.namelist()
 js=z.read('assets/bf8100_original_crystal_drop_core.js').decode('utf8')
 assert 'BF_GLOBAL_ORIGINAL_CRYSTAL_DROP_CORE_V8100' in js
 assert 'bcBasePercent:35' in js and 'hcBasePercent:10' in js
 # v81 did not know normal attack BC checks; v82 recovered exact F_UNIT
 # dropCheckCount for supported forms. Preserve both fail-closed contracts.
 assert js.count('BF_GLOBAL_ORIGINAL_CRYSTAL_DROP_CORE_V8100')==1
 assert 'unknownBattleCrystalChecks:true' in js or (
  'unknownBattleCrystalChecks:!window.BFGlobalNormalCrystalChecksV8200?.lookup(unitId)' in js
  and 'expectedBattleCrystals:window.BFGlobalNormalCrystalChecksV8200?.lookup(unitId)?.expectedBattleCrystals??null' in js)
 if 'assets/bf8200_original_normal_crystal_checks.js' in z.namelist():
  assert 'unknownBattleCrystalChecks:!window.BFGlobalNormalCrystalChecksV8200?.lookup(unitId)' in js
  assert 'expectedBattleCrystals:window.BFGlobalNormalCrystalChecksV8200?.lookup(unitId)?.expectedBattleCrystals??null' in js
 else:
  assert 'unknownBattleCrystalChecks:true' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf700_original_normal_hits.js")')<java.index('readPackagedText("bf8100_original_crystal_drop_core.js")')
g=(R/'app/build.gradle').read_text('utf8')
versions=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(versions)==1 and versions[0].split("'")[1].endswith('.00.0-demo')
assert int(versions[0].split("'")[1].split('.')[0])>=81
if int(versions[0].split("'")[1].split('.')[0])>=82:
 with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
  assert 'assets/bf8200_original_normal_crystal_checks.js' in z.namelist()
  bundled=z.read('assets/bf8100_original_crystal_drop_core.js').decode('utf8')
  assert 'unknownBattleCrystalChecks:!window.BFGlobalNormalCrystalChecksV8200?.lookup(unitId)' in bundled
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v81 original crystal drop calculation core is APK-bundled, offline and save compatible')
