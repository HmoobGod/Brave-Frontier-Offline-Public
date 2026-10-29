"""v192: verify the *real built APK* carries atomic token-summon handler.

This changes the existing demo-token summon ONLY, not personal/original Gem
currency, native 2022 summoning, recruitment odds or save schema.
"""
from pathlib import Path
import zipfile

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
APK=R/"app/build/outputs/apk/debug/app-debug.apk"
with zipfile.ZipFile(APK) as z:
 assert z.testzip() is None
 html=z.read("assets/index.html").decode("utf8")
 assert html==(A/"index.html").read_text("utf8")
 assert html.count("BF192_ATOMIC_DEMO_SUMMON")==1
 assert "if(S?.busy||saveRecoveryPending||P?.version!==7)return;" in html
 assert "if(P.summonHistory.length>100)P.summonHistory=P.summonHistory.slice(-100);" in html
 assert "if(!saveProgress()){\n   P=before;" in html
 assert html.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
 assert "bf_global_offline_demo_v7" in html
 assert "BF_GLOBAL_GEMS_PERSONAL_V17000" in html
 assert "BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300" in html
 assert "BF_GLOBAL_UNIT_ARCHIVE_BEGIN" in html
 assert "equal likelihood" in html
 assert 'Recruited '+chr(36)+'{UNIT_BY_ID.get(id).name}' in html
 assert "S?.busy||saveRecoveryPending||P.summonTokens<1" in html
 assert "P._bfGemV170Custom" in html and "P._bfGemV160" in html
 assert "assets/bf17000_personal_gem_rewards_ui.js" in z.namelist()
 assert "assets/bf19100_original_2022_dungeon_backdrops.js" in z.namelist()
 gradle=(R/"app/build.gradle").read_text("utf8")
 assert "applicationId 'org.bravefrontier.offline'" in gradle
print("PASS v192 compiled APK: atomic demo token recruit, no Gem spending and unchanged canonical save")
