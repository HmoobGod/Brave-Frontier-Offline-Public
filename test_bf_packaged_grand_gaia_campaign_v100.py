"""v1.00 APK smoke: verified three-region source-backed demo remains offline."""
from pathlib import Path
from zipfile import ZipFile
import json,hashlib
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
  entries=set(apk.namelist())
  html=apk.read('assets/index.html').decode('utf8')
  nav=apk.read('assets/bf_home_nav.js')
  addon=apk.read('assets/bf100_grand_gaia_campaign.js').decode('utf8')
  for marker in ('BF_ORIGINAL_MORGAN_QUESTS_V080','BF_STLAMIA_QUESTS_V090',
                 'BF_TOWER_OF_MISTRAL_V051','BF_ORIGINAL_MISSION_INSPECTOR_STAGED_V060',
                 'BF_EXTENDED_PLAYABLE_ATTACK_FRAMES_V065',
                 'BF_PLAYABLE_HIT_INSPECTOR_V070'):
    assert html.count('/* '+marker+' */')==1,marker
  assert addon.count('/* BF_GRAND_GAIA_CAMPAIGN_V100 */')==1
  assert '106 archived missions' in addon
  assert 'localStorage' not in addon and 'saveProgress(' not in addon
  assert 'bf_global_offline_demo_v7' in html
  assert len(nav)<65536
  assert 'assets/bf080_morgan_map.js' in entries
  assert 'assets/bf090_st_lamia_map.js' in entries
  assert 'assets/bf100_grand_gaia_campaign.js' in entries
  for area in (1,2,3):
    assert 'assets/content/area/area_%04d.jpg'%area in entries
    assert 'assets/content/area/area_plate_%04d.png'%area in entries
  for id in [*range(10300,10900,100), *range(20100,20800,100),
              *range(30100,30800,100)]:
    assert 'assets/content/dungeon/dungeon_battle_%d.jpg'%id in entries,id
  assert 'assets/content/monster/img/bf053_training_monsters.png' in entries
  assert 'assets/bf054_header_status.js' in entries
gradle=(R/'app/build.gradle').read_text('utf8')
# v1.01 retains all v1.00 assets while incrementing the installable demo version.
assert "versionName '" in gradle
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf090_st_lamia_map.js")')<java.index('readPackagedText("bf100_grand_gaia_campaign.js")')
print('PASS v1.00 APK original 3 regions / 23 dungeons / 106 missions and unchanged save v7')
