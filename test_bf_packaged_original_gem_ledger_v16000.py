"""v160: verify signed APK contains exact source-Gem legacy ledger, no grant."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
bundle=(R/'app/src/main/assets/index.html').read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 apk=z.read('assets/index.html')
 assert apk==bundle
 assert apk.count(b'BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER')==1
 assert b'out._bfGemV160=bf160MigratedGemState(data._bfGemV160,out.questClears);' in apk
 assert b'P._bfGemV160=bf160MigratedGemState(P._bfGemV160,P.questClears);' in apk
 assert b'questClears:{},lastMission:1,_bfGemV160:{schema:1,balance:0,paidFinales:[],legacyFinales:[]}' in apk
 assert b"bf_global_offline_demo_v7" in apk
 assert b'P._bfGemV160.balance+=' not in apk
 java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
 assert 'bf16000_wallet.js' not in java
 assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
 assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
print('PASS v160: byte-exact APK legacy Gem ledger, canonical v7 key and no live awards')
