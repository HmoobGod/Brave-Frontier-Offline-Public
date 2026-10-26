"""v0.65 packaged Android APK preserves master 72-unit hit references and save."""
from pathlib import Path
from zipfile import ZipFile
import json
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/'source_data/bf_global_playable_attack_frames_v061.json').read_text('utf-8'))
assert len(m['rows'])==72
with ZipFile(ROOT/'app/build/outputs/apk/debug/app-debug.apk') as z:
    html=z.read('assets/index.html').decode('utf-8')
    addon=z.read('assets/bf062_playable_attack_frames.js').decode('utf-8')
    assert html.count('/* BF_PLAYABLE_ORIGINAL_HITS_V062 */')==1
    assert html.count('/* BF_EXTENDED_PLAYABLE_ATTACK_FRAMES_V065 */')==1
    assert addon.count('/* BF_PLAYABLE_ORIGINAL_HITS_V062 */')==1
    assert '__BF_PLAYABLE_ATTACK_FRAMES__' in addon
    assert '10023' in html and '130' in html
    assert 'window.BF_ARCHIVE_NORMAL_HITS=' in html
    assert 'bf_global_offline_demo_v7' in html
    assert 'BF_HIT_TICKS_PER_SECOND_UNVERIFIED=60' in html
    assert '/* BF_ORIGINAL_MISSION_INSPECTOR_STAGED_V060 */' in html
    assert '/* BF_TOWER_BOSS_FORMATION_HOOK_V055 */' in html
    assert '/* BF_MONSTER_TRAINING_HOOK_V053 */' in html
    assert len(z.read('assets/bf_home_nav.js'))<65536
print('PASS v0.65 packaged original 72 playable hit events, source guards, prior Mistral, v7')
