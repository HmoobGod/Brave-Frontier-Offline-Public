"""v171: signed APK carries canonical Imp save adapter and new cap engine."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
html=(A/'index.html').read_bytes()
imps=(A/'bf16900_optional_imp_fusion.js').read_bytes()
assert html.count(b'BF_GLOBAL_IMP_CANONICAL_V17100')==1
assert b'out._bfImpsV171=bf171ValidateCanonicalImps(data._bfImpsV171)' in html
assert b'P._bfImpsV171=bf171ValidateCanonicalImps(P._bfImpsV171)' in html
assert html.count(b'localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
assert b'_bfGemV170Custom' in html
assert b'bf_global_offline_demo_v7' in html
assert b'Math.max(n,Math.floor((n*5/4)/steps[i])*steps[i])' in imps
assert b'P[canonicalField]=checked' in imps
assert b'localStorage.setItem(key' not in imps
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '171.00.0-demo'" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert z.read('assets/index.html')==html
 assert z.read('assets/bf16900_optional_imp_fusion.js')==imps
 assert b'BF_GLOBAL_IMP_CANONICAL_V17100' in z.read('assets/index.html')
 assert b'_bfImpsV171' in z.read('assets/index.html')
print('PASS v171: canonical Imp backup in signed APK, strict <=125% caps and stable Android/save identity')
