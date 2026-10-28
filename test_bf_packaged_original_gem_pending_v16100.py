"""v161: signed APK carries canonical v7 first-clear evidence, no real payout."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
source=(R/'app/src/main/assets/index.html').read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 bundled=z.read('assets/index.html')
 assert bundled==source
 assert b'BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER' in bundled
 assert bundled.count(b'BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING')==1
 assert b'bf161RecordNewFirstClear(previousQuestClearCount)' in bundled
 assert b'out._bfGemV161Pending=bf161ValidateOriginalPending(data._bfGemV161Pending,out.questClears)' in bundled
 assert b'P._bfGemV161Pending=bf161ValidateOriginalPending(P._bfGemV161Pending,P.questClears)' in bundled
 assert bundled.count(b'localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
 assert b'bf_global_offline_demo_v7' in bundled
 assert b'P._bfGemV160.balance++' not in bundled
 assert b'P._bfGemV160.balance+=' not in bundled
 assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
 assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v161: signed APK original 22-finale pending evidence, no new wallet and v7 persistence')
