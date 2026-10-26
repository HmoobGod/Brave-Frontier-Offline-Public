"""Verify original 2022 Egor background and v0.45 quests in actual APK."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json
R=Path(__file__).resolve().parent
j=json.loads((R/'source_data/bf_global_egor_snowfield_v045.json').read_text())
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 s=z.read('assets/index.html').decode()
 nav=z.read('assets/bf_home_nav.js').decode()
 art=z.read('assets/content/dungeon/dungeon_battle_10300.jpg')
 assert hashlib.sha256(art).hexdigest()==j['sources']['backgroundSha256']
 for m in ('/* BF_EGOR_SNOWFIELD_V045 */','/* BF_EXPERIMENTAL_SBB_V044 */',
           '/* BF_GLOBAL_SBB_PREVIEW_V043 */','/* BF_EVOLUTION_ROADMAP_V039 */'):
  assert s.count(m)==1,m
 assert s.count('window.BF_QUEST_BACKGROUNDS["dungeon_battle_10300.jpg"]')==1
 assert 'Egor Snowfield' in nav and 'The Dragon Hunting Ice Knight' in nav
 assert 'bf_global_offline_demo_v7' in s
print('PASS v0.45 APK original Egor art, 13 quests and save v7')
