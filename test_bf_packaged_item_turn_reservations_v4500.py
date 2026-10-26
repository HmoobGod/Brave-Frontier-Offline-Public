"""v45 Android package remains offline, signed, and save-compatible."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
names=('bf4200_demo_potion_command.js','bf4300_source_party_heal.js',
       'bf4400_source_atk_item.js','bf4500_item_turn_reservations.js')
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in names: assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf4500_item_turn_reservations.js').decode('utf8')
 assert 'BF_GLOBAL_ITEM_TURN_RESERVATIONS_V4500' in js
 assert len(js.encode('utf8'))<65536
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
order=['bf4500_item_turn_reservations.js',*names[:3]]
assert all(j.index('readPackagedText("'+a+'")')<j.index('readPackagedText("'+b+'")')
           for a,b in zip(order,order[1:]))
g=(R/'app/build.gradle').read_text('utf8')
# Historical v45 package gates accept newer releases; the current release's
# package test pins its own exact versionName.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=45
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v45: packaged item locks, offline package, development signer, v7 key')
