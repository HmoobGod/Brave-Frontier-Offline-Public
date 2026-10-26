"""v0.55 package inspection: historical boss preview remains opt-in, no fake sprites."""
from pathlib import Path
from zipfile import ZipFile
import json

R=Path(__file__).resolve().parent
original=json.loads((R/'source_data/bf_global_mistral_boss_intel_v052.json').read_text('utf-8'))
assert original['schema']=='bf-global-mistral-boss-intel-v052'
assert [v['missionId'] for v in original['entries']]==[81,82,83,84,85]
apk=R/'app/build/outputs/apk/debug/app-debug.apk'
with ZipFile(apk) as z:
    html=z.read('assets/index.html').decode('utf-8')
    addon=z.read('assets/bf055_tower_formations.js').decode('utf-8')
    for marker in ('BF_TOWER_BOSS_FORMATION_HOOK_V055',
                   'BF_TOWER_BOSS_PLACEHOLDER_V055',
                   'BF_HISTORICAL_TOWER_FORMATIONS_V055',
                   'BF_MISTRAL_BOSS_HOOK_V052',
                   'BF_MONSTER_TRAINING_HOOK_V053',
                   'BF_MONSTER_TRAINING_DRAW_V053'):
        assert html.count('/* '+marker+' */')==1,marker
    assert addon.count('/* BF_HISTORICAL_TOWER_FORMATIONS_V055 */')==1
    assert "toggle.checked = false" in addon
    assert "historicalBossPreview:true" in addon
    assert "drawPlaceholder(e,ctx,x,y)" in addon
    assert "ART UNKNOWN" in addon
    assert 'const xyEnemy=[[120,95],[101,179],[133,263],[180,181]];' in html
    assert 'window.BF055TowerBosses?.encounter(' in html
    assert 'window.BF055TowerBosses?.drawPlaceholder(' in html
    assert 'bf_global_offline_demo_v7' in html
    assert 'assets/bf054_header_status.js' in z.namelist()
    assert len(z.read('assets/bf_home_nav.js')) < 65536
print('PASS v0.55 APK holds historical boss preview 81-84, silhouettes, previous version and save v7')
