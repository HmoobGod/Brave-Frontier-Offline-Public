"""v217: isolate 7-star set completeness, exact corruption reason, JSON-only source.

These are synthetic in-memory manifest mutations. No production app, owner
inventory, Android APK, network requests, or saved player progress are read.
"""
from copy import deepcopy
from hashlib import sha256
import json
from unittest.mock import patch

import audit_bf_7star_typed_evolution_preflight_v21500 as audit

base_source = json.loads(audit.SOURCE.read_text("utf8"))
base_manifest = json.loads(audit.MANIFEST.read_text("utf8"))
before_source = audit.SOURCE.read_bytes()
before_manifest = audit.MANIFEST.read_bytes()


def expects_message(source, manifest, message):
    try:
        audit.recipe_rows(source, manifest)
    except ValueError as exc:
        assert str(exc) == message, (message, str(exc))
    else:
        raise AssertionError("invalid source accepted: " + message)


def canonical_digest(rows):
    return sha256(json.dumps(
        rows, separators=(",", ":"), ensure_ascii=True
    ).encode()).hexdigest()


def duplicate_form(source_id, duplicate_id, expected_message):
    """Update both manifests + source SHA so only six-element identity rejects."""
    src, manifest = deepcopy(base_source), deepcopy(base_manifest)
    rows = src["rows"]
    ids = [row[0] for row in rows]
    missing_index = ids.index(source_id)
    copied_index = ids.index(duplicate_id)
    rows[missing_index] = deepcopy(rows[copied_index])
    manifest["rows"][missing_index] = deepcopy(manifest["rows"][copied_index])
    new_checksum = canonical_digest(rows)
    src["typedRowsSha256"] = new_checksum
    assert new_checksum != audit.ROWS_SHA
    assert all(
        r[0] == m["unitId"] for r, m in zip(src["rows"], manifest["rows"])
    ), "mutated manifests must still agree"
    with patch.object(audit, "ROWS_SHA", new_checksum):
        expects_message(src, manifest, expected_message)


# With source hash and two-manifest join artificially satisfied, the remaining
# six-element completeness guards MUST independently reject both missing forms.
duplicate_form(60016, 50016, "incomplete six starter 7-star set")
duplicate_form(60017, 50017, "incomplete six starter 8-star set")

# Verify precise guard outcomes so any unrelated ValueError no longer suffices.
modified_source, modified_manifest = deepcopy(base_source), deepcopy(base_manifest)
modified_source["rows"][0][7][0][2] += 1
modified_manifest["rows"][0]["originalEvo"]["materialSlots"][0]["id"] += 1
assert all(
    r[0] == m["unitId"] for r, m in zip(
        modified_source["rows"], modified_manifest["rows"]
    )
)
expects_message(modified_source, modified_manifest,
                "source recipe checksum mismatch")

# Shape/type guard failure reasons are normalized, not accidental AttributeError.
for bad in (None, [], "bad", 42):
    malformed = deepcopy(base_manifest)
    malformed["rows"][0] = bad
    expects_message(base_source, malformed, "malformed source form")
for bad in (None, [], "bad"):
    malformed = deepcopy(base_manifest)
    malformed["rows"][0]["originalEvo"] = bad
    expects_message(base_source, malformed, "malformed original evolution source")
for bad in (None, {}, "bad", [None]):
    malformed = deepcopy(base_manifest)
    malformed["rows"][0]["originalEvo"]["materialSlots"] = bad
    expected = ("malformed source material record" if bad == [None]
                else "malformed original evolution source")
    expects_message(base_source, malformed, expected)

malformed_source = deepcopy(base_source)
malformed_source["rows"][0] = None
expects_message(malformed_source, base_manifest, "malformed source recipe row")

# Python-only callers can send objects not representable in JSON. Normalize
# their errors as ValueError before checksum verification.
malformed_source = deepcopy(base_source)
malformed_source["rows"][0][7][0][2] = {123}
expects_message(malformed_source, base_manifest,
                "source recipe rows are not JSON-serializable")

# Positive source rows and synthetic no-evolution gates are unchanged.
rows = audit.recipe_rows()
assert [r[0] for r in rows] == [
    10016, 10017, 20016, 20017, 30016, 30017,
    40016, 40017, 50016, 50017, 60016, 60017
]
for target, prev, rarity, cost, level, zel, karma, slots in rows:
    fake_units = {
        item_id: sum(x[2] == item_id and x[1] == 1 for x in slots)
        for slot, kind, item_id in slots if kind == 1
    }
    report = audit.preflight(target, {prev}, fake_units, {110100: 1},
                             zel, karma)
    assert report["syntheticResourceCoverage"] is True
    assert report["original2022EvolutionAuthorized"] is False
    assert report["changesPlayability"] is False
    assert report["readsOrWritesPlayerSaves"] is False
assert audit.SOURCE.read_bytes() == before_source
assert audit.MANIFEST.read_bytes() == before_manifest
print("PASS v217: 7/8-star six-element guard isolation, exact corruption reasons and no live evolution")
