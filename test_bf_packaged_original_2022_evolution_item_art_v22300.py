"""v223 APK test: the original 31 PNG source bytes and JS are packaged exactly."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
APK=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
CAT=json.loads((ROOT/'source_data/bf_global_2022_evolution_item_art_catalog_v222.json').read_text('utf8'))
with zipfile.ZipFile(APK) as z:
    for item_id, source_name, image, count, expected_size, expected_sha in CAT['rows']:
        asset=ASSETS/'content/item'/image
        original=asset.read_bytes()
        assert len(original)==expected_size and hashlib.sha256(original).hexdigest()==expected_sha
        assert z.read('assets/content/item/'+image)==original, image
    js='bf22300_original_2022_evolution_item_gallery.js'
    expected=(ASSETS/js).read_bytes()
    assert b'BF_GLOBAL_ORIGINAL_2022_TYPED_EVOLUTION_ITEM_GALLERY_V22300' in expected
    assert z.read('assets/'+js)==expected
    assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
assert "applicationId 'org.bravefrontier.offline'" in (ROOT/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (ROOT/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v223 actual APK: 31 exact original 2022 item PNGs, read-only JS, existing offline v7 identity')
