"""v153 signed APK original 2022 Legend Stone 4,000 Merit source reference."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
asset='bf15300_legend_stone_merit_source.js'
src=(R/'app/src/main/assets'/asset).read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert z.read('assets/'+asset)==src
 assert b'BF_GLOBAL_ORIGINAL_2022_LEGEND_STONE_MERIT_EXCHANGE_V15300' in src
 assert b'originalPrice:4000' in src
 assert b'playableEvolutionsUnlocked:false' in src
 assert b'liveAcquisition:false,saveMutation:false' in src
 assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'readPackagedText("bf15300_legend_stone_merit_source.js")' in java
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'bf-development-debug.keystore' in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v153 signed APK source-only Legend Stone price and unchanged v7 identity')
