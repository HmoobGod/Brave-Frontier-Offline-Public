"""v77 packaged Gradual Recovery Light #20102 with signed offline Android save."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf7700_original_party_regen.js' in z.namelist()
 js=z.read('assets/bf7700_original_party_regen.js').decode('utf8')
 assert 'BF_GLOBAL_ORIGINAL_PARTY_REGEN_V7700' in js
 assert "itemId:20102" in js and "passiveSkillInfo:'800,1000,0,3,0'" in js
 assert "'party-regen-demo'" in z.read('assets/bf4500_item_turn_reservations.js').decode('utf8')
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
versions=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(versions)==1 and versions[0].split("'")[1].endswith('.00.0-demo')
assert int(versions[0].split("'")[1].split('.')[0])>=77
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v77 original group regeneration item identity and offline signed v7 package')
