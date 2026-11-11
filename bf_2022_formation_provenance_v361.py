"""Read-only preflight for future original-2022 enemy formation imports.

No historical formation records are bundled here. A caller MUST supply a trusted,
independently pinned SHA-256 for the complete formation manifest. Neither a
manifest's self-reported digest nor an unpinned caller input proves provenance.
No runtime spawn, save, reward, or enemy AI operations are implemented.
"""
import hashlib
import json
import re

SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _number(value, minimum=0):
    return type(value) is int and minimum <= value <= 2**53 - 1


def audit_formations(mission_rows, formations, trusted_manifest_sha256):
    """Return a read-only acceptance report or fail closed.

    mission_rows: trusted 2022 tuples [missionId, ..., missionBattleCount, ...]
    formations: ordered [missionId, waveIndex, formationId, sourceRecordSha256]
    trusted_manifest_sha256: digest pinned OUTSIDE the candidate manifest.
    The caller must independently authenticate mission_rows before invoking.
    """
    if not isinstance(trusted_manifest_sha256, str) or not SHA256.fullmatch(trusted_manifest_sha256):
        raise ValueError("missing independently pinned formation digest")
    if not isinstance(mission_rows, list) or len(mission_rows) != 106:
        raise ValueError("unverified mission coverage")
    counts = {}
    for row in mission_rows:
        if not isinstance(row, (list, tuple)) or len(row) != 8:
            raise ValueError("invalid mission tuple")
        mission_id, waves = row[0], row[3]
        if not _number(mission_id, 1) or not _number(waves, 1) or mission_id in counts:
            raise ValueError("invalid mission or wave count")
        counts[mission_id] = waves
    if not isinstance(formations, list) or len(formations) != sum(counts.values()):
        raise ValueError("incomplete formation coverage")
    expected = [(mission, wave) for mission, count in counts.items() for wave in range(count)]
    normalized = []
    for row, (mission, wave) in zip(formations, expected):
        if not isinstance(row, list) or len(row) != 4:
            raise ValueError("invalid formation row")
        mid, index, formation_id, record_sha = row
        if mid != mission or index != wave or not _number(mid, 1) or not _number(index) or not _number(formation_id, 1):
            raise ValueError("missing, reordered, or invented formation slot")
        if not isinstance(record_sha, str) or not SHA256.fullmatch(record_sha):
            raise ValueError("formation source record digest absent")
        normalized.append(row)
    digest = hashlib.sha256(json.dumps(normalized, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    if digest != trusted_manifest_sha256:
        raise ValueError("formation manifest does not match external pin")
    return {
        "readOnly": True,
        "missionsChecked": 106,
        "formationSlotsChecked": len(normalized),
        "manifestSha256": digest,
        "sourceRecordsIndependentlyVerified": False,
        "nativeSpawnsAuthorized": False,
        "nativeWavesPlayableCertified": 0,
    }
