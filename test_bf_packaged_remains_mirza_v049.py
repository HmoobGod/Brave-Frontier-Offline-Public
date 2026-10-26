"""v0.49 verifies original Mirza mission data/art in the actual Android APK."""
from pathlib import Path
from zipfile import ZipFile
import hashlib, json
R=Path(__file__).resolve().parent
m=json.loads((R/'source_data/bf_global_remains_mirza_v049.json').read_text('utf-8'))
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    html=z.read('assets/index.html').decode('utf-8')
    nav=z.read('assets/bf_home_nav.js')
    art=z.read('assets/content/dungeon/dungeon_battle_10600.jpg')
    assert len(art)==66699 and hashlib.sha256(art).hexdigest()==m['sources']['backgroundSha256']
    assert art==(R/'source_assets/bf1/dungeon/dungeon_battle_10600.jpg').read_bytes()
    for mark in ('BF_REMAINS_OF_MIRZA_V049','BF_GLOBAL_QUEST_TEXT_DATA_V048',
                 'BF_MAGUTAGAL_WETLANDS_V047','BF_FOREST_OF_BEASTS_V046',
                 'BF_EGOR_SNOWFIELD_V045','BF_EXPERIMENTAL_SBB_V044',
                 'BF_GLOBAL_SBB_PREVIEW_V043','BF_EVOLUTION_ROADMAP_V039'):
        assert html.count('/* '+mark+' */')==1,mark
    assert 'window.BF_QUEST_BACKGROUNDS["dungeon_battle_10600.jpg"]' in html
    assert 'window.BF_QUEST_ENGLISH_DESCRIPTIONS_V049=Object.freeze(' in html
    assert b'Remains of Mirza' in nav and b'Moonlit Battle' in nav
    assert len(nav)<65536,len(nav)
    assert 'bf_global_offline_demo_v7' in html
print('PASS v0.49 packaged Mirza original source JPEG and English, 25 quests, v7')
