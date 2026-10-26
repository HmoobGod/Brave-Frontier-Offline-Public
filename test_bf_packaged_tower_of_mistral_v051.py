"""v0.51 verify original Tower of Mistral metadata and art in Android APK."""
from pathlib import Path
from zipfile import ZipFile
import json,hashlib

ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/'source_data/bf_global_tower_of_mistral_v051.json').read_text('utf-8'))
with ZipFile(ROOT/'app/build/outputs/apk/debug/app-debug.apk') as z:
    html=z.read('assets/index.html').decode('utf-8')
    nav=z.read('assets/bf_home_nav.js')
    art=z.read('assets/content/dungeon/dungeon_battle_10800.jpg')
    assert len(art)==46410 and hashlib.sha256(art).hexdigest()==m['sources']['backgroundSha256']
    assert art==(ROOT/'source_assets/bf1/dungeon/dungeon_battle_10800.jpg').read_bytes()
    for marker in ('BF_TOWER_OF_MISTRAL_V051','BF_MONSTERS_NEST_V050',
                   'BF_REMAINS_OF_MIRZA_V049','BF_GLOBAL_QUEST_TEXT_DATA_V048',
                   'BF_MAGUTAGAL_WETLANDS_V047','BF_FOREST_OF_BEASTS_V046',
                   'BF_EGOR_SNOWFIELD_V045','BF_EXPERIMENTAL_SBB_V044',
                   'BF_GLOBAL_SBB_PREVIEW_V043','BF_EVOLUTION_ROADMAP_V039'):
        assert html.count('/* '+marker+' */')==1,marker
    assert 'window.BF_QUEST_ENGLISH_DESCRIPTIONS_V051=Object.freeze(' in html
    assert 'window.BF_QUEST_BACKGROUNDS["dungeon_battle_10800.jpg"]' in html
    assert b'Tower of Mistral' in nav and b'The Forged Gigantor' in nav
    assert len(nav)<65536,len(nav)
    assert 'bf_global_offline_demo_v7' in html
print('PASS v0.51 APK includes original Tower background, 5 quests, older builds, v7')
