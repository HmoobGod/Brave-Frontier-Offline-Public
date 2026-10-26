"""v101 APK contains read-only viewed-dialogue module and stable package."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 data=z.read('assets/bf10100_qol_viewed_dialogue.js').decode('utf8')
 assert 'BF_GLOBAL_QOL_VIEWED_DIALOGUE_SKIP_V10100' in data
 assert 'timeline.jump(s.lines)' in data
 assert 'assets/bf10000_qol_squad_presets.js' in z.namelist()
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10000_qol_squad_presets.js")')<java.index('readPackagedText("bf10100_qol_viewed_dialogue.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(101,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v101 packaged original dialogue quick-skip, signing and v7 unchanged')
