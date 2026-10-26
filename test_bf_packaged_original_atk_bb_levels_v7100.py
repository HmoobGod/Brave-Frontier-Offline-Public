"""v71 original source ATK BB skill levels in signed offline Android APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf7100_original_atk_bb_levels.js' in z.namelist()
 js=z.read('assets/bf7100_original_atk_bb_levels.js').decode('utf8')
 assert 'BF_GLOBAL_ORIGINAL_ATK_BB_LEVELS_V7100' in js and len(js.encode())<65536
 assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
 html=z.read('assets/index.html').decode('utf8')
 assert html.count('BFGlobalOriginalAtkBBLevelsV7100?.boostFor(p.unitId)')==1
 assert html.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
 assert 'bf_global_offline_demo_v7' in html
g=(R/'app/build.gradle').read_text('utf8')
versions=[line.strip() for line in g.splitlines() if line.strip().startswith('versionName ')]
assert len(versions)==1
version=versions[0].split("'")[1]
assert version.endswith('.00.0-demo') and int(version.split('.')[0])>=71
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v71 source ATK BB levels, signed offline APK, v7 saved progress identity')
