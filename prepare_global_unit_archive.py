"""Stage archive-verified 2022 Global unit catalog and original thumbnails.

Reads checked-in base64 + gzip/ZIP payloads, not live Drive/network content.
Does not change player units, combat, summons, saves, or script execution.
Idempotently embeds JSON in generated index.html to avoid Android file:// CORS.
"""
from __future__ import annotations
import base64,gzip,hashlib,html,json,re,zipfile,io
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
DATA=ROOT/'source_data'
PACK=ROOT/'source_assets/bf1'
META=json.loads((DATA/'bf_global_original_unit_catalog_meta.json').read_text('utf-8'))
assert META['schema']=='bf-global-unit-archive-package-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()

def decode_b64(path):
    raw=path.read_text('ascii')
    assert re.fullmatch(r'[A-Za-z0-9+/=\s]+',raw)
    return base64.b64decode(raw,validate=False)

compressed=decode_b64(DATA/'bf_global_original_unit_catalog.json.gz.b64')
assert sha(compressed)==META['catalogGzipSha256']
raw=gzip.decompress(compressed)
assert sha(raw)==META['catalogJsonSha256'] and len(raw)==META['catalogJsonBytes']
archive=json.loads(raw)
assert archive['schema']=='bf-global-unit-archive-2022-v1'
assert len(archive['units'])==META['catalogRecordCount']==2291
ids={row['id'] for row in archive['units']}
assert len(ids)==2291
assert all(set(row['evo']).issubset(ids) for row in archive['units'])
thumb_ids={row['id'] for row in archive['units'] if row['thumbnail']}
assert len(thumb_ids)==META['thumbnailCount']
assert archive['provenance']['curatedThumbsSha256']==META['thumbnailZipSha256']
assert archive['provenance']['thumbnailArchiveSha256']==META['sourceArchiveSha256']

zbytes=decode_b64(PACK/'BF1_Global_2022_Unit_Archive_Thumbs_Curated.zip.b64')
assert sha(zbytes)==META['thumbnailZipSha256']
with zipfile.ZipFile(io.BytesIO(zbytes)) as source:
    actual=source.namelist()
    expected=[f'content/unit_archive/unit_ills_thum_{i}.png' for i in sorted(thumb_ids)]
    assert sorted(actual)==sorted(expected),(len(actual),len(expected))
    for item in actual:
        png=source.read(item)
        assert png.startswith(b'\x89PNG\r\n\x1a\n'),item
        target=ASSETS/item
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==png,item
        else:target.write_bytes(png)

# JSON is data-only, not executable code. Escape dangerous HTML characters
# and restore with textContent in the separate archive renderer.
json_payload=raw.decode('utf-8').replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
script='<script type="application/json" id="bf-global-unit-catalog-data">'+json_payload+'</script>'
start='<!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->'
end='<!-- BF_GLOBAL_UNIT_ARCHIVE_END -->'
block=start+script+end
index=ASSETS/'index.html'
s=index.read_text('utf-8')
if start in s or end in s:
    assert s.count(start)==1 and s.count(end)==1
    assert block in s,'Existing unit catalog payload is not source-identical'
else:
    assert s.count('</body>')==1
    s=s.replace('</body>',block+'</body>',1)
    index.write_text(s,'utf-8')
assert s.count('id="bf-global-unit-catalog-data"')==1
print(f'PASS 2022 original Global archive: {len(ids)} unit/form records, {len(thumb_ids)} original PNG thumbnails; index staged once')
