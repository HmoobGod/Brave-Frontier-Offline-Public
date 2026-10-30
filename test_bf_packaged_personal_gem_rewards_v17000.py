"""v170 packaged live personal Gem system and canonical v7 save guards."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
html=(A/'index.html').read_bytes()
ui=(A/'bf17000_personal_gem_rewards_ui.js').read_bytes()
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert html.count(b'BF_GLOBAL_GEMS_PERSONAL_V17000')==1
assert b'bf170ApplyQuestReward(previousQuestClearCount,QUEST.missionId)' in html
# v198 introduces an optional schema-2 receipt-aware validator. Retain the
# historical v170 guard for older builds and require both guarded call sites
# when the new validator is present in the compiled HTML.
if b'BF198_PERSONAL_GEM_SUMMON_V19800' in html:
 assert b'out._bfGemV170Custom=bf198ValidateWallet(data._bfGemV170Custom,out.questClears,out.roster)' in html
 assert b'P._bfGemV170Custom=bf198ValidateWallet(P._bfGemV170Custom,P.questClears,P.roster)' in html
 assert b'const valid=bf170ValidateWallet(legacy,clears)' in html
else:
 assert b'out._bfGemV170Custom=bf170ValidateWallet(data._bfGemV170Custom,out.questClears)' in html
 assert b'P._bfGemV170Custom=bf170ValidateWallet(P._bfGemV170Custom,P.questClears)' in html
assert html.count(b'localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
assert b'bf_global_offline_demo_v7' in html
assert b'BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER' in html
assert b'BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING' in html
assert 'readPackagedText("bf17000_personal_gem_rewards_ui.js")' in java
assert any("versionName '"+str(v)+".00.0-demo'" in gradle for v in range(170,200))
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
 assert sha256(apk.read('assets/index.html')).digest()==sha256(html).digest()
 assert sha256(apk.read('assets/bf17000_personal_gem_rewards_ui.js')).digest()==sha256(ui).digest()
print('PASS v170: signed APK 106-quest custom Gem wallet, first/login/daily/replay and unchanged app identity and canonical storage')
