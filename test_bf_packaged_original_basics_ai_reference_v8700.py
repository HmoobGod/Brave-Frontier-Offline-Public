"""v87 signed Android artifact contains reference only; keeps installed save identity."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
p=R/'app/build/outputs/apk/debug/app-debug.apk'
assert p.is_file()
with ZipFile(p) as z:
    names=z.namelist()
    assert 'assets/bf8700_original_basics_ai_reference.js' in names
    js=z.read('assets/bf8700_original_basics_ai_reference.js').decode('utf8')
    assert js.count('BF_GLOBAL_HISTORICAL_BASICS_AI_REFERENCE_V8700')==1
    assert '797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe' in js
    assert 'confirmed2022:false' in js
    assert len(js.encode('utf8'))<65536
    assert all(t not in js for t in ('localStorage','saveProgress(', 'BFAndroid', 'fetch('))
    assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf200_historical_wave_lab.js")')<java.index('readPackagedText("bf8700_original_basics_ai_reference.js")')
g=(R/'app/build.gradle').read_text('utf8')
v=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(v)==1 and int(v[0].split("'")[1].split('.')[0])>=87
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v87 archived AI read-only source asset in offline signed APK, package/signing/save identity retained')
