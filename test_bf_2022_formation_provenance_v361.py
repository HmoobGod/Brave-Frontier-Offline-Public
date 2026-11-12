"""Synthetic-only negative acceptance tests. No invented rows enter the game."""
import copy
import hashlib
import json
from bf_2022_formation_provenance_v361 import audit_formations

rows = [[i, i // 5 + 1, i - 1, (i % 3) + 1, 0, 0, 0, 0] for i in range(1, 107)]
formations = [[r[0], wave, r[0] * 10 + wave, "a" * 64]
              for r in rows for wave in range(r[3])]
digest = lambda value: hashlib.sha256(json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
pin = digest(formations)
report = audit_formations(rows, formations, pin)
assert report["missionsChecked"] == 106
assert report["formationSlotsChecked"] == len(formations)
assert report["nativeSpawnsAuthorized"] is False
assert report["sourceRecordsIndependentlyVerified"] is False
assert report["nativeWavesPlayableCertified"] == 0

def rejects(mission_rows, manifest, trusted_pin):
    try:
        audit_formations(mission_rows, manifest, trusted_pin)
    except ValueError:
        return
    raise AssertionError("unsafe manifest accepted")

rejects(rows, formations, None)
rejects(rows, formations, "0" * 64)
rejects(rows[:-1], formations, pin)
rejects(rows, formations[:-1], pin)
bad = copy.deepcopy(formations)
bad[0][2] += 1
rejects(rows, bad, pin)
bad = copy.deepcopy(formations)
bad[0][3] = "b" * 64
rejects(rows, bad, pin)
bad = copy.deepcopy(formations)
bad[0][3] = "self-reported"
rejects(rows, bad, digest(bad))
bad = copy.deepcopy(formations)
bad[0][2] = True
rejects(rows, bad, digest(bad))
bad = copy.deepcopy(formations)
bad[0], bad[1] = bad[1], bad[0]
rejects(rows, bad, digest(bad))
bad_rows = copy.deepcopy(rows)
bad_rows[1][0] = bad_rows[0][0]
rejects(bad_rows, formations, pin)
bad_rows = copy.deepcopy(rows)
bad_rows[0][3] += 1
rejects(bad_rows, formations, pin)
# A digest matching the candidate is insufficient without a trusted external pin.
# The positive fixture's pin is synthetic; never treat it as a 2022 source root.
print("PASS: 106-mission synthetic formation coverage and negative provenance gates")
