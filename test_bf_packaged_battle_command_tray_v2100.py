"""v21.00 Android APK contains native-controls battle command tray."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for name in ('bf2100_battle_command_tray.js','bf2000_story_battle_hud.js',
              'bf1900_evolution_ab.js','index.html'):
  assert 'assets/'+name in names,name
 src=z.read('assets/bf2100_battle_command_tray.js').decode('utf8')
 assert '/* BF_GLOBAL_BATTLE_COMMAND_TRAY_V2100 */' in src
 assert len(src.encode('utf8'))<65536
 assert 'localStorage' not in src and 'saveProgress(' not in src
 # Every signed standard owner APK contains all native manual protection
 # modes; the default 40% path remains and player slot validation is strict.
 assert "'bf2100-protect-critical',()=>protectWounded(0.20)" in src
 assert "'bf2100-protect',()=>protectWounded()" in src
 assert "'bf2100-protect-cautious',()=>protectWounded(0.60)" in src
 assert 'if(![0.20,0.40,0.60].includes(threshold)||!ready()' in src
 assert 'S.party[p.id]!==p||!slots.children[p.id]' in src
 assert 'protectCritical.disabled=!woundedPlan(0.20);' in src
 assert 'protectCautious.disabled=!woundedPlan(0.60);' in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf2000_story_battle_hud.js")')<java.index('readPackagedText("bf2100_battle_command_tray.js")')
print('PASS v21.00 offline squad commands APK and save compatibility')
