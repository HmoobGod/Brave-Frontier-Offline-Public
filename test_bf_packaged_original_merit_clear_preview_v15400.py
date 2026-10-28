"""v154: APK packages read-only 2022 merit quest milestone local preview."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
asset='bf15400_original_merit_clear_preview.js'
src=(R/'app/src/main/assets'/asset).read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert z.read('assets/'+asset)==src
 assert b'BF_GLOBAL_2022_QUEST_CLEAR_MERIT_PREVIEW_V15400' in src
 assert b'originalStoryClearMissionId:365' in src
 assert b'meritAwardEnabled:false' in src
 assert b'playableContentChanged:false,saveMutation:false' in src
 assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf15300_legend_stone_merit_source.js")') < \
       java.index('readPackagedText("bf15400_original_merit_clear_preview.js")')
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'bf-development-debug.keystore' in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v154: APK contains exact source-only 2022 merit milestones; no currency/save/Android permission change')
