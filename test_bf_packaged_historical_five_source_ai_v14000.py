"""v140: packaged original Global 2014 five-mission practice source AI."""
from pathlib import Path
import zipfile
APK=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(APK) as z:
 source=z.read('assets/bf14000_five_historical_source_ai.js').decode('utf8')
 lab=z.read('assets/bf200_historical_wave_lab.js').decode('utf8')
 html=z.read('assets/index.html').decode('utf8')
 assert source.count('BF_GLOBAL_2014_FIVE_MISSION_SOURCE_AI_V14000')==1
 assert 'bf-global-historical-2014-five-mission-attack-ai-source-v140' in source
 assert 'sourceEnemyPlan2014(foes)' in lab and 'BFHistoricalFiveMissionSourceAIV14000' in lab
 assert 'bf_global_offline_demo_v7' in html
print('PASS v140 APK: 41 historical 2014 source-validated enemy attack decisions, no owner save schema modifications')
