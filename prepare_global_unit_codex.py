"""Pack verified 2022 Global unit histories/skill text/evolution recipes into offline HTML.

Only publishes read-only text. Does not touch state/units/summons/skill formulas.
All data originates in mst-decoded.zip and BF1_sgtext_part001.zip; JSON SHA is asserted.
"""
import base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
META=json.loads((ROOT/'source_data/bf_global_original_lore_meta.json').read_text('utf-8'))
assert META['schema']=='bf-global-original-lore-package-v1'
compressed=base64.b64decode((ROOT/'source_data/bf_global_original_lore_codex.json.gz.b64').read_text('ascii'),validate=False)
assert hashlib.sha256(compressed).hexdigest()==META['payloadGzipSha256']
raw=gzip.decompress(compressed)
assert len(raw)==META['jsonBytes'] and hashlib.sha256(raw).hexdigest()==META['payloadJsonSha256']
source=json.loads(raw)
assert source['schema']=='bf-global-original-lore-codex-v1'
assert len(source['units'])==META['payloadRecordCount']==2291
assert len({int(r['id']) for r in source['units']})==2291
assert source['provenance']['mstZipSha256']==META['mstZipSha256']
assert source['provenance']['englishTextZipSha256']==META['englishTextZipSha256']
assert source['stats']['rows']==2291
assert all(source['stats'][k]==v for k,v in META['stats'].items())
htmlpath=ROOT/'app/src/main/assets/index.html'
html=htmlpath.read_text('utf-8')
# Encode markup as JSON unicode escapes before embedding in non-executing script.
data=raw.decode('utf-8').replace('&',r'\u0026').replace('<',r'\u003c').replace('>',r'\u003e')
marker1='<!-- BF_GLOBAL_UNIT_LORE_BEGIN -->';marker2='<!-- BF_GLOBAL_UNIT_LORE_END -->'
block=marker1+'<script type="application/json" id="bf-original-unit-lore-data">'+data+'</script>'+marker2
if marker1 in html or marker2 in html:
    assert html.count(marker1)==1 and html.count(marker2)==1
    assert block in html,'Existing codex payload is not hash-identical; refusing overwrite'
else:
    assert html.count('</body>')==1
    html=html.replace('</body>',block+'</body>',1)
    htmlpath.write_text(html,'utf-8')
assert html.count('id="bf-original-unit-lore-data"')==1
print('PASS original Global 2022 lore codex: 2,291 rows, ' +
    f"{source['stats']['story']} source histories, {source['stats']['bb']} BB skill records, " +
    f"{source['stats']['recipes']} verified evolution recipes; idempotent")
