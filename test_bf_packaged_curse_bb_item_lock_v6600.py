"""v66 offline APK preserves exact-source BB item with Curse charging prevention."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf4600_source_bb_gauge_item.js' in z.namelist()
 js=z.read('assets/bf4600_source_bb_gauge_item.js').decode('utf8')
 assert 'BFGlobalOriginalAilmentStateV5700?.codesFor(i).includes(5)' in js
 assert 'itemId:21000' in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
v=[line.strip() for line in g.splitlines() if line.strip().startswith('versionName ')]
assert len(v)==1 and v[0].split("'")[1].endswith('.00.0-demo')
assert int(v[0].split("'")[1].split('.')[0])>=66
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v66 source BB item respects Curse BB lock; APK signer/offline/save unchanged')
