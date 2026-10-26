"""v73 source Potion now targets an independently selected ally in signed APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 js=z.read('assets/bf4200_demo_potion_command.js').decode('utf8')
 assert 'function useSourcePotion(actorId,targetId=actorId)' in js
 assert "passiveSkillInfo:'100,120,0,0'" in js
 assert 'recipient.hp+=healed;' in js and 'caster.action=' in js
 assert "Math.min(500,p.maxHp-p.hp)" in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
lines=[s.strip() for s in g.splitlines() if s.strip().startswith('versionName ')]
assert len(lines)==1 and lines[0].split("'")[1].endswith('.00.0-demo')
assert int(lines[0].split("'")[1].split('.')[0])>=73
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v73 source one-ally Potion targeting, legacy option, saved identity, offline signer')