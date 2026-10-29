"""v174 signed APK: read-only original 2022 encounter/backdrop crossrefs."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
file=A/'bf17400_original_2022_encounter_crossrefs.js'
asset=file.read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
 assert apk.read('assets/'+file.name)==asset
 html=apk.read('assets/index.html')
 assert b'bf_global_offline_demo_v7' in html
 assert b'BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300' in html
 assert b'_bfGemV160' in html
 assert b'_bfGemV170Custom' in html
assert asset.count(b'BF_GLOBAL_ORIGINAL_2022_ENCOUNTER_CROSSREFS_V17400')==1
assert b'nativeWavesDecoded:false' in asset
assert b'nativeAIDecoded:false' in asset
assert b'firstRefBackgroundMatches:133' in asset
assert b'playable:106,amdahlReadOnly:36' in asset
assert len(asset)<65536
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf15100_amdahl_encounter_evidence.js")')<java.index(
 'readPackagedText("bf17400_original_2022_encounter_crossrefs.js")')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '174.00.0-demo'" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v174 signed APK: exact 2022 evidence asset, v7 save and signing unchanged')
