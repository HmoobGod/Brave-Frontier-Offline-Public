"""v72 source Potion and legacy demo coexist in signed offline APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 js=z.read('assets/bf4200_demo_potion_command.js').decode('utf8')
 turns=z.read('assets/bf4500_item_turn_reservations.js').decode('utf8')
 assert "passiveSkillInfo:'100,120,0,0'" in js
 assert 'useSourcePotion' in js and 'original-potion-demo' in js
 assert 'Math.min(500,p.maxHp-p.hp)' in js
 assert "'original-potion-demo'" in turns
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
versions=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(versions)==1
assert versions[0].split("'")[1].endswith('.00.0-demo')
assert int(versions[0].split("'")[1].split('.')[0])>=72
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v72 2022 Potion source healing and retained demo option, signed offline Android v7')
