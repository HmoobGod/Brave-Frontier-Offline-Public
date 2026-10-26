"""v0.80 Android APK content audit of source-backed Morgan story and map."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json
R=Path(__file__).resolve().parent
source=json.loads((R/'source_data/bf_global_morgan_original_v080.json').read_text())
assert len(source['quests'])==36 and len(source['dungeons'])==7
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
    names=set(apk.namelist())
    html=apk.read('assets/index.html').decode('utf-8')
    nav=apk.read('assets/bf_home_nav.js').decode('utf-8')
    mapjs=apk.read('assets/bf080_morgan_map.js').decode('utf-8')
    assert '/* BF_ORIGINAL_MORGAN_QUESTS_V080 */' in html
    assert 'BF_MORGAN_QUEST_DATA_V080' in html
    assert 'BF_MORGAN_QUEST_DATA_V080' in nav
    assert 'BF_MORGAN_QUEST_DATA_V080' in mapjs
    assert len(nav.encode())<65536
    assert 'bf_global_offline_demo_v7' in html
    assert '/* BF_ORIGINAL_MISSION_INSPECTOR_STAGED_V060 */' in html
    for d in source['dungeons']:
        path='assets/content/dungeon/'+d['background']
        assert path in names
        raw=apk.read(path)
        assert len(raw)==d['imageBytes']
        assert hashlib.sha256(raw).hexdigest()==d['imageSha256']
    assert 'assets/content/area/area_0002.jpg' in names
    assert 'assets/content/area/area_plate_0002.png' in names
    assert 'assets/bf054_header_status.js' in names
    assert 'assets/bf053_monster_training.js' in names
print('PASS v0.80 APK: 36 Morgan quests, seven original JPEGs and original Morgan world art; v7 identity')
