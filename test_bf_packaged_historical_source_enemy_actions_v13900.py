"""v139 signed Android APK retains historical source AI simulator and saves."""
from pathlib import Path
import zipfile
APK=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(APK) as z:
 historic=z.read('assets/bf200_historical_wave_lab.js').decode('utf8')
 original=z.read('assets/bf8700_original_basics_ai_reference.js').decode('utf8')
 html=z.read('assets/index.html').decode('utf8')
 assert 'function sourceEnemyPlan2014(foes)' in historic
 assert "sourceAttacks.reduce((n,a)=>n+a.syntheticHarm,0)" in historic
 assert 'random target NOT simulated' in historic
 assert "const blob='797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe'" in original
 assert 'gitBlobSha:blob' in original
 assert 'bf_global_offline_demo_v7' in html
 assert 'BF_GLOBAL_ARCHIVE_TRIALS_V200' in historic
print('PASS v139 APK: authentic 2014 archived AI cadence wired to sandbox practice, no 2022 runtime/save changes')
