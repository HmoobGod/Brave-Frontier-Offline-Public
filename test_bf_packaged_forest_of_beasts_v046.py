"""Verify v0.46 original Forest of Beasts quests/art in compiled offline APK."""
from pathlib import Path
import hashlib,json
from zipfile import ZipFile
R=Path(__file__).resolve().parent
m=json.loads((R/'source_data/bf_global_forest_of_beasts_v046.json').read_text('utf8'))
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 s=z.read('assets/index.html').decode('utf8')
 nav=z.read('assets/bf_home_nav.js').decode('utf8')
 art=z.read('assets/content/dungeon/dungeon_battle_10400.jpg')
 assert len(art)==55278 and hashlib.sha256(art).hexdigest()==m['sources']['backgroundSha256']
 for mark in ('/* BF_FOREST_OF_BEASTS_V046 */','/* BF_EGOR_SNOWFIELD_V045 */',
  '/* BF_EXPERIMENTAL_SBB_V044 */','/* BF_GLOBAL_SBB_PREVIEW_V043 */',
  '/* BF_EVOLUTION_ROADMAP_V039 */'):
  assert s.count(mark)==1,mark
 assert s.count('window.BF_QUEST_BACKGROUNDS["dungeon_battle_10400.jpg"]')==1
 assert 'Forest of Beasts' in nav and 'Hunter from the Forest' in nav
 assert 'bf_global_offline_demo_v7' in s
print('PASS v0.46 packaged original forest art, four quests, prior content and v7')
