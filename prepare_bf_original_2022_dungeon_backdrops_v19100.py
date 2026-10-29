"""v191: 29 2022-original mission-to-backdrop joins; seven byte-exact BF1 JPGs.

Never infer 2022 enemy waves, native AI, loot or background animation from
opaque mission fields. This is an opt-in cosmetic source-visual expansion only.
"""
from pathlib import Path
import base64, gzip, hashlib, json, re

R=Path(__file__).resolve().parent
SRC=R/"source_data"
OUT=R/"app/src/main/assets"
MASTER_SHA="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
ZIP_GZ_SHA="cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a"
RAW_SHA="2f5daf4b5c74fcc53965f1115e5e1ce37bf788f03e372900f57bb1bd9843f2f7"
CANON_SHA="2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284"
# Git source-object SHA-1 of the *original archived JPEG files*, not art generated
# from an emulator. The v27 10200 JPG additionally has its original SHA-256 gate.
JPEG_GIT_BLOBS={
  "dungeon_battle_10200.jpg":(36820,"f5feca0464a8553f4f6ddd84b5095a088422867c"),
  "dungeon_battle_10300.jpg":(27958,"1aee08986b144ea5f4873fb077a25b7a4a96f9fe"),
  "dungeon_battle_10400.jpg":(55278,"bd4f819ab828b7a1699723ab900d3a4027e789ec"),
  "dungeon_battle_10500.jpg":(43940,"feb206bbb549f846824203c2477b6ea53553ddda"),
  "dungeon_battle_10600.jpg":(66699,"7dbd52ce75671b968a957715768c587ff0e65f6d"),
  "dungeon_battle_10700.jpg":(32032,"15a260eb75bf17954f4bc90c375fad840149638e"),
  "dungeon_battle_10800.jpg":(46410,"eb2a7732d88483aaef0d74712c7569103d538252"),
}
def sha(b):return hashlib.sha256(b).hexdigest()
def gitblob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()

z=base64.b64decode("".join((SRC/"bf_global_2022_mission_cross_table_v152.json.gz.b64").read_text("ascii").split()),validate=True)
assert sha(z)==ZIP_GZ_SHA
raw=gzip.decompress(z);assert sha(raw)==RAW_SHA
m=json.loads(raw)
assert m["sourceZipSha256"]==MASTER_SHA
assert m["canonicalRowsSha256"]==CANON_SHA
assert m["schema"]=="bf-global-original-2022-142-mission-cross-table-evidence-v152"
assert m["columns"]==["missionId","opaqueEncounterField","dungeonBackdrop","matchingGrandSpotRows","matchingRaidPointRows"]
assert len(m["rows"])==142
assert sha(json.dumps(m["rows"],ensure_ascii=False,separators=(",",":")).encode())==CANON_SHA
live=json.loads((SRC/"bf_global_original_2022_live_quest_economy_v142.json").read_text("utf8"))
assert live["total"]==106 and len(live["records"])==106
ids={r[0] for r in live["records"]}
assert len(ids)==106
expected=sorted((row[0],row[2]) for row in m["rows"] if row[2] in JPEG_GIT_BLOBS)
assert len(expected)==29 and len({r[0] for r in expected})==29
assert {name for _,name in expected}==set(JPEG_GIT_BLOBS)
assert all(mid in ids for mid,_ in expected), "Only original 2022 playable missions"
assert [mid for mid,_ in expected]==[
  20,21,22,23,30,31,32,33,40,41,42,43,50,51,52,53,
  60,61,62,63,70,71,72,73,81,82,83,84,85]
assert {name:sum(row[1]==name for row in expected) for name in JPEG_GIT_BLOBS}=={
  **{f"dungeon_battle_{n}.jpg":4 for n in (10200,10300,10400,10500,10600,10700)},
  "dungeon_battle_10800.jpg":5}

# All source JPEGs already belong to the user's original BF1 asset pack.
# Copy only after original source-object checksum, byte length and JPEG markers.
for filename,(size,blobsha) in JPEG_GIT_BLOBS.items():
  src=R/"source_assets/bf1/dungeon"/filename
  data=src.read_bytes()
  assert len(data)==size and gitblob(data)==blobsha,filename
  assert data[:2]==b"\xff\xd8" and data[-2:]==b"\xff\xd9",filename
  if filename=="dungeon_battle_10200.jpg":
    assert sha(data)=="50b7833e5045b5ffbf23056d33ee13d1e96654e9665e6b4d770fe6f8baef473b"
  dest=OUT/"content/dungeon"/filename
  dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.is_file():assert dest.read_bytes()==data,"Cannot overwrite an unlike original JPG"
  else:dest.write_bytes(data)

js=r"""/* BF_GLOBAL_2022_MISSION_BACKDROP_SOURCE_V19100 */
(()=>{
'use strict';
if(window.BFGlobalOriginalDungeonBackdropsV19100||
   typeof P==='undefined'||P.version!==7||
   typeof QUESTS==='undefined'||!Array.isArray(QUESTS)||QUESTS.length!==106)return;
const refs=window.BFGlobalEncounterCrossrefsV17400;
if(!refs||refs.source?.year!==2022||
  refs.source?.crossTableRowsSha256!=='2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284'||
  refs.source?.nativeWavesDecoded!==false||
  refs.source?.nativeEnemyIdsDecoded!==false||
  typeof refs.lookup!=='function')return;
// From owner's exact 2022 master: mission id -> original dungeon background.
const rows=__ROWS__;
const liveIds=new Set(QUESTS.map(q=>q.missionId));
if(liveIds.size!==106||rows.length!==29)return;
const images=new Set(['dungeon_battle_10200.jpg','dungeon_battle_10300.jpg',
'dungeon_battle_10400.jpg','dungeon_battle_10500.jpg',
'dungeon_battle_10600.jpg','dungeon_battle_10700.jpg',
'dungeon_battle_10800.jpg']);
const source=Object.freeze({year:2022,missionCount:29,jpegCount:7,
  missionCrossTableSha256:'2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284',
  changesCombat:false,nativeEnemyWavesDecoded:false,nativeEnemyAIDecoded:false,
  nativeDropsDecoded:false,saveFieldsAdded:0});
const map=new Map();
for(const [id,image] of rows){
 const ref=refs.lookup(id);
 if(!Number.isSafeInteger(id)||map.has(id)||!liveIds.has(id)||
    !images.has(image)||!ref||!ref.playable||!ref.sourceIsOriginal2022||
    ref.originalDungeonBattleBackground!==image||
    ref.enemyWavesDecoded!==false||ref.enemyAIDecoded!==false||
    ref.enemyIdsDecoded!==false)return;
 map.set(id,Object.freeze({missionId:id,image,original2022Background:true,
   originalEnemyFormationVerified:false,originalEnemyAIVerified:false}));
}
if(map.size!==29||new Set([...map.values()].map(r=>r.image)).size!==7)return;
window.BFGlobalOriginalDungeonBackdropsV19100=Object.freeze({
 source,
 lookup(id){return Number.isSafeInteger(id)?map.get(id)||null:null;}
});
})();"""
js=js.replace("__ROWS__",json.dumps(expected,separators=(",",":")))
assert js.count("BF_GLOBAL_2022_MISSION_BACKDROP_SOURCE_V19100")==1
assert len(js.encode())<65536
assert not any(x in js for x in ("localStorage","saveProgress(","P.unitExp=","S.enemies=","Math.random(","fetch(","XMLHttpRequest"))
(OUT/"bf19100_original_2022_dungeon_backdrops.js").write_text(js,"utf8")
assert "bf_global_offline_demo_v7" in (OUT/"index.html").read_text("utf8")
print("PASS v191: 7 byte-original dungeon JPGs, 29 source-matched original 2022 missions; no gameplay/save changes")
