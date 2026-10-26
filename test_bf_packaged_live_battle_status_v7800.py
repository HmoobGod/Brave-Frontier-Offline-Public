"""v78 packaged battle status display; no changed saved data or Android signer."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf7800_live_battle_status.js' in z.namelist()
 js=z.read('assets/bf7800_live_battle_status.js').decode('utf8')
 assert 'BF_GLOBAL_LIVE_BATTLE_STATUS_V7800' in js and len(js.encode('utf8'))<65536
 assert 'BFGlobalStatusNegationV7600' in js and 'BFGlobalOriginalPartyRegenV7700' in js
 assert 'host.prepend(panel)' in js and 'battle.prepend(panel)' not in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf7700_original_party_regen.js")')<java.index('readPackagedText("bf7800_live_battle_status.js")')
gradle=(R/'app/build.gradle').read_text('utf8')
versions=[x.strip() for x in gradle.splitlines() if x.strip().startswith('versionName ')]
assert len(versions)==1 and versions[0].split("'")[1].endswith('.00.0-demo')
assert int(versions[0].split("'")[1].split('.')[0])>=78
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v78 battle status HUD in signed offline APK, original item states, original save v7 preserved')
