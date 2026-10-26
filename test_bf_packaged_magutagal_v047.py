"""v0.47 APK packages Magutagal art/quests and preserves legacy original data."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/'source_data/bf_global_magutagal_v047.json').read_text('utf-8'))
p=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert p.is_file(),p
with ZipFile(p) as z:
    s=z.read('assets/index.html').decode('utf-8')
    nav=z.read('assets/bf_home_nav.js').decode('utf-8')
    pic=z.read('assets/content/dungeon/dungeon_battle_10500.jpg')
    assert len(pic)==43940 and hashlib.sha256(pic).hexdigest()==m['sources']['backgroundSha256']
    for marker in ('/* BF_MAGUTAGAL_WETLANDS_V047 */','/* BF_FOREST_OF_BEASTS_V046 */',
        '/* BF_EGOR_SNOWFIELD_V045 */','/* BF_EXPERIMENTAL_SBB_V044 */',
        '/* BF_GLOBAL_SBB_PREVIEW_V043 */','/* BF_EVOLUTION_ROADMAP_V039 */'):
        assert s.count(marker)==1,marker
    assert s.count('window.BF_QUEST_BACKGROUNDS["dungeon_battle_10500.jpg"]')==1
    assert 'Magutagal Wetlands' in nav and 'The Thundering Strategist' in nav
    assert 'bf_global_offline_demo_v7' in s
print('PASS v0.47 packaged Magutagal, original JPEG, previous features and save v7')
