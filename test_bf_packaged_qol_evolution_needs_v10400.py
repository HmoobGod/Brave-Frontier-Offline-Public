"""v104 APK packages owned-unit evolution material comparison and stable Android identity."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 data=z.read('assets/bf10400_qol_evolution_needs.js').decode('utf8')
 assert 'BF_GLOBAL_QOL_EVOLUTION_NEEDS_V10400' in data
 assert 'evo.sourceRecipes(current.id)' in data
 assert 'assets/bf10300_qol_battle_details.js' in z.namelist()
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10300_qol_battle_details.js")')<java.index('readPackagedText("bf10400_qol_evolution_needs.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '104.00.0-demo'" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v104 packaged source evolution needs, stable v7/Android signing')
