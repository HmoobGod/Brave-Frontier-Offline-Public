"""v99 signed APK ships opt-in animation speed UI, stable v7/Android identity."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    data=z.read('assets/bf9900_qol_battle_speed.js').decode('utf8')
    assert 'BF_GLOBAL_QOL_BATTLE_SPEED_V9900' in data
    assert 'window.wait=function(ms)' in data
    assert 'nativeWait.call(this,40)' in data
    assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
    assert 'assets/bf9800_qol_cleared_quest_repeat.js' in z.namelist()
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf9800_qol_cleared_quest_repeat.js")')<java.index('readPackagedText("bf9900_qol_battle_speed.js")')
gradle=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in gradle for v in range(99,200))
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert "bf-development-debug.keystore" in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v99 packaged optional battle speed and animation skip, identity/keys preserved')
