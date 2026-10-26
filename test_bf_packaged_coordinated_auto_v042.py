"""v0.42 APK preserves all previous content and optional coordinated Auto Battle."""
from pathlib import Path
from zipfile import ZipFile
apk=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
assert apk.exists(),apk
with ZipFile(apk) as z:
    html=z.read('assets/index.html').decode('utf-8')
    for marker in ('/* BF_COORDINATED_AUTO_V042 */','/* BF_SOURCE_AWARE_AUTO_V041 */',
        '/* BF_BATTLE_BB_GUIDE_V040 */','/* BF_EVOLUTION_ROADMAP_V039 */',
        '/* BF_GLOBAL_OTHER_SIX_STAR_V038 */'):
        assert html.count(marker)==1,marker
    assert 'window.BF042AutoCoordination?.plan(liveParty())' in html
    assert 'window.BF041SmartAuto?.kindFor(p)' in html
    assert 'bf_global_offline_demo_v7' in html
    assert 'unit_anime_atlas_10025.png' in html
print('PASS v0.42 packaged: coordinated optional support AI; original evolution/source BB; save v7')
