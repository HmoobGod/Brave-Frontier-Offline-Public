"""v20.00 APK contains offline source quest wave HUD with unchanged save and signing."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for name in ('bf2000_story_battle_hud.js','bf101_story_continue.js',
              'bf110_quest_journal.js','bf1900_evolution_ab.js','index.html'):
  assert 'assets/'+name in names,name
 src=z.read('assets/bf2000_story_battle_hud.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_STORY_BATTLE_HUD_V2000 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'function snapshot()' in src and 'function advance()' in src
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf110_quest_journal.js")')<java.index('readPackagedText("bf2000_story_battle_hud.js")')
print('PASS v20.00: offline Android mission HUD packaged, unchanged save v7 and signing')
