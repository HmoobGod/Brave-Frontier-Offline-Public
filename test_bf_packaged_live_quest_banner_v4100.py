"""v41.00 signed offline APK packages optional original quest battle name overlay."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for name in ('bf4100_live_quest_banner.js','bf4000_next_chapter_intro.js',
              'bf3900_story_battle_handoff.js'):
  assert 'assets/'+name in names,name
 src=z.read('assets/bf4100_live_quest_banner.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_LIVE_QUEST_BANNER_V4100 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
# This inherited test must also accept later milestones that preserve v41.
import re
match=re.search(r"versionName '(\d+)\.00\.0-demo'",gradle)
assert match and int(match.group(1))>=41
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v41.00 original battle banner included without changing original game save or signing')
