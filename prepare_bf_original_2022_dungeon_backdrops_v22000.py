"""v220: stage 15 byte-original 2022 dungeon JPEGs for 77 additional live quests.

All 2022 image/dungeon data are source-pinned. This is a cosmetic opt-in
expansion of v191; it neither decodes native waves nor changes player saves.
"""
from pathlib import Path
from collections import Counter
import base64, gzip, hashlib, json, zipfile

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source_data"
OUT = ROOT / "app/src/main/assets"
ART = ROOT / "source_assets/bf1/dungeon/BF1_Global_2022_15_Dungeon_Backdrops_v220.zip"
COVERAGE = SRC / "bf_global_2022_dungeon_art_v220.json"
ZIP_SHA = "c6ff4f67493839c6af1cc86cce19384899d56c9fa25762edeb96d06f3306a7e9"
SOURCE_ZIP_SHA = "69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
TABLE_SHA = "16f090514d65846f6bd4a9998b50d6c810bc806a79858c0ff766cdb1a22536fc"
TRIPLES_SHA = "efdaf2c44abacb2d939d42a24631af8b16fd175b78e3c27f298f872dba5fe4ce"
V152_GZIP_SHA = "cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a"
V152_ROWS_SHA = "2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284"

def sha(data): return hashlib.sha256(data).hexdigest()

def verified_catalog():
    catalog = json.loads(COVERAGE.read_text("utf8"))
    if not (catalog.get("schema") == "bf-global-2022-source-only-106-playable-dungeon-art-coverage-v220"
            and catalog.get("sourceArchiveSha256") == SOURCE_ZIP_SHA
            and catalog.get("sourceDungeonTableSha256") == TABLE_SHA
            and catalog.get("canonical106MissionTriplesSha256") == TRIPLES_SHA
            and catalog.get("sourceOnly") is False
            and catalog.get("visualFeatureOptIn") is True
            and catalog.get("changesRuntime") is True
            and catalog.get("changesCombat") is False
            and catalog.get("changesSaves") is False
            and catalog.get("nativeEnemyWavesAuthenticated") is False
            and catalog.get("readyForPlayableVisualPromotion") is False):
        raise ValueError("unverified 2022 dungeon catalog provenance")
    groups = catalog.get("dungeonToBackground")
    images = catalog.get("imageSources")
    if type(groups) is not list or type(images) is not list or len(groups) != 23 or len(images) != 22:
        raise ValueError("incomplete original dungeon source")
    if any(type(x) is not list or len(x) != 2 or type(x[0]) is not int or type(x[1]) is not str for x in groups):
        raise ValueError("malformed original dungeon join")
    if len({g[0] for g in groups}) != 23:
        raise ValueError("duplicate original dungeon id")
    by_id = dict(groups)
    files = {a["file"] for a in images}
    if len(files) != 22 or files != set(by_id.values()):
        raise ValueError("incomplete original dungeon artwork")
    for a in images:
        if (type(a) is not dict or type(a.get("sizeBytes")) is not int
                or a["sizeBytes"] < 100 or type(a.get("sha256")) is not str
                or len(a["sha256"]) != 64 or type(a.get("gitBlobSha1")) is not str
                or len(a["gitBlobSha1"]) != 40 or type(a.get("missions")) is not int
                or type(a.get("alreadyPackagedByV191")) is not bool
                or not a["file"].startswith("dungeon_battle_")
                or not a["file"].endswith(".jpg")):
            raise ValueError("malformed original dungeon artwork record")
    assert sum(a["alreadyPackagedByV191"] for a in images) == 7
    assert sum(not a["alreadyPackagedByV191"] for a in images) == 15
    original_ref = SRC / "bf_global_2022_mission_cross_table_v152.json.gz.b64"
    binary = base64.b64decode("".join(original_ref.read_text("ascii").split()), validate=True)
    if sha(binary) != V152_GZIP_SHA:
        raise ValueError("original mission fixture checksum mismatch")
    source = json.loads(gzip.decompress(binary))
    if (source.get("canonicalRowsSha256") != V152_ROWS_SHA
            or source.get("sourceZipSha256") != SOURCE_ZIP_SHA
            or len(source.get("rows", [])) != 142):
        raise ValueError("invalid 2022 mission reference fixture")
    live = json.loads((SRC / "bf_global_original_2022_live_quest_economy_v142.json").read_text("utf8"))
    if live.get("total") != 106 or live.get("sourceArchiveSha256") != SOURCE_ZIP_SHA:
        raise ValueError("original live quest catalog mismatch")
    live_dungeons = {int(r[0]): int(r[1]) for r in live["records"]}
    if len(live_dungeons) != 106:
        raise ValueError("duplicate live 2022 mission id")
    crossrefs = {r[0]: r[2] for r in source["rows"] if r[0] in live_dungeons}
    if len(crossrefs) != 106:
        raise ValueError("missing original 2022 mission reference")
    triples = sorted([mid, dungeon, by_id[dungeon]] for mid, dungeon in live_dungeons.items())
    if sha(json.dumps(triples, separators=(",", ":")).encode()) != TRIPLES_SHA:
        raise ValueError("original 2022 dungeon mission join mismatch")
    if any(crossrefs[mid] != image for mid, _, image in triples):
        raise ValueError("2022 mission-to-dungeon artwork inconsistent")
    tally = Counter(image for _, _, image in triples)
    if any(a["missions"] != tally[a["file"]] for a in images):
        raise ValueError("2022 background usage tally mismatch")
    old = [(mid, image) for mid, _, image in triples if image in {
        f"dungeon_battle_{x}.jpg" for x in (10200, 10300, 10400, 10500, 10600, 10700, 10800)}]
    new = [(mid, image) for mid, _, image in triples if (mid, image) not in old]
    if len(old) != 29 or len(new) != 77:
        raise ValueError("unexpected 2022 coverage change")
    return catalog, old, new


def stage():
    cat, old, new = verified_catalog()
    if sha(ART.read_bytes()) != ZIP_SHA:
        raise ValueError("original artwork archive checksum mismatch")
    with zipfile.ZipFile(ART) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("broken original artwork archive")
        expected = {"SOURCE_MANIFEST_V220.json"} | {
            "content/dungeon/" + a["file"] for a in cat["imageSources"] if not a["alreadyPackagedByV191"]}
        if set(bundle.namelist()) != expected:
            raise ValueError("unexpected files in original artwork archive")
        inner = json.loads(bundle.read("SOURCE_MANIFEST_V220.json"))
        if inner != cat:
            raise ValueError("artwork archive disagrees with original source manifest")
        for a in cat["imageSources"]:
            if a["alreadyPackagedByV191"]:
                continue
            data = bundle.read("content/dungeon/" + a["file"])
            if (len(data) != a["sizeBytes"] or sha(data) != a["sha256"]
                    or data[:2] != b"\xff\xd8" or data[-2:] != b"\xff\xd9"):
                raise ValueError("original artwork source checksum mismatch: " + a["file"])
            dest = OUT / "content/dungeon" / a["file"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.is_file() and dest.read_bytes() != data:
                raise ValueError("refusing to overwrite unlike original source art")
            dest.write_bytes(data)
    # The prior 29-quest source adapter remains authoritative for its coverage.
    # The new 77-quest adapter is runtime read-only and requires the 2022 v174 gate.
    js = """/* BF_GLOBAL_2022_ADDITIONAL_MISSION_BACKDROPS_V22000 */
(()=>{'use strict';
if(window.BFGlobalOriginalDungeonBackdropsV22000||
 typeof P==='undefined'||P.version!==7||
 typeof QUESTS==='undefined'||!Array.isArray(QUESTS)||QUESTS.length!==106)return;
const old=window.BFGlobalOriginalDungeonBackdropsV19100;
const refs=window.BFGlobalEncounterCrossrefsV17400;
if(!old||old.source?.year!==2022||old.source?.missionCount!==29||
 !refs||refs.source?.year!==2022||
 refs.source?.crossTableRowsSha256!=='2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284'||
 refs.source?.nativeWavesDecoded!==false||refs.source?.nativeEnemyIdsDecoded!==false||
 typeof refs.lookup!=='function')return;
const rows=__ROWS__;
const live=new Set(QUESTS.map(q=>q.missionId));
if(rows.length!==77||live.size!==106)return;
const originalImages=new Set(__IMAGES__);
const map=new Map();
for(const [id,image] of rows){
 const ref=refs.lookup(id);
 if(!Number.isSafeInteger(id)||map.has(id)||!live.has(id)||!originalImages.has(image)||
    old.lookup(id)!==null||!ref||!ref.playable||!ref.sourceIsOriginal2022||
    ref.originalDungeonBattleBackground!==image||
    ref.enemyWavesDecoded!==false||ref.enemyAIDecoded!==false||ref.enemyIdsDecoded!==false)return;
 map.set(id,Object.freeze({missionId:id,image,original2022Background:true,
    originalEnemyFormationVerified:false,originalEnemyAIVerified:false}));
}
if(map.size!==77||new Set([...map.values()].map(r=>r.image)).size!==15)return;
const source=Object.freeze({year:2022,missionCount:77,additionalOriginalJpegs:15,
 originalTotalSupportedMissions:106,changesCombat:false,saveFieldsAdded:0,
 nativeWavesDecoded:false,nativeEnemyIdsDecoded:false,nativeDropsDecoded:false});
window.BFGlobalOriginalDungeonBackdropsV22000=Object.freeze({source,
 lookup(id){return Number.isSafeInteger(id)?map.get(id)||null:null;}});
})();"""
    new_imgs = sorted({image for _, image in new})
    js = js.replace("__ROWS__", json.dumps(new, separators=(",", ":")))
    js = js.replace("__IMAGES__", json.dumps(new_imgs, separators=(",", ":")))
    if any(s in js for s in ('localStorage', 'saveProgress(', 'fetch(', 'XMLHttpRequest', 'P.evolutions=', 'P.unitExp=')):
        raise ValueError("unexpected runtime side effects")
    (OUT / "bf22000_original_2022_additional_dungeon_backdrops.js").write_text(js, "utf8")
    # v38 opt-in panel already defaults OFF. Preserve old lookup first and
    # append v220 only when the older source says the mission is unsupported.
    visual = OUT / "bf3800_source_battle_backdrop.js"
    content = visual.read_text("utf8")
    old_line = 'const source2022=window.BFGlobalOriginalDungeonBackdropsV19100?.lookup?.(q.missionId);'
    new_line = ('const source2022=window.BFGlobalOriginalDungeonBackdropsV19100?.lookup?.(q.missionId) ||\n'
                '      window.BFGlobalOriginalDungeonBackdropsV22000?.lookup?.(q.missionId);')
    if new_line not in content:
        if content.count(old_line) != 1:
            raise ValueError("missing/ambiguous v38 visual-only source lookup")
        visual.write_text(content.replace(old_line, new_line), "utf8")
    assert 'bf_global_offline_demo_v7' in (OUT / 'index.html').read_text('utf8')
    print('PASS v220: source-authenticated 106/106 playable original mission backgrounds, 22 distinct JPGs, 15 new originals, opt-in default OFF, no game/save writes')

if __name__ == '__main__': stage()
