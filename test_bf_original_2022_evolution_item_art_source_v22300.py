"""v223 source-only original PNG bundle integrity, zero gameplay/saves."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import zipfile
import prepare_bf_original_2022_evolution_item_art_v22300 as source

cat, rows = source.verified_source()
assert len(rows) == 31 and len([r for r in rows if r[0] != 110100]) == 30
assert sum(r[3] for r in rows) == 333
assert cat['unitMaterialSlotsType1'] == 7107
original=source.PACK.read_bytes()
with TemporaryDirectory() as td:
    bad = Path(td)/'tampered.zip'
    changed=bytearray(original)
    changed[len(changed)//2] ^= 1
    bad.write_bytes(changed)
    try:
        source.verified_source(pack_path=bad)
    except ValueError:
        pass
    else:
        raise AssertionError('tampered original artwork bundle accepted')
assert source.PACK.read_bytes() == original
assert hashlib.sha256(original).hexdigest() == source.PACK_SHA256
print('PASS v223 source: 31 source items, 30 byte-authentic original PNGs, no type-1 mixing, bundle tamper rejected')
