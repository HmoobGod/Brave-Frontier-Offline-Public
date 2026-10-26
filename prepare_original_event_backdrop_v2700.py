"""Stage the exact source 2022 Cave of Flames event backdrop into the offline APK.

This JPEG is the exact original source asset from user's BF1_dungeon_part001.zip.
Only copy if SHA-256 and size match. Do not modify other battle backgrounds.
"""
from pathlib import Path
from hashlib import sha256
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source_assets/bf1/dungeon/dungeon_battle_10200.jpg'
DEST=ROOT/'app/src/main/assets/content/dungeon/dungeon_battle_10200.jpg'
EXPECTED='50b7833e5045b5ffbf23056d33ee13d1e96654e9665e6b4d770fe6f8baef473b'
data=SOURCE.read_bytes()
assert len(data)==36820,('original jpeg length mismatch',len(data))
assert sha256(data).hexdigest()==EXPECTED,'original source JPEG SHA-256 mismatch'
assert data[:2]==b'\xff\xd8' and data[-2:]==b'\xff\xd9','invalid original jpeg'
DEST.parent.mkdir(parents=True,exist_ok=True)
if not DEST.exists() or DEST.read_bytes()!=data:
    DEST.write_bytes(data)
assert DEST.read_bytes()==data
print('PASS v27.00 original dungeon_battle_10200.jpg staged byte-identical')
