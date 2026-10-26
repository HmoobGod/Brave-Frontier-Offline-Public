"""v53 source all-ally DEF item is included with v7 saves and original signer."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 for name in ('bf4900_source_def_item.js','bf5200_source_double_def_item.js',
              'bf5300_source_party_def_item.js'):
  assert 'assets/'+name in z.namelist(),name
 js=z.read('assets/bf5300_source_party_def_item.js').decode('utf8')
 assert 'BF_GLOBAL_SOURCE_PARTY_DEF_ITEM_V5300' in js and len(js.encode('utf8'))<65536
 assert 'itemId:50600' in js and "passiveSkillInfo:'0,0,50,0,0,3'" in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf5200_source_double_def_item.js")') < j.index('readPackagedText("bf5300_source_party_def_item.js")')
g=(R/'app/build.gradle').read_text('utf8')
# Historical v53 contract: accept newer releases without dropping the 53 floor.
version_lines=[line.strip() for line in g.splitlines()
               if line.strip().startswith('versionName ')]
assert len(version_lines)==1
release=version_lines[0].split("'")[1]
assert release.endswith('.00.0-demo')
assert release.split('.')[0].isdigit() and int(release.split('.')[0])>=53
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v53 original party DEF item, stable signing, v7 save, offline package')
