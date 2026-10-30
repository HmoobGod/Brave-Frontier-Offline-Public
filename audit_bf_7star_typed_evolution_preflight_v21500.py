"""v215: read-only, synthetic 7/8-star starter evolution resource preflight.

NEVER load player saves or interpret the DEMO material inventory. The separately
typed maps supplied here are synthetic test fixtures, NOT a game/save schema.
All native 2022 evolution/playability gates remain false.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_data/bf_global_2022_starter_typed_evolution_v130.json"
MANIFEST = ROOT / "source_data/bf_global_2022_starter_7_8_source_readiness_v127.json"
ZIP_SHA = "69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
ROWS_SHA = "a5b91a61b5101f378fcc2692ca97b601c2034cf150c0716e9b561aebc7a0bed6"
MANIFEST_SHA = "dcd3fb0f3d57b44880088f42c87409e3588a24a183ec866095ea0dbeae57bcbd"


def recipe_rows(source=None, manifest=None):
    """Fail closed on altered source provenance, lineage, materials or typing."""
    if source is None:
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if manifest is None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(source, dict) or not isinstance(manifest, dict):
        raise ValueError("source manifest type mismatch")
    if not (
        source.get("schema") == "bf-global-2022-starter-7-8-typed-evolution-v130"
        and source.get("sourceZipSha256") == ZIP_SHA
        and manifest.get("sourceZipSha256") == ZIP_SHA
        and manifest.get("schema") == "bf-global-2022-7-8-starter-source-readiness-v127"
        and source.get("verifiedInputCanonical12Sha256") == MANIFEST_SHA
        and manifest.get("canonical12SourceSha256") == MANIFEST_SHA
        and source.get("typedRowsSha256") == ROWS_SHA
        and source.get("saveMutation") is False
        and source.get("playableChange") is False
    ):
        raise ValueError("unverified evolution source provenance")
    rows = source.get("rows")
    source_forms = manifest.get("rows")
    if not isinstance(rows, list) or not isinstance(source_forms, list):
        raise ValueError("missing source recipes")
    if len(rows) != 12 or len(source_forms) != 12:
        raise ValueError("must have twelve source forms")
    if any(type(row) is not list or len(row) != 8 for row in rows):
        raise ValueError("malformed source recipe row")
    for unit in source_forms:
        if type(unit) is not dict:
            raise ValueError("malformed source form")
        evo = unit.get("originalEvo")
        if type(evo) is not dict or type(evo.get("materialSlots")) is not list:
            raise ValueError("malformed original evolution source")
        if any(type(slot) is not dict for slot in evo["materialSlots"]):
            raise ValueError("malformed source material record")
    try:
        canon = json.dumps(rows, separators=(",", ":"), ensure_ascii=True).encode()
    except (TypeError, ValueError):
        raise ValueError("source recipe rows are not JSON-serializable") from None
    if hashlib.sha256(canon).hexdigest() != ROWS_SHA:
        raise ValueError("source recipe checksum mismatch")
    if [r[0] for r in rows] != [u.get("unitId") for u in source_forms]:
        raise ValueError("source unit identity mismatch")
    for row, unit in zip(rows, source_forms):
        if type(row) is not list or len(row) != 8:
            raise ValueError("malformed typed evolution row")
        uid, previous, rarity, cost, cap, zel, karma, materials = row
        expected = (
            [unit.get("unitId"), unit.get("previousFormId"), unit.get("rarity"),
             unit.get("unitCost"), unit.get("unitMaxLevel"),
             unit.get("originalEvo", {}).get("zel"),
             unit.get("originalEvo", {}).get("karma"),
             [[m.get("sourceSlot"), m.get("type"), m.get("id")]
              for m in unit.get("originalEvo", {}).get("materialSlots", [])]]
        )
        if row != expected:
            raise ValueError("source manifest disagrees with original typed evolution")
        if not all(type(x) is int for x in (uid, previous, rarity, cost, cap, zel, karma)):
            raise ValueError("invalid numeric field")
        if uid != previous + 1 or uid % 100 not in (16, 17):
            raise ValueError("unexpected starter lineage")
        if (cost, cap, zel, karma) != (
            (38, 120, 1500000, 0) if rarity == 7 else
            (45, 150, 3000000, 1000000)
        ) or rarity not in (7, 8):
            raise ValueError("unexpected original source costs or cap")
        if type(materials) is not list or len(materials) != (5 if rarity == 7 else 8):
            raise ValueError("missing original material slots")
        if not all(type(slot) is list and len(slot) == 3 and
                   all(type(v) is int for v in slot) for slot in materials):
            raise ValueError("malformed typed source slot")
        if [m[0] for m in materials] != list(range(1, len(materials) + 1)):
            raise ValueError("wrong source slot order")
        if [m[1] for m in materials] != [1] * (len(materials) - 1) + [2]:
            raise ValueError("typed original item conflated with evolution unit")
        if materials[-1][2] != 110100:
            raise ValueError("missing original Legend Stone item")
    if [x[0] for x in rows if x[2] == 7] != [k * 10000 + 16 for k in range(1, 7)]:
        raise ValueError("incomplete six starter 7-star set")
    if [x[0] for x in rows if x[2] == 8] != [k * 10000 + 17 for k in range(1, 7)]:
        raise ValueError("incomplete six starter 8-star set")
    return rows


def _count_map(data):
    if type(data) is not dict or any(
        type(k) is not int or k <= 0 or type(v) is not int or v < 0
        for k, v in data.items()
    ):
        raise ValueError("invalid synthetic inventory")
    return data


def preflight(target, owned_forms, unit_materials, original_items,
              zel, karma, source=None, manifest=None):
    """Evaluate resource coverage ONLY; cannot authorize an actual evolution."""
    if type(target) is not int or type(owned_forms) not in (set, frozenset):
        raise ValueError("invalid synthetic target or roster")
    if any(type(i) is not int or i <= 0 for i in owned_forms):
        raise ValueError("invalid synthetic roster")
    for amount in (zel, karma):
        if type(amount) is not int or amount < 0:
            raise ValueError("invalid synthetic currency")
    _count_map(unit_materials)
    _count_map(original_items)
    recipes = recipe_rows(source, manifest)
    match = next((r for r in recipes if r[0] == target), None)
    if match is None:
        raise ValueError("target not original verified starter recipe")
    _, previous, rarity, _, _, cost_zel, cost_karma, slots = match
    units = Counter(m[2] for m in slots if m[1] == 1)
    items = Counter(m[2] for m in slots if m[1] == 2)
    # Keep every original item in its own typed namespace. In particular
    # unit_materials[110100] can NEVER satisfy original_items[110100].
    missing_units = {k: n - unit_materials.get(k, 0) for k, n in units.items()
                     if unit_materials.get(k, 0) < n}
    missing_items = {k: n - original_items.get(k, 0) for k, n in items.items()
                     if original_items.get(k, 0) < n}
    covered = (previous in owned_forms and target not in owned_forms
               and zel >= cost_zel and karma >= cost_karma
               and not missing_units and not missing_items)
    return {
        "schema": "bf-global-v215-synthetic-typed-evolution-preflight",
        "sourceTargetId": target,
        "sourcePreviousFormId": previous,
        "sourceRarity": rarity,
        "sourceMaterialUnitCounts": dict(sorted(units.items())),
        "sourceOriginalItemCounts": dict(sorted(items.items())),
        "missingSyntheticUnitCounts": dict(sorted(missing_units.items())),
        "missingSyntheticItemCounts": dict(sorted(missing_items.items())),
        "syntheticResourceCoverage": covered,
        "original2022ExpAndLevelRulesVerified": False,
        "original2022VisualAnimationRulesVerified": False,
        "original2022EvolutionInventorySemanticsVerified": False,
        "original2022EvolutionAuthorized": False,
        "changesPlayability": False,
        "readsOrWritesPlayerSaves": False,
        "sourceScope": "synthetic preflight only; no player inventory access",
    }
