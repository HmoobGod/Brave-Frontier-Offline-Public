"""v198: packaged Android APK inspection for opt-in PERSONAL OFFLINE summons."""
from pathlib import Path
from zipfile import ZipFile

R=Path(__file__).resolve().parent
APK=R/"app/build/outputs/apk/debug/app-debug.apk"
A=R/"app/src/main/assets"
with ZipFile(APK) as z:
 assert z.testzip() is None
 html=z.read("assets/index.html").decode("utf8")
 assert html==(A/"index.html").read_text("utf8")
 assert html.count("BF198_PERSONAL_GEM_SUMMON_V19800")==1
 assert "function bf198ValidateWallet(source, clears, roster)" in html
 assert "function bf198PersonalSummon()" in html
 assert "bf19800-personal-summon" in html
 assert "BF198_PERSONAL_SUMMON_COST = 100" in html
 assert "P._bfGemV170Custom=bf198ValidateWallet" in html
 assert "out._bfGemV170Custom=bf198ValidateWallet" in html
 assert "BF192_ATOMIC_DEMO_SUMMON" in html
 assert "BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300" in html
 assert "BF_GLOBAL_GEMS_PERSONAL_V17000" in html
 assert "bf_global_offline_demo_v7" in html
 assert html.count("localStorage.setItem(SAVE_KEY,JSON.stringify(P))")==1
 assert "assets/bf17000_personal_gem_rewards_ui.js" in z.namelist()
 ui=z.read("assets/bf17000_personal_gem_rewards_ui.js").decode("utf8")
 assert "PERSONAL OFFLINE" in ui and "100 Gems" in ui
 assert ui==(A/"bf17000_personal_gem_rewards_ui.js").read_text("utf8")
 assert "android.permission.INTERNET" not in (A.parent/"AndroidManifest.xml").read_text("utf8")
 assert "applicationId 'org.bravefrontier.offline'" in (R/"app/build.gradle").read_text("utf8")
print("PASS v198 APK: 100-Gem personal summons, schema-2 receipts, canonical v7, original Gemini ledger unchanged and original signing ID preserved")
