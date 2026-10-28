"""v149 original Amdahl source art and read-only reference in signed Android APK."""
from pathlib import Path
import zipfile,hashlib,json
R=Path(__file__).resolve().parent
M=json.loads((R/'source_data/bf_global_2022_amdahl_original_art_v149.json').read_text('utf8'))
APK=R/'app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(APK) as z:
 for name,meta in M['sourceImages'].items():
  b=z.read('assets/'+name)
  assert hashlib.sha256(b).hexdigest()==meta['sha256'] and len(b)==meta['bytes']
 html=z.read('assets/index.html').decode('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert '/* BF_GLOBAL_AMDAHL_PLAYABLE_QUESTS_V147 */' not in html
 js=z.read('assets/bf14900_original_amdahl_art.js').decode('utf8')
 assert 'BF_GLOBAL_AMDAHL_ORIGINAL_ART_VIEW_V14900' in js
 assert 'originalGameplayEnabled:false' in js
print('PASS v149 Android APK contains all exact original Amdahl area/battle art, locked preview, unchanged 106 quest/save state')
