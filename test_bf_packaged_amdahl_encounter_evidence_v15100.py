"""v151 signed Android APK preserves v7 and packages source-only Amdahl ledger."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
asset='bf15100_amdahl_encounter_evidence.js'
src=(R/'app/src/main/assets'/asset).read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    assert z.read('assets/'+asset)==src
    assert b'BF_GLOBAL_2022_AMDAHL_ENCOUNTER_EVIDENCE_V15100' in src
    assert b'archivedMissions:142' in src
    assert b'meaningDecoded:false' in src
    assert b'gameplayMutation:false,saveMutation:false' in src
    assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'readPackagedText("bf15100_amdahl_encounter_evidence.js")' in java
gradle=(R/'app/build.gradle').read_text('utf8')
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v151 signed APK has exact source-only 142-mission ledger, no Android/save identity changes')
