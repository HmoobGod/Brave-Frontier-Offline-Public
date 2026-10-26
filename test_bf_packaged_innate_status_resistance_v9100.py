"""v91 verify signed APK includes original-status gameplay guard and source module."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
p=R/'app/build/outputs/apk/debug/app-debug.apk'
with ZipFile(p) as z:
 names=set(z.namelist())
 assert 'assets/bf9100_innate_status_resistance.js' in names
 assert 'assets/bf5700_original_ailment_state.js' in names
 src=z.read('assets/bf9100_innate_status_resistance.js').decode()
 ail=z.read('assets/bf5700_original_ailment_state.js').decode()
 assert 'BF_GLOBAL_INNATE_STATUS_RESISTANCE_V9100' in src
 assert 'BFGlobalInnateStatusResistV9100?.immune(slot,code)' in ail
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode()
g=(R/'app/build.gradle').read_text()
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(91,200)), "v91+ version required"
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text()
print('PASS v91 signed offline APK has innate-status guard; app ID, v7 saves and signer preserved')
