"""v145 signed APK packages exact-original 2022 tracks and the optional music UI."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parent
M=json.loads((R/'source_data/bf_global_2022_original_quest_music_v145.json').read_text())
with zipfile.ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 js=z.read('assets/bf14500_original_global_music.js').decode('utf8')
 html=z.read('assets/index.html').decode('utf8')
 assert js.count('BF_ORIGINAL_2022_GLOBAL_OPTIN_MUSIC_V14500')==1
 assert M['canonicalCueSha256'] in js
 assert 'bf_global_offline_demo_v7' in html
 assert 'autoplay:false,saveMutation:false' in js
 for track,details in M['packagedAudio'].items():
  actual=z.read('assets/content/sound/'+track)
  assert len(actual)==details['bytes'] and hashlib.sha256(actual).hexdigest()==details['sha256'],track
 assert len([x for x in z.namelist() if x.startswith('assets/content/sound/') and x.endswith('.mp3')])==3
print('PASS v145 APK: original 2022 source-hashed 3-track opt-in music controls with no save changes')
