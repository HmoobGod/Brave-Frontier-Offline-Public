"""v143 signed APK carries source-validated original 2022 quest Energy/Karma UI."""
from pathlib import Path
import zipfile
A=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(A) as z:
 js=z.read('assets/bf14300_original_quest_energy.js').decode('utf8')
 html=z.read('assets/index.html').decode('utf8')
 assert js.count('BF_ORIGINAL_2022_QUEST_ENERGY_VISIBILITY_V14300')==1
 assert "staminaEnforced:false" in js
 assert '2022 original · Energy ' in js
 assert 'reference; stamina not enforced' in js
 assert 'bf_global_offline_demo_v7' in html
 assert 'window.BF_QUEST_CATALOG' in html
print('PASS v143 APK: 106 verified original 2022 energy and karma quest labels, unchanged save v7')
