"""Byte-exact recovered 2022 original event illustrations and frame mapping.

The immutable curated ZIP contains source event PNGs and an extracted 2022
script-to-expression index. It is not a combat or save patch. Idempotent.
"""
import json,hashlib,zipfile,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ZIP=ROOT/'source_assets/bf1/event/BF1_Global_Original_Event_Expressions_2022_v2900.zip'
TARGET=ROOT/'app/src/main/assets/content/event'
JS=ROOT/'app/src/main/assets/bf2900_original_event_expressions.js'
EXPECTED='fe080b2b7255786b6d835dbe0d03cc07cf763ebb424e784d3d5ab41522e43c95'
SOURCE='0d6e5882aacf458740e99cc41c31bb930a1c757672fb02e0e49306dbe9a7cb8a'
raw=ZIP.read_bytes()
assert hashlib.sha256(raw).hexdigest()==EXPECTED,'curated 2022 ZIP SHA-256 mismatch'
with zipfile.ZipFile(ZIP) as archive:
    assert archive.testzip() is None
    manifest=json.loads(archive.read('EXPRESSIONS_MANIFEST.json'))
    assert manifest['schema']=='bf-global-2022-event-expressions-v2900'
    assert manifest['sourceSha256']==SOURCE
    assert manifest['scenes']==20 and manifest['frames']==405
    assert len(manifest['rows'])==20 and len(manifest['files'])==19
    assert set(archive.namelist())=={'EXPRESSIONS_MANIFEST.json'}|{
      'content/event/'+k for k in manifest['files']}
    for name,meta in manifest['files'].items():
        assert re.fullmatch(r'navi_chara[123]_[0-9]\.png',name),name
        picture=archive.read('content/event/'+name)
        assert len(picture)==meta['length']
        assert hashlib.sha256(picture).hexdigest()==meta['sha256'],name
        assert picture[:8]==b'\x89PNG\r\n\x1a\n',name
        TARGET.mkdir(parents=True,exist_ok=True)
        path=TARGET/name
        if not path.exists() or path.read_bytes()!=picture:
            path.write_bytes(picture)
    total=0
    for name,sequence in manifest['rows'].items():
        assert re.fullmatch(r'map[123]-dungeon[1-7]\.txt',name)
        assert len(sequence)%2==0 and re.fullmatch(r'(?:[123][0-9])+',sequence)
        for i in range(0,len(sequence),2):
            filename='navi_chara'+sequence[i]+'_'+sequence[i+1]+'.png'
            assert filename in manifest['files'],(name,filename)
            total+=1
    assert total==405
data={'schema':'bf-global-original-expression-frames-v2900','rows':manifest['rows'],
      'scenes':20,'frames':405,'sprites':19,'files':sorted(manifest['files'])}
encoded='const DATA='+json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False)+';'
template='const DATA=/* BF2900_DATA_PLACEHOLDER */null;'
source=JS.read_text('utf8')
if template in source:
    source=source.replace(template,encoded,1)
    JS.write_text(source,encoding='utf8')
else:
    assert encoded in source,'existing expression module differs from signed source index'
assert len(JS.read_bytes())<65536,'Android injected script over size limit'
print('PASS v29.00 19 exact 2022 facial expressions, 20 source scripts, 405 frame matches')
