"""v190: ensure the visible Quest-to-Gems shortcut ships in the compiled APK."""
from pathlib import Path
import zipfile

R=Path(__file__).resolve().parent
JS=R/"app/src/main/assets/bf17000_personal_gem_rewards_ui.js"
JAVA=R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java"
APK=R/"app/build/outputs/apk/debug/app-debug.apk"
source=JS.read_bytes()
with zipfile.ZipFile(APK) as z:
    assert z.testzip() is None
    packaged=z.read("assets/bf17000_personal_gem_rewards_ui.js")
    assert packaged==source, "Gem UI in APK differs from source"
    text=packaged.decode("utf8")
    assert text.count("bf19000-open-gem-rewards")==1
    assert "host.before(shortcut);" in text and "host.after(panel);" in text
    assert "panel.open=true;" in text and "scrollIntoView" in text
    assert "aria-controls" in text and "GEMS · DAILY REWARDS" in text
    assert "localStorage.setItem(" not in text and "saveProgress(" not in text
    html=z.read("assets/index.html").decode("utf8")
    assert "bf_global_offline_demo_v7" in html
    assert "BF_GLOBAL_GEMS_PERSONAL_V17000" in html
assert 'readPackagedText("bf17000_personal_gem_rewards_ui.js")' in JAVA.read_text("utf8")
print("PASS v190 packaged APK: Quest reward shortcut visible, canonical v7 Gem save/claim module unchanged")
