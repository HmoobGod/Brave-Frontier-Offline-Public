"""v97 packaged Android APK includes isolated backup UI and no signing/save changes."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    src=z.read('assets/bf9700_qol_rotating_backups.js').decode('utf8')
    assert 'BF_GLOBAL_QOL_ROTATING_BACKUPS_V9700' in src
    assert 'bf_global_offline_qol_rotating_backups_v97' in src
    assert 'window.BFAndroid?.exportSaveFile' in src
    assert "localStorage.setItem(liveKey" not in src
    assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'readPackagedText("bf9700_qol_rotating_backups.js")' in java
gradle=(R/'app/build.gradle').read_text('utf8')
manifest=(R/'app/src/main/AndroidManifest.xml').read_text('utf8')
assert "versionName '97.00.0-demo'" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert "bf-development-debug.keystore" in gradle
assert "android.permission.INTERNET" not in manifest
print('PASS v97 packaged rotating backups, unchanged package/signing configuration and v7 key')
