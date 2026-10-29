"""v191 post-Gradle APK: exact seven 2022-source JPEG bytes and lookup.
This verifies a visual-only adapter, not native 2022 enemy formations or AI.
"""
from pathlib import Path
import base64,gzip,hashlib,json,zipfile,re

R=Path(__file__).resolve().parent
AS=R/"app/src/main/assets"
APK=R/"app/build/outputs/apk/debug/app-debug.apk"
table=base64.b64decode("".join((R/"source_data/bf_global_2022_mission_cross_table_v152.json.gz.b64").read_text("ascii").split()),validate=True)
assert hashlib.sha256(table).hexdigest()=="cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a"
data=json.loads(gzip.decompress(table))
assert data["canonicalRowsSha256"]=="2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284"
whitelist={f"dungeon_battle_{i}.jpg" for i in (10200,10300,10400,10500,10600,10700,10800)}
matched={r[0]:r[2] for r in data["rows"] if r[2] in whitelist}
assert len(matched)==29 and len(set(matched.values()))==7
assert set(matched)=={20,21,22,23,30,31,32,33,40,41,42,43,
 50,51,52,53,60,61,62,63,70,71,72,73,81,82,83,84,85}
def gitblob(b):
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()
shas={
 "dungeon_battle_10200.jpg":(36820,"f5feca0464a8553f4f6ddd84b5095a088422867c"),
 "dungeon_battle_10300.jpg":(27958,"1aee08986b144ea5f4873fb077a25b7a4a96f9fe"),
 "dungeon_battle_10400.jpg":(55278,"bd4f819ab828b7a1699723ab900d3a4027e789ec"),
 "dungeon_battle_10500.jpg":(43940,"feb206bbb549f846824203c2477b6ea53553ddda"),
 "dungeon_battle_10600.jpg":(66699,"7dbd52ce75671b968a957715768c587ff0e65f6d"),
 "dungeon_battle_10700.jpg":(32032,"15a260eb75bf17954f4bc90c375fad840149638e"),
 "dungeon_battle_10800.jpg":(46410,"eb2a7732d88483aaef0d74712c7569103d538252"),
}
with zipfile.ZipFile(APK) as apk:
 assert apk.testzip() is None
 for name,(size,sha) in shas.items():
  original=(R/"source_assets/bf1/dungeon"/name).read_bytes()
  assert len(original)==size and gitblob(original)==sha
  assert apk.read("assets/content/dungeon/"+name)==original
  assert (AS/"content/dungeon"/name).read_bytes()==original
 js=apk.read("assets/bf19100_original_2022_dungeon_backdrops.js").decode("utf8")
 assert js==(AS/"bf19100_original_2022_dungeon_backdrops.js").read_text("utf8")
 assert "BF_GLOBAL_2022_MISSION_BACKDROP_SOURCE_V19100" in js
 assert "rows.length!==29" in js and "sourceIsOriginal2022" in js
 assert "nativeWavesDecoded!==false" in js and "nativeEnemyIdsDecoded!==false" in js
 assert "localStorage" not in js and "saveProgress(" not in js
 old=apk.read("assets/bf3800_source_battle_backdrop.js").decode("utf8")
 assert old==(AS/"bf3800_source_battle_backdrop.js").read_text("utf8")
 assert "BFGlobalOriginalDungeonBackdropsV19100?.lookup?.(q.missionId)" in old
 assert "localStorage" not in old and "saveProgress(" not in old
 html=apk.read("assets/index.html").decode("utf8")
 assert html==(AS/"index.html").read_text("utf8")
 assert "bf_global_offline_demo_v7" in html
 java=(R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
 assert java.index('readPackagedText("bf3800_source_battle_backdrop.js")')<java.index(
  'readPackagedText("bf17400_original_2022_encounter_crossrefs.js")')<java.index(
  'readPackagedText("bf19100_original_2022_dungeon_backdrops.js")')
 assert "org.bravefrontier.offline" in (R/"app/build.gradle").read_text("utf8")
print("PASS v191 real APK: seven exact original dungeon JPGs, 29 source-joined quests, no changes to canonical v7, combat or source images")
