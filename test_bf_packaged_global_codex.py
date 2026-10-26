"""Verify final Android APK contains the exact original 2022 Global unit codex."""
import base64,gzip,hashlib,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
META=json.loads((ROOT/'source_data/bf_global_original_lore_meta.json').read_text())
raw=gzip.decompress(base64.b64decode((ROOT/'source_data/bf_global_original_lore_codex.json.gz.b64').read_text()))
assert hashlib.sha256(raw).hexdigest()==META['payloadJsonSha256']
with zipfile.ZipFile(ROOT/'app/build/outputs/apk/debug/app-debug.apk') as apk:
    paths=set(apk.namelist())
    html=apk.read('assets/index.html').decode('utf-8')
    match=re.search(r'<script type="application/json" id="bf-original-unit-lore-data">(.*?)</script>',html,re.S)
    assert match,'Missing codex payload inside compiled APK'
    included=json.loads(match.group(1))
    assert included==json.loads(raw)
    assert len(included['units'])==2291
    nav=apk.read('assets/bf_home_nav.js')
    ui=apk.read('assets/bf_global_unit_archive.js')
    css=apk.read('assets/bf_global_unit_archive.css')
    assert len(nav)<=65536 and len(ui)<=65536 and len(css)<=65536,'Android UI reader limit'
    assert b'VIEW ORIGINAL GLOBAL PROFILE' in nav
    assert b'bf-original-unit-lore-data' in ui
    assert b'bf-archive-codex' in css
print('PASS packaged 2,291 Global character histories/skills/recipes and Android UI script limits')
