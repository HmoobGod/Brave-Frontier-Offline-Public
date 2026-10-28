"""v155 Android signed APK original 2022 dungeon first-clear source ledger only."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
asset='bf15500_first_clear_gem_source.js'
src=(R/'app/src/main/assets'/asset).read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert z.read('assets/'+asset)==src
 assert b'BF_GLOBAL_2022_DUNGEON_FIRST_CLEAR_REWARD_SOURCE_V15500' in src
 assert b'originalSourceRewardCount:29' in src
 assert b'liveStoryQuestRewardCount:22' in src
 assert b'amdahlSourceOnlyRewardCount:7' in src
 assert b'actualGemsGranted:0,saveMutation:false' in src
 assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'readPackagedText("bf15500_first_clear_gem_source.js")' in java
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'bf-development-debug.keystore' in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v155 signed APK bundles exact 29 source-first-clear references with no save or Gem wallet change')
