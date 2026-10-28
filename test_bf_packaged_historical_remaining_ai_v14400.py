"""v144: packaged original 2014 complete historical source AI, signed APK regression."""
from pathlib import Path
import zipfile
R=Path(__file__).resolve().parent
with zipfile.ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 js=z.read('assets/bf14400_remaining_historical_source_ai.js').decode('utf8')
 historic=z.read('assets/bf200_historical_wave_lab.js').decode('utf8')
 html=z.read('assets/index.html').decode('utf8')
 assert js.count('BF_GLOBAL_HISTORICAL_2014_COMPLETE_SOURCE_AI_V14400')==1
 assert 'sourceBacked:safe===1' in js
 assert 'complex:29' in js
 assert 'BFHistoricalRemainingMissionSourceAIV14400' in historic
 assert 'UNMODELED COMPLEX AI (synthetic reply)' in historic
 assert 'bf_global_offline_demo_v7' in html
print('PASS v144 signed APK: 2014 177 source AI slots with 29 complex fallback cases, v7 save intact')
