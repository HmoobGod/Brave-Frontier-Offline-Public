"""v0.43 APK: source-only SBB data, combat v0.42 and save v7 preserved."""
from pathlib import Path
from zipfile import ZipFile
p=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
assert p.is_file(),p
with ZipFile(p) as z:
    s=z.read('assets/index.html').decode('utf8')
    for tag in ('/* BF_GLOBAL_SBB_PREVIEW_V043 */','/* BF_COORDINATED_AUTO_V042 */',
                '/* BF_SOURCE_AWARE_AUTO_V041 */','/* BF_BATTLE_BB_GUIDE_V040 */',
                '/* BF_EVOLUTION_ROADMAP_V039 */','/* BF_GLOBAL_OTHER_SIX_STAR_V038 */'):
        assert s.count(tag)==1,tag
    assert s.count('id="bf043-sbb-preview-style"')==1
    assert 'window.BF043SBBSource=Object.freeze' in s
    assert 'bf_global_offline_demo_v7' in s
    assert 'unit_anime_atlas_10025.png' in s
print('PASS v0.43 source preview packaged, original unit forms, v7 save intact')
