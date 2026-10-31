"""v223: stage 30 byte-original BF1 evolution-item thumbnails for read-only UI.

The 31st (Legend Stone) is already in the v221 APK. This module never
changes player state, currency, item grants, recipes, combat or save data.
"""
from pathlib import Path
import hashlib
import json
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "source_data/bf_global_2022_evolution_item_art_catalog_v222.json"
PACK = ROOT / "source_assets/bf1/item/BF1_2022_30_Evolution_Item_Thumbnails_v223.zip"
ASSETS = ROOT / "app/src/main/assets"
PACK_SHA256 = "46ca5b5af879685b243dd0416506dfb5fdce5fb3ddc4042cdbf599f6ed01e273"
CATALOG_SHA256 = "3c96e0a37f8fb9cf11b924f6ebb487edd2034f02c7c11f27d9991c6efd13065c"
SOURCE_PACK_SHA256 = "735c50613f55a84d8a3717a4ee53ef513c694031aa44963c43e24b597f134e2c"
LEGEND_SHA256 = "c3decdc9ce4403cf12bf022b0ff233f802b11883105d125a6c0877d85135e0e7"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verified_source(catalog_path=CATALOG, pack_path=PACK):
    catalog = json.loads(Path(catalog_path).read_text("utf-8"))
    if not (catalog.get("schema") == "bf-global-2022-original-evolution-item-material-art-catalog-v222"
            and catalog.get("canonicalRowsSha256") == CATALOG_SHA256
            and catalog.get("sourceBF1ItemPackSha256") == SOURCE_PACK_SHA256
            and catalog.get("sourceArchiveSha256") == "69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
            and catalog.get("originalEvolutionTransitions") == 1342
            and catalog.get("unitMaterialSlotsType1") == 7107
            and catalog.get("distinctUnitMaterialIdsType1") == 85
            and catalog.get("itemMaterialSlotsType2") == 333
            and catalog.get("distinctItemMaterialIdsType2") == 31
            and catalog.get("legendStoneItemId") == 110100
            and catalog.get("legendStoneSlotCount") == 279
            and catalog.get("readOnlySourceCatalog") is True
            and catalog.get("other30ImagesPackagedInApp") is False
            and all(catalog.get(flag) is False for flag in ("changesGameplay", "changesInventory", "changesSaves", "unlocksPlayableEvolutions"))):
        raise ValueError("original 2022 item source catalog flags/provenance failed")
    rows = catalog.get("rows")
    if not isinstance(rows, list) or len(rows) != 31 or digest(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()) != CATALOG_SHA256:
        raise ValueError("original 2022 item catalog digest mismatch")
    if (sum(row[3] for row in rows) != 333 or sum(row[4] for row in rows) != 180761
            or len(set(row[0] for row in rows)) != 31 or len(set(row[2] for row in rows)) != 31
            or not any(row[0] == 110100 and row[5] == LEGEND_SHA256 for row in rows)):
        raise ValueError("original 2022 item counts/Legend Stone mismatch")
    expected = set()
    for row in rows:
        if (not isinstance(row, list) or len(row) != 6 or type(row[0]) is not int
                or type(row[1]) is not str or type(row[2]) is not str
                or type(row[3]) is not int or type(row[4]) is not int
                or type(row[5]) is not str or len(row[5]) != 64
                or not re.fullmatch(r"item_thum_[0-9]+\.png", row[2])
                or row[3] < 1 or row[4] < 100):
            raise ValueError("invalid item thumbnail path/shape")
        if row[0] != 110100:
            expected.add("content/item/" + row[2])
    binary = Path(pack_path).read_bytes()
    if digest(binary) != PACK_SHA256:
        raise ValueError("original source thumbnail bundle SHA-256 mismatch")
    with zipfile.ZipFile(pack_path) as source:
        if source.testzip() is not None or len(source.namelist()) != 30 or set(source.namelist()) != expected:
            raise ValueError("unexpected or unsafe ZIP contents")
        for row in rows:
            if row[0] == 110100:
                continue
            name = "content/item/" + row[2]
            info = source.getinfo(name)
            if info.is_dir() or info.file_size > 150000 or info.compress_type != zipfile.ZIP_STORED:
                raise ValueError("invalid original thumbnail ZIP member " + name)
            img = source.read(name)
            if len(img) != row[4] or digest(img) != row[5] or img[:8] != b"\x89PNG\r\n\x1a\n" or img[12:16] != b"IHDR":
                raise ValueError("original thumbnail byte mismatch " + name)
            w, h = struct.unpack(">II", img[16:24])
            if not (16 <= w <= 1024 and 16 <= h <= 1024):
                raise ValueError("original thumbnail invalid dimensions " + name)
    return catalog, rows


def stage():
    cat, rows = verified_source()
    target = ASSETS / "content/item"
    target.mkdir(parents=True, exist_ok=True)
    original = next(r for r in rows if r[0] == 110100)
    v221 = target / original[2]
    if not v221.exists() or len(v221.read_bytes()) != original[4] or digest(v221.read_bytes()) != LEGEND_SHA256:
        raise ValueError("existing original v221 Legend Stone image mismatch")
    with zipfile.ZipFile(PACK) as source:
        for row in rows:
            if row[0] == 110100:
                continue
            img = source.read("content/item/" + row[2])
            dest = target / row[2]
            if dest.exists() and dest.read_bytes() != img:
                raise ValueError("refuse overwrite unlike packaged item " + row[2])
            dest.write_bytes(img)
    names = [[r[0], r[2], r[3]] for r in rows]
    js = r"""/* BF_GLOBAL_ORIGINAL_2022_TYPED_EVOLUTION_ITEM_GALLERY_V22300 */
(()=>{'use strict';
if(window.BFGlobalOriginalEvolutionItemGalleryV22300 ||
   typeof P==='undefined'||P.version!==7||!Array.isArray(P.roster) ||
   !window.BFGlobalOriginalLegendStoneExchangeV15300 ||
   window.BFGlobalOriginalLegendStoneExchangeV15300.source?.liveAcquisition!==false ||
   window.BFGlobalOriginalLegendStoneExchangeV15300.source?.saveMutation!==false)return;
const host=document.getElementById('bf15300-legend-stone-source');
if(!host)return;
const rows=__ROWS__;
const ids=new Set(rows.map(row=>row[0])),names=new Set(rows.map(row=>row[1]));
if(rows.length!==31||ids.size!==31||names.size!==31||
 rows.reduce((n,row)=>n+row[2],0)!==333||
 rows.find(row=>row[0]===110100)?.[1]!=='item_thum_111000.png')return;
const root=document.createElement('details');
root.id='bf22300-original-evolution-item-gallery';
root.style.cssText='margin:10px 4px;padding:9px;border:1px solid #728596;border-radius:7px;background:#223443;color:#f1f4f8;font:12px/1.5 system-ui';
const summary=document.createElement('summary');
summary.textContent='Original 2022 evolution-item artwork · 31 source references (read-only)';
summary.style.cssText='font-weight:700;cursor:pointer;min-height:36px';
const note=document.createElement('p');
note.textContent='Archived artwork reference only. These images are not evidence of owned items. Evolution unit materials are a separate category. This screen does not grant items, spend currency or unlock evolution.';
const gallery=document.createElement('div');
gallery.id='bf22300-original-item-grid';
gallery.style.cssText='display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:7px';
for(const [id,name,slots] of rows){
 const item=document.createElement('figure');
 item.style.cssText='margin:0;padding:6px;text-align:center;background:#293e4f;border-radius:5px';
 const img=document.createElement('img');
 img.src='content/item/'+name;img.alt='Original 2022 item reference '+id;
 img.width=60;img.height=60;img.loading='lazy';
 img.style.cssText='width:60px;height:60px;object-fit:contain';
 const label=document.createElement('figcaption');
 label.textContent='Item #'+id+' · '+slots+' recipe slot'+(slots===1?'':'s');
 item.append(img,label);gallery.append(item);
}
root.append(summary,note,gallery);
host.after(root);
const frozen=Object.freeze(rows.map(([id,image,slots])=>Object.freeze({itemId:id,image,originalRecipeSlots:slots,owned:false,grantable:false})));
window.BFGlobalOriginalEvolutionItemGalleryV22300=Object.freeze({
 source:Object.freeze({year:2022,itemCount:31,originalNewImages:30,type2Slots:333,readOnly:true,changesGameplay:false,changesInventory:false,changesSaves:false}),
 rows:frozen,lookup(id){return Number.isSafeInteger(id)?frozen.find(r=>r.itemId===id)||null:null;}
});
})();
"""
    js = js.replace("__ROWS__", json.dumps(names, ensure_ascii=False, separators=(",", ":")))
    if any(x in js for x in ("localStorage", "saveProgress(", "P.materials=", "P.roster=", "fetch(", "XMLHttpRequest", "setItem(", "removeItem(")):
        raise ValueError("unexpected v223 gallery side effect")
    (ASSETS / "bf22300_original_2022_evolution_item_gallery.js").write_text(js, encoding="utf-8")
    print("PASS v223 31 source-original evolution item icons (30 staged), 333 item slots, read-only v7 UI")


if __name__ == "__main__":
    stage()
