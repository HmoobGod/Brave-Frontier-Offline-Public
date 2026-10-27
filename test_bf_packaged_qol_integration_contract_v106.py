"""v106 final packaged APK: exact QoL asset bytes, Android identity and v7 key."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
from test_bf_qol_integration_contract_v106 import MODULES

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
with ZipFile(ROOT/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for name,marker in MODULES:
  member='assets/'+name
  assert member in names,name
  bundled=z.read(member)
  assert sha256(bundled).digest()==sha256((ASSETS/name).read_bytes()).digest(),name
  assert bundled.decode('utf8').count(marker)==1,name
 assert 'assets/index.html' in names
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
print('PASS v106 APK holds all exact QoL modules with unchanged offline v7 save contract')
