"""v207: verify Amdahl's original read-only 2022 guide in the COMPILED APK.

This gate checks packaged bytes, Java source injection order and DEX-embedded
asset name. It does not claim Android lifecycle/device execution, original enemy
waves, save migration on device, or authenticity beyond pinned source fixtures.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
APK = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
ASSETS = ROOT / "app/src/main/assets"
JAVA = ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java"
GRADLE = ROOT / "app/build.gradle"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
SOURCE = ROOT / "source_data/bf_global_2022_amdahl_quest_readiness_v147.json"
LIVE = ROOT / "source_data/bf_global_original_2022_live_quest_economy_v142.json"
GUIDE = "bf20600_amdahl_source_quest_guide.js"
ORDER = ("bf14900_original_amdahl_art.js",
         "bf15100_amdahl_encounter_evidence.js",
         GUIDE,
         "bf17400_original_2022_encounter_crossrefs.js")
MASTER = "d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
QUEST = "f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3"

assert APK.is_file(), "Build debug APK before executing v207"
readiness = json.loads(SOURCE.read_text("utf8"))
economy = json.loads(LIVE.read_text("utf8"))
assert len(readiness["quests"]) == 36
assert len(readiness["dungeons"]) == 7
assert readiness["provenance"]["missionTableSha256"] == economy["missionMasterSha256"] == MASTER
assert readiness["provenance"]["questCanonSha256"] == QUEST
assert readiness["area"]["playableNow"] is False
assert readiness["area"]["originalEnemyWavesDecoded"] is False
assert economy["total"] == 106
java = JAVA.read_text("utf8")
assert all(java.count('readPackagedText("' + n + '")') == 1 for n in ORDER)
positions = [java.index('readPackagedText("' + n + '")') for n in ORDER]
assert positions == sorted(positions), "Source module injection order changed"
assert 'view.evaluateJavascript(amdahlGuide, null);' in java
assert 'Optional original Amdahl story guide unavailable' in java
assert "applicationId 'org.bravefrontier.offline'" in GRADLE.read_text("utf8")
assert "android.permission.INTERNET" not in MANIFEST.read_text("utf8")
source_bytes = (ASSETS / GUIDE).read_bytes()
source_text = source_bytes.decode("utf8")
assert len(source_bytes) < 65536
assert source_text.count("BF_AMDAHL_ORIGINAL_2022_STORY_GUIDE_V20600") == 1
assert source_text.count(MASTER) == source_text.count(QUEST) == 1
assert "const MASTER_SHA256='" + MASTER + "'" in source_text
assert "const QUEST_SHA256='" + QUEST + "'" in source_text
assert "masterSha256:MASTER_SHA256" in source_text
assert "canonicalQuestSha256:QUEST_SHA256" in source_text
assert "localStorage.setItem" not in source_text
assert "QUESTS.push" not in source_text

with ZipFile(APK) as apk:
    assert apk.testzip() is None, "APK archive contains corrupt members"
    names = set(apk.namelist())
    for n in ORDER:
        key = "assets/" + n
        assert key in names, "Missing packaged script: " + key
        assert apk.read(key) == (ASSETS / n).read_bytes(), "Wrong packaged asset bytes: " + n
    assert apk.read("assets/" + GUIDE) == source_bytes
    html = apk.read("assets/index.html")
    assert html == (ASSETS / "index.html").read_bytes()
    assert b"bf_global_offline_demo_v7" in html
    assert html.count(b"localStorage.setItem(SAVE_KEY,JSON.stringify(P))") == 1
    dex_files = sorted(n for n in names if re.fullmatch(r"classes(?:[0-9]+)?\.dex", n))
    assert dex_files, "No compiled DEX classes in APK"
    dex = [apk.read(n) for n in dex_files]
    needle = GUIDE.encode("ascii")
    assert sum(blob.count(needle) for blob in dex) == 1, (
        "Compiled Android DEX missing or duplicates readPackagedText guide name")
    assert any(needle in blob and b"evaluateJavascript" in blob for blob in dex), (
        "Compiled DEX lacks WebView evaluateJavascript near guide reference")
    for n in ORDER:
        assert sum(blob.count(n.encode("ascii")) for blob in dex) >= 1, (
            "Compiled Android DEX lost source dependency: " + n)

print("PASS v207: compiled APK bytes, full 2022 SHA, ordered Android DEX guide reference, 106 quests, v7 save key")
