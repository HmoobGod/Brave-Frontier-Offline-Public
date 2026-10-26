"""v0.80: verify Morgan original 2022 source records, art and v7 in Android APK."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json
R=Path(__file__).resolve().parent
m=json.loads((R/'source_data/bf_global_morgan_original_v080.json').read_text('utf-8'))
assert len(m['quests'])==36 and len(m['dungeons'])==7
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    html=z.read('assets/index.html').decode('utf-8')
    nav=z.read('assets/bf_home_nav.js')
    addon=z.read('assets/bf080_morgan_map.js').decode('utf-8')
    assert html.count('/* BF_ORIGINAL_MORGAN_QUESTS_V080 */')==1
    assert 'bf-global-morgan-2022-original-quests-v080' in html
    assert 'The Burning Desert' in html and 'The Eroding Barricade' in html
    assert 'window.BF_MORGAN_QUEST_DATA_V080=Object.freeze(' in html
    assert html.count('window.BF_QUEST_CATALOG.push(')==9  # Mistral, Morgan, and St. Lamia source groups
    assert 'bf_global_offline_demo_v7' in html
    assert len(nav)<65536,len(nav)
    assert b'MST_DUNGEONS_DUNGEON_' in nav and b'BF_MORGAN_QUEST_DATA_V080' in nav
    assert addon.count('/* BF_ORIGINAL_MORGAN_MAP_V080 */')==1
    assert 'MORGAN · 7 DUNGEONS' in addon
    for d in m['dungeons']:
        name='assets/content/dungeon/'+d['background']
        raw=z.read(name)
        assert len(raw)==d['imageBytes'],d['id']
        assert hashlib.sha256(raw).hexdigest()==d['imageSha256'],d['id']
    for name,digest in [
        ('assets/content/area/area_0002.jpg','e4390a48e56cb1f071f299d22a89e9bbb5c90610e47b8ff4cd3ddf0a888ac0fc'),
        ('assets/content/area/area_plate_0002.png','a437f389f77e203a6d51539481d6e153e57963afb67c7e045054a212706395fd')]:
        assert hashlib.sha256(z.read(name)).hexdigest()==digest
    for prior in ['BF_TOWER_OF_MISTRAL_V051','BF_ORIGINAL_MISSION_INSPECTOR_STAGED_V060','BF_EXTENDED_PLAYABLE_ATTACK_FRAMES_V065','BF_PLAYABLE_HIT_INSPECTOR_V070']:
        assert '/* '+prior+' */' in html,prior
    assert 'assets/bf054_header_status.js' in z.namelist()
assert 'readPackagedText("bf080_morgan_map.js")' in (
    R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
print('PASS v0.80 Android APK: original Morgan map and 7 battle JPEGs, 36 quests, v7, prior milestones')
