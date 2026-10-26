"""v0.70: verify original attack inspector, archived roster markers in signed APK."""
from pathlib import Path
from zipfile import ZipFile
import json
ROOT=Path(__file__).resolve().parent
with ZipFile(ROOT/'app/build/outputs/apk/debug/app-debug.apk') as z:
  html=z.read('assets/index.html').decode('utf8')
  assert html.count('/* BF_PLAYABLE_HIT_INSPECTOR_V070 */')==1
  assert html.count('/* BF_EXTENDED_PLAYABLE_ATTACK_FRAMES_V065 */')==1
  assert 'window.BFPlayableAttackFramesV062' in html
  assert 'ARCHIVE ONLY' in html
  assert 'not normalized' in html
  assert 'bf_global_offline_demo_v7' in html
  assert '/* BF_ORIGINAL_MISSION_INSPECTOR_STAGED_V060 */' in html
  assert '/* BF_TOWER_BOSS_FORMATION_HOOK_V055 */' in html
  assert 'assets/bf054_header_status.js' in z.namelist()
  assert len(z.read('assets/bf_home_nav.js'))<65536
print('PASS v0.70 APK preserved v0.65 authentic playable hit inspector, offline quests and save v7')
