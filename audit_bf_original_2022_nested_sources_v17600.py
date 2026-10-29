"""v176: bounded, read-only scan for nested exact 2022 mission reference reuse.

A candidate text match is NOT evidence of a decoded enemy, formation, AI or drop.
Real runs require the exact owner-approved 2022 full ZIP checksum.
"""
from collections import defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

import audit_bf_original_2022_wave_sources_v17500 as base

MAX_NODES_PER_TABLE = 2_000_000
MAX_DEPTH = 8
MAX_FIELD_LENGTH = 160
MAX_REPORT_PATHS = 10_000

class TraversalLimit(ValueError):
    pass

def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()

def nested_strings(node, path=(), depth=0, visits=None, max_nodes=MAX_NODES_PER_TABLE,
                   max_depth=MAX_DEPTH):
    """Yield nested (path-tuple, exact-string) pairs; exclude top-level scalars."""
    if visits is None:
        visits = [0]
    visits[0] += 1
    if visits[0] > max_nodes:
        raise TraversalLimit("node-limit")
    if isinstance(node, str):
        if len(path) >= 2:
            yield path, node
    elif isinstance(node, (dict, list)):
        if depth >= max_depth:
            raise TraversalLimit("depth-limit")
        if isinstance(node, dict):
            for key, val in node.items():
                if not isinstance(key, str) or len(key) > MAX_FIELD_LENGTH:
                    raise TraversalLimit("field-name-limit")
                yield from nested_strings(val, path + (key,), depth + 1,
                                          visits, max_nodes, max_depth)
        else:
            for val in node:
                yield from nested_strings(val, path + ("[]",), depth + 1,
                                          visits, max_nodes, max_depth)

def printable_path(parts):
    # JSON Pointer-style escape; explicit [] represents any array entry.
    return "/" + "/".join(p.replace("~", "~0").replace("/", "~1") for p in parts)

def scan_nested(z, refs, require_primary_sha=True, max_bytes=base.MAX_TABLE_BYTES,
                max_nodes=MAX_NODES_PER_TABLE, max_depth=MAX_DEPTH):
    """Validate the v175 source gate, then enumerate nested exact-string joins.

    Synthetic callers MUST explicitly set require_primary_sha=False. CLI never does.
    The caller of this function must authenticate the full ZIP first for real use.
    """
    checked = base.scan_tables(z, refs, max_bytes=max_bytes,
                               require_primary_sha=require_primary_sha)
    by_raw = defaultdict(set)
    for mission_id, raw in refs.items():
        by_raw[raw].add(mission_id)
    fields = []
    skipped = []
    for entry in sorted(z.infolist(), key=lambda e: e.filename):
        name = entry.filename
        if (name == base.ORIGINAL_MISSION or not name.startswith("3-mst-translated/F_")
                or not name.endswith(".json")):
            continue
        table_name = name.split("/")[-1]
        if entry.file_size > max_bytes:
            skipped.append({"table": table_name, "reason": "oversized"})
            continue
        try:
            rows = json.loads(z.read(entry))
        except (ValueError, UnicodeDecodeError):
            skipped.append({"table": table_name, "reason": "invalid-json"})
            continue
        if not isinstance(rows, list):
            skipped.append({"table": table_name, "reason": "not-row-array"})
            continue
        matches = defaultdict(lambda: {"missions": set(), "rows": 0})
        budget = [0]
        try:
            for row in rows:
                if not isinstance(row, dict):
                    continue
                per_row = defaultdict(set)
                for parts, value in nested_strings(row, visits=budget,
                                                   max_nodes=max_nodes, max_depth=max_depth):
                    if value in by_raw:
                        per_row[parts].update(by_raw[value])
                for parts, missions in per_row.items():
                    matches[parts]["missions"].update(missions)
                    matches[parts]["rows"] += 1
            if len(matches) > MAX_REPORT_PATHS:
                raise TraversalLimit("report-path-limit")
        except TraversalLimit as error:
            skipped.append({"table": table_name, "reason": str(error)})
            continue
        for parts, stats in matches.items():
            fields.append({"table": table_name, "path": printable_path(parts),
                           "matchedMissionIds": len(stats["missions"]),
                           "matchingTableRows": stats["rows"],
                           "nativeFormationDecoded": False,
                           "nativeEnemyIdsDecoded": False,
                           "nativeAIDecoded": False,
                           "nativeDropsDecoded": False})
        if len(fields) > MAX_REPORT_PATHS:
            raise ValueError("total report path safety limit exceeded")
    fields.sort(key=lambda row: (-row["matchedMissionIds"], row["table"], row["path"]))
    return {"schema": "bf-global-original-2022-nested-join-candidates-v176",
            "scope": "nested exact string reuse only, not original enemy waves",
            "sourceMissionMasterSha256": checked["sourceMissionMasterSha256"],
            "sourceMissionCount": checked["sourceMissionCount"],
            "topLevelCandidateFieldCount": len(checked["candidateFields"]),
            "nestedCandidatePaths": fields,
            "skippedTables": skipped,
            "nativeFormationDecoded": False, "nativeEnemyIdsDecoded": False,
            "nativeAIDecoded": False, "nativeDropsDecoded": False,
            "gameplayMutation": False, "saveMutation": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if file_sha256(args.archive) != base.ZIP_SHA:
        raise SystemExit("Archive SHA mismatch: exact owner-verified 2022 ZIP required")
    with zipfile.ZipFile(args.archive) as z:
        report = scan_nested(z, base.pinned_refs(Path(__file__).resolve().parent))
    result = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
        print("Nested source-only report written:", args.output)
    else:
        print(result, end="")

if __name__ == "__main__":
    main()
