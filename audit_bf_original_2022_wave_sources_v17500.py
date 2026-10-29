"""v175: offline, source-gated candidate inventory for original 2022 wave joins.

This does NOT decode original enemy IDs or prove a formation/AI/loot table.
It reports only exact string re-use of the 2022 opaque mission field across
other ORIGINAL 2022 master files. Nothing is extracted, uploaded, or mutated.

Usage (owner-provided local file, never committed to public GitHub):
  python audit_bf_original_2022_wave_sources_v17500.py --archive mst-decoded.zip
  python audit_bf_original_2022_wave_sources_v17500.py --archive mst-decoded.zip --output audit.json
"""
from pathlib import Path
from collections import defaultdict
import argparse,base64,gzip,hashlib,json,re,zipfile

ZIP_SHA="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
MISSION_SHA="d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
CROSS_PACK_SHA="cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a"
CROSS_ROWS_SHA="2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284"
ORIGINAL_MISSION="3-mst-translated/F_MISSION_MST_1_Ver1118.json"
OPAQUE="MISSION_8f4NYKxb"
MAX_TABLE_BYTES=80_000_000
sha=lambda b:hashlib.sha256(b).hexdigest()

def pinned_refs(root):
    """Read the existing, separately audited v152 reference fixture."""
    p=Path(root)/"source_data/bf_global_2022_mission_cross_table_v152.json.gz.b64"
    compressed=base64.b64decode(p.read_text("ascii").strip(),validate=True)
    if sha(compressed)!=CROSS_PACK_SHA:raise ValueError("wrong 2022 cross-table fixture")
    data=json.loads(gzip.decompress(compressed))
    rows=data["rows"]
    if data["canonicalRowsSha256"]!=CROSS_ROWS_SHA or len(rows)!=142:
        raise ValueError("wrong source cross-table version")
    if sha(json.dumps(rows,ensure_ascii=False,separators=(",",":")).encode())!=CROSS_ROWS_SHA:
        raise ValueError("2022 cross-table rows changed")
    return {row[0]:row[1] for row in rows}

def scan_tables(z,refs,max_bytes=MAX_TABLE_BYTES,require_primary_sha=True):
    """Return schema-level candidates only, never infer enemy/wave semantics.

    Caller must verify the FULL ZIP SHA before invoking in production.
    Explicitly open only ZIP entries; do not extract paths to disk.
    """
    if not refs or len(set(refs))!=len(refs):
        raise ValueError("source mission set missing")
    by_opaque=defaultdict(set)
    for id,raw in refs.items():
        if type(id) is not int or not re.fullmatch(r"\d+:\d+(?:,\d+:\d+)*",raw):
            raise ValueError("invalid original mission identity/reference")
        by_opaque[raw].add(id)
    if len(refs)==142 and set(refs)==set(range(142)):
        raise ValueError("unexpected synthetic identity block")
    if ORIGINAL_MISSION not in z.namelist():
        raise ValueError("original 2022 mission master absent")
    meta=z.getinfo(ORIGINAL_MISSION)
    if meta.file_size>max_bytes:raise ValueError("mission master exceeds safety limit")
    original_bytes=z.read(ORIGINAL_MISSION)
    if require_primary_sha and sha(original_bytes)!=MISSION_SHA:
        raise ValueError("original 2022 mission master SHA mismatch")
    original=json.loads(original_bytes)
    if not isinstance(original,list):raise ValueError("mission master is not a list")
    missions={}
    for row in original:
        if not isinstance(row,dict):continue
        mid=row.get("missionId")
        if not isinstance(mid,str) or not mid.isdigit():continue
        key=int(mid)
        if key in missions:raise ValueError("duplicate source missionId")
        missions[key]=row.get(OPAQUE)
    for id,raw in refs.items():
        if missions.get(id)!=raw:raise ValueError("original 2022 mission cross-table mismatch")
    findings=[];skipped=[]
    for entry in sorted(z.infolist(),key=lambda a:a.filename):
        name=entry.filename
        if name==ORIGINAL_MISSION or not name.startswith("3-mst-translated/") or not name.endswith(".json"):
            continue
        # An archive may contain arbitrary JSON, but only named original master
        # tables are inspected. Do not silently classify other data as native.
        if not name.split("/")[-1].startswith("F_"):continue
        if entry.file_size>max_bytes:
            skipped.append({"table":name.split("/")[-1],"reason":"oversized"})
            continue
        try:
            table=json.loads(z.read(entry))
        except (ValueError,UnicodeDecodeError) as exc:
            skipped.append({"table":name.split("/")[-1],"reason":"invalid json"})
            continue
        if not isinstance(table,list):
            skipped.append({"table":name.split("/")[-1],"reason":"not row array"})
            continue
        fields=defaultdict(set);exact_rows=defaultdict(int)
        for obj in table:
            if not isinstance(obj,dict):continue
            for field,value in obj.items():
                # Exact full opaque text only; integers, substring matches,
                # first-token suffixes and numeric IDs are NOT native joins.
                if not isinstance(value,str) or value not in by_opaque:continue
                fields[field].update(by_opaque[value])
                exact_rows[field]+=1
        if fields:
            for field,matched in sorted(fields.items()):
                findings.append({"table":name.split("/")[-1],"field":field,
                    "matchedMissionIds":len(matched),"matchingTableRows":exact_rows[field],
                    "nativeFormationDecoded":False,"nativeEnemyIdsDecoded":False,
                    "nativeAIDecoded":False,"nativeDropsDecoded":False})
    findings.sort(key=lambda x:(-x["matchedMissionIds"],x["table"],x["field"]))
    return {"schema":"bf-global-original-2022-wave-join-candidates-v175",
        "scope":"exact string matches in original source tables, not formations",
        "sourceMissionMasterSha256":MISSION_SHA if require_primary_sha else "synthetic-fixture-only",
        "sourceMissionCount":len(refs),"candidateFields":findings,
        "skippedTables":skipped,"nativeFormationDecoded":False,
        "nativeEnemyIdsDecoded":False,"nativeAIDecoded":False,
        "nativeDropsDecoded":False,"gameplayMutation":False,
        "saveMutation":False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path,required=True)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if sha(args.archive.read_bytes())!=ZIP_SHA:
        raise SystemExit("Archive SHA mismatch: only the exact owner-verified 2022 MST is accepted")
    root=Path(__file__).resolve().parent
    with zipfile.ZipFile(args.archive) as z:
        report=scan_tables(z,pinned_refs(root))
    formatted=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(formatted,"utf8")
        print("Source-only audit report written:",args.output)
    else:
        print(formatted,end="")
if __name__=="__main__":
    main()
