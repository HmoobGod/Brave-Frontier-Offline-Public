"""v0.40 packaged-APK regression: BB guide present and v7 compatible."""
from pathlib import Path
from zipfile import ZipFile
p=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
assert p.exists(),p
with ZipFile(p) as z:
    html=z.read('assets/index.html').decode('utf-8')
    assert html.count('/* BF_BATTLE_BB_GUIDE_V040 */')==1
    assert html.count('id="bf040-bb-guide-style"')==1
    assert 'window.BFGlobalBBGuideV040=Object.freeze({infoFor,refresh});' in html
    assert 'bf_global_offline_demo_v7' in html
    assert '/* BF_EVOLUTION_ROADMAP_V039 */' in html
    assert '/* BF_GLOBAL_OTHER_SIX_STAR_V038 */' in html
    assert 'unit_anime_atlas_10025.png' in html
print('PASS v0.40 APK: BB source guide, Evolution Roadmap, Global 6-star content and save v7')
