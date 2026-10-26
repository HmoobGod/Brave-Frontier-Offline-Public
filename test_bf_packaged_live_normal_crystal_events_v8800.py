"""v88 signed Android package and source event hooks remain offline and save compatible."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=z.namelist()
 assert 'assets/bf8800_live_normal_crystal_events.js' in names
 js=z.read('assets/bf8800_live_normal_crystal_events.js').decode('utf8')
 assert js.count('BF_GLOBAL_LIVE_NORMAL_CRYSTAL_EVENTS_V8800')==1
 assert 'source.rollNormal(unitId,{overkill:false,random:Math.random})' in js
 assert len(js.encode('utf8'))<65536
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid', 'fetch('))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8400_original_normal_crystal_checks.js")')<java.index('readPackagedText("bf8800_live_normal_crystal_events.js")')
g=(R/'app/build.gradle').read_text('utf8')
v=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(v)==1 and int(v[0].split("'")[1].split('.')[0])>=88
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v88 source-backed live normal BC/HC event module in signed offline APK, original save identity')
