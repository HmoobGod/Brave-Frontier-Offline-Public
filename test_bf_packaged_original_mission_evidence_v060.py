"""v0.60 original archived Mistral master data is packaged safely in Android APK."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json
R=Path(__file__).resolve().parent
source=json.loads((R/'source_data/bf_global_mistral_raw_mission_evidence_v056.json').read_text('utf-8'))
assert source['schema']=='bf-global-2022-mistral-raw-mission-evidence-v056'
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    html=z.read('assets/index.html').decode('utf-8')
    loader=z.read('assets/bf057_mission_evidence.js').decode('utf-8')
    panel=z.read('assets/bf058_mission_inspector.js').decode('utf-8')
    for m in ('BF_ORIGINAL_MISSION_EVIDENCE_V057',
              'BF_ORIGINAL_MISSION_INSPECTOR_V058',
              'BF_ORIGINAL_MISSION_INSPECTOR_STAGED_V060',
              'BF_TOWER_BOSS_FORMATION_HOOK_V055',
              'BF_MISTRAL_BOSS_HOOK_V052',
              'BF_MONSTER_TRAINING_HOOK_V053',
              'BF_MONSTER_TRAINING_DRAW_V053',
              'BF_TOWER_OF_MISTRAL_V051',
              'BF_MONSTERS_NEST_V050',
              'BF_REMAINS_OF_MIRZA_V049'):
        assert html.count('/* '+m+' */')==1,m
    assert loader.count('__BF_MISSION_EVIDENCE_ROWS__')==1
    assert panel.count('/* BF_ORIGINAL_MISSION_INSPECTOR_V058 */')==1
    assert 'd4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83' in html
    assert '1:10800,0:10801' in html and '8:0:1:0:0' in html
    assert 'item identity unknown' in html
    assert 'Enemy identities, enemy AI, drop rates and damage formulas are NOT restored' in html
    assert 'bf_global_offline_demo_v7' in html
    assert len(z.read('assets/bf_home_nav.js')) < 65536
    assert 'assets/bf054_header_status.js' in z.namelist()
    assert 'assets/bf055_tower_formations.js' in z.namelist()
    assert 'assets/content/monster/img/bf053_training_monsters.png' in z.namelist()
print('PASS v0.60 packaged source-reference audit, existing art/features and save v7')
