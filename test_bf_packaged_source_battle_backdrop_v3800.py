"""v38.00 original source backdrop packaged with preserved identity."""
from pathlib import Path
import re
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for name in ('bf3800_source_battle_backdrop.js','bf3700_cinematic_reader.js'):
  assert 'assets/'+name in files,name
 assert 'assets/content/dungeon/dungeon_battle_10200.jpg' in files
 src=z.read('assets/bf3800_source_battle_backdrop.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_OPTIONAL_SOURCE_BATTLE_BACKDROP_V3800 */')==1
 assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
version=re.search(r"versionName '(\d+)\.00\.0-demo'",g)
assert version and int(version.group(1))>=38
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v38.00 optional source-backed dungeon art packaged; offline and v7 preserved')
