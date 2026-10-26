"""v68 signed Android APK preserves recorded BB levels and save identity."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf6800_original_heal_bb_levels.js' in z.namelist()
 js=z.read('assets/bf6800_original_heal_bb_levels.js').decode('utf8')
 assert 'BF_GLOBAL_ORIGINAL_HEAL_BB_LEVELS_V6800' in js and len(js.encode())<65536
 assert 'return Math.round(base)+30*(level-1)' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 rec=z.read('assets/bf6700_burst_recipient_rec.js').decode('utf8')
 assert 'window.BFGlobalOriginalHealBBLevelsV6800?.baseHeal(base)??base' in rec
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
v=[line.strip() for line in g.splitlines() if line.strip().startswith('versionName ')]
assert len(v)==1 and v[0].split("'")[1].endswith('.00.0-demo')
assert int(v[0].split("'")[1].split('.')[0])>=68
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v68 all original base healing BB levels in signed offline Android APK')
