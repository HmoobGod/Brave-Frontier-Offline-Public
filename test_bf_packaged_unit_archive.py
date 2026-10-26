"""Post-build verification: authentic unit encyclopedia data and images in APK."""
import base64,gzip,hashlib,io,json,re,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
META=json.loads((ROOT/'source_data/bf_global_original_unit_catalog_meta.json').read_text('utf-8'))
APK=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert APK.is_file(),f'Missing compiled Android APK: {APK}'
raw=gzip.decompress(base64.b64decode((ROOT/'source_data/bf_global_original_unit_catalog.json.gz.b64').read_text()))
assert hashlib.sha256(raw).hexdigest()==META['catalogJsonSha256']
thumb_zip=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Unit_Archive_Thumbs_Curated.zip.b64').read_text())
assert hashlib.sha256(thumb_zip).hexdigest()==META['thumbnailZipSha256']
with zipfile.ZipFile(APK) as apk,zipfile.ZipFile(io.BytesIO(thumb_zip)) as thumbs:
    names=set(apk.namelist())
    assert 'assets/bf_global_unit_archive.js' in names
    assert 'assets/bf_global_unit_archive.css' in names
    html=apk.read('assets/index.html').decode('utf-8')
    found=re.search(r'<script type="application/json" id="bf-global-unit-catalog-data">(.*?)</script>',html,re.DOTALL)
    assert found,'Missing original Global encyclopedia payload in compiled APK'
    data=json.loads(found.group(1))
    assert len(data['units'])==META['catalogRecordCount']==2291
    assert data['stats']['thumbnailCount']==META['thumbnailCount']==127
    ids={u['id'] for u in data['units']}
    assert len(ids)==2291
    for asset in thumbs.namelist():
        packaged='assets/'+asset
        assert packaged in names,packaged
        assert apk.read(packaged)==thumbs.read(asset),f'Changed original PNG bytes: {packaged}'
    assert len(thumbs.namelist())==127
print('PASS final compiled APK contains all 2,291 authentic unit/form records and 127 byte-identical original Global PNGs')
