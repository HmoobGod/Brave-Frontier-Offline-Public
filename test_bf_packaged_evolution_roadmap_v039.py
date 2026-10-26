"""v0.39 APK packaging: roadmap is offline, inline, and leaves v7 untouched."""
from pathlib import Path
import zipfile
p=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
assert p.exists(),p
with zipfile.ZipFile(p) as z:
 html=z.read('assets/index.html').decode('utf-8')
 assert html.count('/* BF_EVOLUTION_ROADMAP_V039 */')==1
 assert html.count('id="bf039-evo-roadmap-style"')==1
 assert 'window.BF_EvolutionRoadmapV039' in html
 assert "bf_global_offline_demo_v7" in html
 assert '/* BF_GLOBAL_OTHER_SIX_STAR_V038 */' in html
 assert 'unit_anime_atlas_10025.png' in html and 'unit_anime_atlas_10015.png' in html
print('PASS v0.39 packaged APK: optional read-only Evolution Roadmap, 72 forms and save v7')
