"""v26.00 exact original 2022 event PNG SHA-256 validation and offline APK safety."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
R=Path(__file__).resolve().parent
expected={
 'navi_chara1_0.png':'312e926601854589d0c381f2ae9692e2d53c7ad67d1964a8fdd2145cc0fe969d',
 'navi_chara2_0.png':'fe95519338d9026c2d43bc9965c0bef78b1ab98f47842df70f35659f1a253e2d',
 'navi_chara3_0.png':'381c36cb2442c3c4997931d1aa48b3c1cedc291dba13944d4ffd3432738fa9bf'
}
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for image,digest in expected.items():
  src='assets/content/event/'+image
  assert src in files and sha256(z.read(src)).hexdigest()==digest,src
 assert 'assets/bf2600_original_event_portraits.js' in files
 js=z.read('assets/bf2600_original_event_portraits.js').decode('utf8')
 assert js.count('/* BF_GLOBAL_ORIGINAL_EVENT_PORTRAITS_V2600 */')==1
 assert len(js.encode('utf8'))<65536 and 'localStorage' not in js and 'saveProgress(' not in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v26.00 byte-identical original event portraits and Android v7 integrity')
