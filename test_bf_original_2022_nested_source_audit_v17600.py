"""v176: synthetic nested candidate tests; never publish private 2022 master rows."""
import io
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import audit_bf_original_2022_nested_sources_v17600 as nested
import audit_bf_original_2022_wave_sources_v17500 as base

ROOT = Path(__file__).resolve().parent
original = base.pinned_refs(ROOT)
assert len(original) == 142
a = original[1]
b = original[400]
assert b == original[404]
sample = {1: a, 400: b, 404: b}
primary = [{"missionId": str(k), base.OPAQUE: v} for k, v in sample.items()]

def fake_zip(missions=None, other=None):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(base.ORIGINAL_MISSION, json.dumps(primary if missions is None else missions))
        tables = other if other is not None else {
            "F_NESTED_MST_Ver1.json": [
                {"nested": {"sets": [{"ref": a}, {"ref": b}, {"ref": b}]},
                 "topLevel": a, "numeric": 50100},
                {"nested": {"sets": [{"ref": b}]},
                 "substring": "3:50100", "joined": "prefix:" + a},
                {"nested": {"sets": [{"ref": "3:99999"}]}}
            ],
            "F_SECOND_MST_Ver1.json": [{"outer": {"ref": a}, "values": [{"token": b}]}],
            "F_SCALAR_ONLY_MST_Ver1.json": [{"ref": a}, {"ref": b}],
            "F_INVALID_MST_Ver1.json": "not-valid-json",
            "NOT_AN_ORIGINAL_TABLE.json": [{"fake": {"ref": a}}]
        }
        for name, rows in tables.items():
            text = rows if name == "F_INVALID_MST_Ver1.json" else json.dumps(rows)
            z.writestr("3-mst-translated/" + name, text)
    out.seek(0)
    return zipfile.ZipFile(out)

with fake_zip() as z:
    report = nested.scan_nested(z, sample, require_primary_sha=False)
    assert report["sourceMissionCount"] == 3
    assert report["sourceMissionMasterSha256"] == "synthetic-fixture-only"
    assert report["topLevelCandidateFieldCount"] == 2
    assert {key: report[key] for key in
            ("nativeFormationDecoded", "nativeEnemyIdsDecoded", "nativeAIDecoded",
             "nativeDropsDecoded", "gameplayMutation", "saveMutation")} == {
             "nativeFormationDecoded": False, "nativeEnemyIdsDecoded": False,
             "nativeAIDecoded": False, "nativeDropsDecoded": False,
             "gameplayMutation": False, "saveMutation": False}
    paths = {(r["table"], r["path"]): r for r in report["nestedCandidatePaths"]}
    assert len(paths) == 3, paths
    combined = paths[("F_NESTED_MST_Ver1.json", "/nested/sets/[]/ref")]
    assert combined["matchedMissionIds"] == 3
    assert combined["matchingTableRows"] == 2  # repeated array members count once per row
    assert paths[("F_SECOND_MST_Ver1.json", "/outer/ref")]["matchedMissionIds"] == 1
    assert paths[("F_SECOND_MST_Ver1.json", "/values/[]/token")]["matchedMissionIds"] == 2
    assert all(row["nativeFormationDecoded"] is False for row in paths.values())
    assert report["skippedTables"] == [
        {"table": "F_INVALID_MST_Ver1.json", "reason": "invalid-json"}]
    try:
        nested.scan_nested(z, sample, require_primary_sha=True)
        assert False, "synthetic source incorrectly accepted as original"
    except ValueError as error:
        assert "SHA mismatch" in str(error)
    for override in ({"max_nodes": 3}, {"max_depth": 2}):
        reduced = nested.scan_nested(z, sample, require_primary_sha=False, **override)
        assert not any(r["table"] == "F_NESTED_MST_Ver1.json"
                       for r in reduced["nestedCandidatePaths"])
        assert any(r["table"] == "F_NESTED_MST_Ver1.json"
                   and "limit" in r["reason"] for r in reduced["skippedTables"])

assert nested.printable_path(("odd/name", "key~value", "[]")) == "/odd~1name/key~0value/[]"

with fake_zip(missions=primary[:-1]) as z:
    try:
        nested.scan_nested(z, sample, require_primary_sha=False)
        assert False, "missing original mission unexpectedly allowed"
    except ValueError as error:
        assert "mismatch" in str(error)

with tempfile.TemporaryDirectory() as tmp:
    fake = Path(tmp) / "unverified-source.zip"
    with fake_zip() as z:
        fake.write_bytes(z.fp.getbuffer())
    report_file = Path(tmp) / "should-not-exist.json"
    result = subprocess.run([sys.executable, str(ROOT / "audit_bf_original_2022_nested_sources_v17600.py"),
                             "--archive", str(fake), "--output", str(report_file)],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert "Archive SHA mismatch" in (result.stderr + result.stdout)
    assert not report_file.exists()
print("PASS v176: bounded nested exact-source matches, ambiguous repeat counts, source SHA refusal, honest native flags, no output on failure")
