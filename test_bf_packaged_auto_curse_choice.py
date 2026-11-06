"""APK contains both Auto Curse choice guards; no signing/device certification."""
from pathlib import Path
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parent
with ZipFile(ROOT/'app/build/outputs/apk/debug/app-debug.apk') as archive:
    html=archive.read('assets/index.html').decode()
    advanced=archive.read('assets/bf10500_qol_advanced_smart_auto.js')
    assert 'BFGlobalCurseBBLockV5900?.cursed(p?.id)' in html
    assert b'BFGlobalCurseBBLockV5900?.cursed(unit?.id)' in advanced
    assert advanced==(ROOT/'app/src/main/assets/bf10500_qol_advanced_smart_auto.js').read_bytes()
    assert 'bf_global_offline_demo_v7' in html
print('PASS packaged default/Smart/Advanced Auto Curse choice guards and exact Advanced module')
