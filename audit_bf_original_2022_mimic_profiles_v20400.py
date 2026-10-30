"""v204: source-authenticated, read-only 2022 original mission mimic profile audit.

Production reads only a local owner archive whose FULL ZIP SHA256 matches the
pinned 2022 source. No unredacted source rows or mission-level values leave
this program. Profile strings are kept opaque: no inferred mimic probabilities,
foe identity, drop rates or playable encounters.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import re
import zipfile

from audit_bf_original_2022_wave_sources_v17500 import (
    ZIP_SHA, MISSION_SHA, ORIGINAL_MISSION, pinned_refs,
)

AREAS = {"100": "mistral", "200": "morgan", "300": "stlamia",
         "400": "amdahl"}
AREA_COUNTS = {"mistral": 34, "morgan": 36, "stlamia": 36, "amdahl": 36}
RAW_PATTERN = re.compile(r"[0-9]+,[0-9]+,[0-9]+:[0-9]+,[0-9]+:[0-9]+\Z")
MAX_MASTER_BYTES = 80_000_000


def local_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_rows(rows, refs, expected_areas=None):
    """Exact mission/reference joins. Synthetic tests can pass smaller refs."""
    if type(rows) is not list or type(refs) is not dict or not refs:
        raise ValueError("invalid mission master or source reference map")
    chosen = [r for r in rows if type(r) is dict
              and r.get("missionAreaId") in AREAS
              and r.get("missionId") != "90"]
    if len(chosen) != len(refs):
        raise ValueError("source mission count differs from pinned references")
    seen = set()
    distributions = {label: Counter() for label in AREAS.values()}
    all_profiles = Counter()
    for row in chosen:
        mid = row.get("missionId")
        area = row.get("missionAreaId")
        raw_ref = row.get("MISSION_8f4NYKxb")
        raw_mimic = row.get("missionMimicInfo")
        if type(mid) is not str or not mid.isdecimal() or int(mid) in seen:
            raise ValueError("duplicate or invalid original mission id")
        seen.add(int(mid))
        if refs.get(int(mid)) != raw_ref or type(raw_ref) is not str:
            raise ValueError("mission source reference differs from pinned fixture")
        if type(raw_mimic) is not str or not RAW_PATTERN.fullmatch(raw_mimic):
            raise ValueError("unexpected original mission mimic format")
        distributions[AREAS[area]][raw_mimic] += 1
        all_profiles[raw_mimic] += 1
    if seen != set(refs):
        raise ValueError("source mission identity mismatch")
    if expected_areas is not None:
        if {a: sum(distributions[a].values()) for a in AREA_COUNTS} != expected_areas:
            raise ValueError("source area mission count changed")
    return {
        "schema": "bf-global-v204-original-2022-mimic-opaque-profile-audit",
        "sourceArchiveSha256": ZIP_SHA,
        "sourceMissionMasterSha256": MISSION_SHA,
        "sourceMissionCount": len(chosen),
        "sourceAreas": {a: sum(distributions[a].values())
                        for a in AREA_COUNTS},
        "opaqueRawPatternCounts": dict(sorted(all_profiles.items())),
        "opaqueRawPatternCountsByArea": {
            a: dict(sorted(distributions[a].items())) for a in AREA_COUNTS
        },
        "distinctOpaquePatterns": len(all_profiles),
        "unverifiedSingleOccurrencePatterns": sorted(
            value for value, count in all_profiles.items() if count == 1),
        "interpretsRawTokensAsProbabilities": False,
        "originalMimicEnemyIdsVerified": False,
        "originalMimicEncounterTriggerVerified": False,
        "originalMimicRewardsAndDropsVerified": False,
        "changesGame": False,
        "changesSaves": False,
    }


def source_scan(archive_path, root=Path(__file__).resolve().parent):
    if local_sha256(archive_path) != ZIP_SHA:
        raise ValueError("original 2022 ZIP SHA-256 mismatch")
    with zipfile.ZipFile(archive_path) as archive:
        member = archive.getinfo(ORIGINAL_MISSION)
        if member.file_size > MAX_MASTER_BYTES:
            raise ValueError("original mission master exceeds safe size")
        payload = archive.read(member)
        if hashlib.sha256(payload).hexdigest() != MISSION_SHA:
            raise ValueError("original 2022 mission master SHA-256 mismatch")
        rows = json.loads(payload)
        return scan_rows(rows, pinned_refs(root), AREA_COUNTS)


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--archive", required=True, type=Path,
                   help="local SHA-pinned original 2022 mst-decoded.zip")
    p.add_argument("--output", type=Path, help="optional local aggregate only")
    args = p.parse_args()
    result = source_scan(args.archive)
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
        print("Read-only opaque mimic aggregate saved:", args.output)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
