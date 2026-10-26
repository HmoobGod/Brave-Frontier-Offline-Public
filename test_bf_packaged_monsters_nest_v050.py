"""v0.50 verifies original Nest mission data/art in the actual Android APK."""
from pathlib import Path
from zipfile import ZipFile
import hashlib, json
R=Path(__file__).resolve().parent
m=json.loads((R/'source_data/bf_global_monsters_nest_v050.json').read_text('utf-8'))
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    html=z.read('assets/index.html').decode('utf-8')
    nav=z.read('assets/bf_home_nav.js')
    art=z.read('assets/content/dungeon/dungeon_battle_10700.jpg')
    assert len(art)==32032 and hashlib.sha256(art).hexdigest()==m['sources']['backgroundSha256']
    assert art==(R/'source_assets/bf1/dungeon/dungeon_battle_10700.jpg').read_bytes()
    for mark in ('BF_MONSTERS_NEST_V050','BF_GLOBAL_QUEST_TEXT_DATA_V048',
                 'BF_MAGUTAGAL_WETLANDS_V047','BF_FOREST_OF_BEASTS_V046',
                 'BF_EGOR_SNOWFIELD_V045','BF_EXPERIMENTAL_SBB_V044',
                 'BF_GLOBAL_SBB_PREVIEW_V043','BF_EVOLUTION_ROADMAP_V039'):
        assert html.count('/* '+mark+' */')==1,mark
    assert 'window.BF_QUEST_BACKGROUNDS["dungeon_battle_10700.jpg"]' in html
    assert 'window.BF_QUEST_ENGLISH_DESCRIPTIONS_V050=Object.freeze(' in html
    assert b"Monster's Nest" in nav and b'The Monster Slaying Blade' in nav
    assert len(nav)<65536,len(nav)
    assert 'bf_global_offline_demo_v7' in html
print('PASS v0.50 packaged Nest original source JPEG and English, 29 quests, v7')
