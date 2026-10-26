"""v74 signed offline APK original fixed 1000/2000 ally healing."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ['bf7400_original_strong_potions.js','bf4200_demo_potion_command.js']:
  assert 'assets/'+name in z.namelist()
 js=z.read('assets/bf7400_original_strong_potions.js').decode('utf8')
 assert 'BF_GLOBAL_ORIGINAL_STRONG_POTIONS_V7400' in js
 assert "passiveSkillInfo:'1000,1000,0,0'" in js and "passiveSkillInfo:'2000,2000,0,0'" in js
 assert "turns.reserve(actorId,'strong-potion-demo')" in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
versions=[l.strip() for l in g.splitlines() if l.strip().startswith('versionName ')]
assert len(versions)==1 and versions[0].split("'")[1].endswith('.00.0-demo')
assert int(versions[0].split("'")[1].split('.')[0])>=74
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v74 source exact fixed recovery #20001/#20002, Android offline signer/save identity')
