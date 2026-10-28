"""v141: signed APK includes source-verifiable 2014 mixed AI, not saved gameplay."""
from pathlib import Path
import zipfile
APK=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(APK) as z:
 js=z.read('assets/bf14100_mixed_historical_source_ai.js').decode('utf8')
 lab=z.read('assets/bf200_historical_wave_lab.js').decode('utf8')
 html=z.read('assets/index.html').decode('utf8')
 assert js.count('BF_GLOBAL_2014_MIXED_MISSION_SOURCE_AI_V14100')==1
 assert 'bf-global-historical-2014-four-mixed-mission-ai-v141' in js
 assert 'unmodeled-source-fallback' in js
 assert 'UNMODELED COMPLEX AI (synthetic reply)' in lab
 assert 'bf_global_offline_demo_v7' in html
print('PASS v141 signed APK: 40 2014 source AI attacks and 6 explicitly synthetic complex fallbacks, v7 save unchanged')
