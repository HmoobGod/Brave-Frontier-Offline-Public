"""v0.44 APK contains only opt-in SBB DEMO, original content and v7 intact."""
from pathlib import Path
from zipfile import ZipFile
p=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
assert p.exists()
with ZipFile(p) as z:
 s=z.read('assets/index.html').decode('utf8')
 for tag in ('/* BF_EXPERIMENTAL_SBB_V044 */','/* BF_GLOBAL_SBB_PREVIEW_V043 */',
   '/* BF_COORDINATED_AUTO_V042 */','/* BF_SOURCE_AWARE_AUTO_V041 */',
   '/* BF_BATTLE_BB_GUIDE_V040 */','/* BF_EVOLUTION_ROADMAP_V039 */'):
    assert s.count(tag)==1,tag
 assert 'bf_global_offline_demo_v7' in s
 assert "if(action.kind==='sbb_demo' && window.BF044SBBDemo?.perform)" in s
 assert 'unit_anime_atlas_10025.png' in s
print('PASS v0.44 APK original v0.38–v0.43 assets and v7; optional SBB DEMO only')
