"""v173 signed APK: original first-clear wallet and single canonical save."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
html=(R/'app/src/main/assets/index.html').read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 apk=z.read('assets/index.html')
 assert apk==html
 assert apk.count(b'BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300')==1
 assert b'bf173ValidateOriginalClaims(out._bfGemV160,out._bfGemV161Pending,out._bfGemV170Custom)' in apk
 assert b'bf173ValidateOriginalClaims(P._bfGemV160,P._bfGemV161Pending,P._bfGemV170Custom)' in apk
 assert b'bf173ClaimOriginal()' in apk
 assert b"bf_global_offline_demo_v7" in apk
 assert apk.count(b'localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
 assert b'BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER' in apk
 assert b'BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING' in apk
 assert b'BF_GLOBAL_GEMS_PERSONAL_V17000' in apk
 assert b'_bfImpsV171' in apk
 g=(R/'app/build.gradle').read_text('utf8')
 assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(173,200))
 assert "applicationId 'org.bravefrontier.offline'" in g
 assert 'bf-development-debug.keystore' in g
 assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v173 signed APK original claim + v7 persistence and Android identity')
