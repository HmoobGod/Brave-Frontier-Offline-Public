# v223 — Byte-original 2022 Global evolution-item artwork, read-only reference

**DRAFT CANDIDATE — source/browser/full Android CI and independent exact-head Claude approval required before merge.** This changes only the optional source reference display and APK cosmetic assets. Not a new player item inventory, new currency or evolution unlock.

## Authenticated original data

- Owner-verified 2022 `mst-decoded.zip` SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` and `BF1_item_part001.zip` SHA-256 `735c50613f55a84d8a3717a4ee53ef513c694031aa44963c43e24b597f134e2c`.
- The previously merged v222 catalog pins 31 **type-2 item materials**, 333 type-2 recipe slots, and the entirely distinct 7,107 **type-1 unit-material** slots. No unit-material image is mistaken for a type-2 item here.
- All 31 exact archived PNG images total 180,761 original bytes. The original Legend Stone `item_thum_111000.png` already ships with v221. The v223 bundle adds the other 30 originals (174,391 original PNG bytes), with each size and SHA-256 independently validated against the v222 catalog and owner item pack.
- Newly committed source bundle `source_assets/bf1/item/BF1_2022_30_Evolution_Item_Thumbnails_v223.zip`, SHA-256 `46ca5b5af879685b243dd0416506dfb5fdce5fb3ddc4042cdbf599f6ed01e273` (ZIP STORED original PNGs, strict file-set check).

## Safe implementation and tests

- Strict source preflight rejects altered source checksums, malformed paths, non-original PNG bytes, or source catalog drift. Build preparation stages all 30 original PNG files under the packaged offline `content/item/` path, verifies the existing v221 image, generates a read-only gallery adapter, and refuses to overwrite unlike bytes.
- The new collapsible v223 gallery is **closed by default** and lists source item IDs, original archived image thumbnails and how many original recipe slots use each item. It does not show an unverified translation of unresolved `MST_EVOITEM_*` keys. The UI says plainly that the art is not evidence of item ownership or acquisition. It does not read or write saved progression.
- Chromium tests use an isolated fixture and load each of the 31 genuine PNGs. They confirm the gallery is idempotent, closed by default, and leaves `P`, `S`, and the canonical v7 save unchanged. APK tests check actual packaged bytes of all 31 thumbnails and the JS adapter against their exact source SHA-256 values.
- No changes to player inventory, Merit balances, purchase flows, drop tables, unit material costs, evolution availability, EXP, BB/CGG, manifest, signing, Java app identity or existing v7 save schema. Android Java only reads/evaluates the optional source reference script, failing safely if unavailable.

## Merge and owner APK policy

Require PR-head source CI, full Android browser tests and compiled APK tests, independent Claude exact-commit review, unchanged main/head and SHA-guarded merge; verify postmerge source and full Android CI on the actual new main SHA. Do **not** promote Current, overwrite the owner's APK, or change user saves before in-place Android acceptance using a backed-up v7 save.
