"""v40.00 offline signed APK next chapter intro and save compatibility."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for f in ('bf4000_next_chapter_intro.js','bf3900_story_battle_handoff.js','bf3000_battle_results.js'):
  assert 'assets/'+f in names,f
 src=z.read('assets/bf4000_next_chapter_intro.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_NEXT_CHAPTER_INTRO_V4000 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v40.00 source-gated next chapter intro bundled without modifying save or signing identity')
