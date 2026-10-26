"""Verify packaged source SBB/UBB evidence, original offline Android identity and v7 saves."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=z.namelist()
 assert 'assets/bf8600_original_all_sbb_ubb_checks.js' in names
 js=z.read('assets/bf8600_original_all_sbb_ubb_checks.js').decode('utf8')
 assert js.count('BF_GLOBAL_ALL_SBB_UBB_DROP_CHECKS_V8600')==1
 assert 'sbbProfiles:1290,ubbProfiles:932' in js
 assert 'offensiveSimpleSBB:7,offensiveSimpleUBB:0' in js
 assert "if(fnv(packedSBB)!=='e5d6ec6a'||fnv(packedUBB)!=='e058a575')return;" in js
 assert len(js.encode('utf8'))<65536
 assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8500_original_all_bb_checks.js")')<java.index('readPackagedText("bf8600_original_all_sbb_ubb_checks.js")')
g=(R/'app/build.gradle').read_text('utf8')
v=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(v)==1 and int(v[0].split("'")[1].split('.')[0])>=86
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v86 source SBB/UBB pure reference in signed offline Android package; saves remain v7')