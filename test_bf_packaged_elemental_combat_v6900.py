"""v69 source-aware element combat preserved in signed offline Android APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf6900_elemental_combat.js' in z.namelist()
 js=z.read('assets/bf6900_elemental_combat.js').decode('utf8')
 assert 'BF_GLOBAL_ELEMENTAL_COMBAT_V6900' in js
 assert 'Fire:' in js and 'Light:' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 html=z.read('assets/index.html').decode('utf8')
 assert html.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
 assert html.count('BFGlobalBurstRecipientRecoveryV6700?.healAmount(base,ally)')==1
 assert 'bf_global_offline_demo_v7' in html
g=(R/'app/build.gradle').read_text('utf8')
v=[line.strip() for line in g.splitlines() if line.strip().startswith('versionName ')]
assert len(v)==1 and v[0].split("'")[1].endswith('.00.0-demo')
assert int(v[0].split("'")[1].split('.')[0])>=69
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v69 source-aware elemental scaling packaged, immutable signer and offline/v7 save identity')
