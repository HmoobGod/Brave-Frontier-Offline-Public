"""v118: fail-closed 2022 Global EXP pattern/type metadata provenance.

This checks *identifiers and raw ranges only*, not EXP thresholds, native type
assignment, level-up RNG, rounding, or live combat behavior.
"""
from collections import Counter
from decimal import Decimal
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
catalog = json.loads((ROOT / "source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json").read_text("utf8"))
caps = json.loads((ROOT / "source_data/bf_global_2022_playable_level_caps_v115.json").read_text("utf8"))
assert catalog["schema"] == "bf-global-2022-playable-lord-stat-endpoints-v116"
assert catalog["source"]["archiveSha256"] == "69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
assert catalog["source"]["typeMaster"]["sha256"] == "69cc9a357b1915d31f852346e144fd6b4a0e61c9d7d64e0ac9c1a60297a10301"
rows = {r["unitId"]: r for r in catalog["rows"]}
assert len(rows) == len(catalog["rows"]) == catalog["unitCount"] == 72
expected = {}
for element in range(1, 7):
    base = element * 10000
    expected.update({base + x: 10 for x in [11, 12, 13, 14, 15, 41, 42]})
    expected.update({base + x: 15 for x in [21, 22, 23, 24]})
    expected[base + 25] = 20
assert set(rows) == set(expected), (sorted(set(expected)-set(rows)), sorted(set(rows)-set(expected)))
assert all(rows[uid]["expPatternId"] == pattern for uid, pattern in expected.items())
assert dict(Counter(r["expPatternId"] for r in rows.values())) == {10: 42, 15: 24, 20: 6}
for e in range(1, 7):
    for offset in range(5):
        assert rows[e*10000 + 11+offset]["maxLevel"] == caps["firstStarterCapByElement"][str(e)][offset]
        assert rows[e*10000 + 21+offset]["maxLevel"] == caps["secondStarterCap"][offset]
    for offset in range(2):
        assert rows[e*10000 + 41+offset]["maxLevel"] == caps["alternateCap"][offset]
# Compare exact archived raw fields, never converting them into fabricated bonuses.
expected_types = [
    ("0,0", "0,0", "0,0", "0,0", "23.00", "1.00"),
    ("5,10", "0,0", "0,0", "-3,-1", "23.00", "2.00"),
    ("0,0", "1,3", "-3,-1", "0,0", "22.00", "1.00"),
    ("0,0", "0,0", "1,3", "-2,0", "22.00", "1.00"),
    ("0,0", "0,0", "-2,0", "2,4", "10.00", "0.50"),
    ("10,15", "1,2", "1,2", "1,2", "0.00", "0.75"),
]
fields = ("unitTypeHpRaw", "unitTypeAtkRaw", "unitTypeDefRaw", "unitTypeRecRaw", "unitTypeChanceRaw", "unknownRaw")
types = catalog["unitTypeRaw"]
assert catalog["rawUnitTypeCount"] == len(types) == 6
assert [t["unitTypeId"] for t in types] == [1, 2, 3, 4, 5, 6]
assert [tuple(t[k] for k in fields) for t in types] == expected_types
assert sum(Decimal(t["unitTypeChanceRaw"]) for t in types) == Decimal("100.00")
assert types[5]["unitTypeChanceRaw"] == "0.00" # Rex is NOT a normal-acquisition random roll.
# Safety gate remains explicit: no unverified native midlevel solver or saved XP rewrite.
reference = (ROOT / "app/src/main/assets/bf11600_original_lord_stats_reference.js").read_text("utf8")
assert "nativeMidlevelGrowthVerified:false" in reference
assert not any(x in reference for x in ("P.unitExp=", "P.version=", "P.roster=", "Math.random"))
print("PASS v118 72/72 archival EXP pattern IDs (10/15/20: 42/24/6), six exact raw type records, unchanged native growth safety boundary")
