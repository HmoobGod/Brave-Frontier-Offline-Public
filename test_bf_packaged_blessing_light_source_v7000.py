"""v70 signed APK contains fixed original Blessing Light 500 base."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 js=z.read('assets/bf4300_source_party_heal.js').decode('utf8')
 assert "passiveSkillInfo:'500,500,0,0'" in js and 'archivedBaseHeal:500' in js
 assert 'Math.min(source.archivedBaseHeal,p.maxHp-p.hp)' in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
v=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(v)==1 and v[0].split("'")[1].endswith('.00.0-demo')
assert int(v[0].split("'")[1].split('.')[0])>=70
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v70 source-payload Blessing Light correction and offline signed v7 APK')
