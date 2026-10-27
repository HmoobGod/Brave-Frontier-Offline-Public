"""v105 APK packages opt-in advanced Smart Auto without altering original save/signing."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 data=z.read('assets/bf10500_qol_advanced_smart_auto.js').decode('utf8')
 assert 'BF_GLOBAL_QOL_ADVANCED_SMART_AUTO_V10500' in data
 assert 'window.BF041SmartAuto=freeze({...smart,kindFor})' in data
 assert 'assets/bf10400_qol_evolution_needs.js' in z.namelist()
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10400_qol_evolution_needs.js")')<java.index('readPackagedText("bf10500_qol_advanced_smart_auto.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(105,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v105 packaged opt-in advanced Smart Auto, original v7 and Android signing')
