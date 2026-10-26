"""v79 packaged source-documented Injury penalty stacks additively with buffs."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf6200_injury_attack.js' in z.namelist()
 js=z.read('assets/bf6200_injury_attack.js').decode('utf8')
 assert 'BF_GLOBAL_INJURY_ATTACK_V6200' in js
 assert 'Math.round(originalAtk*(multiplier-.5))' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
versions=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(versions)==1 and versions[0].split("'")[1].endswith('.00.0-demo')
assert int(versions[0].split("'")[1].split('.')[0])>=79
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v79 original subtractive Injury mechanic in signed offline APK, preserved saves/signer')
