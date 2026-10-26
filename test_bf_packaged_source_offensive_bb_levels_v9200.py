"""v92 original offensive BB modifier injection and signed Android artifact."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 assert 'assets/bf9200_source_offensive_bb_levels.js' in names
 assert 'assets/bf9100_innate_status_resistance.js' in names
 assert 'assets/bf6800_original_heal_bb_levels.js' in names
 src=z.read('assets/bf9200_source_offensive_bb_levels.js').decode('utf8')
 assert 'BF_GLOBAL_SOURCE_OFFENSIVE_BB_LEVELS_V9200' in src
 assert 'window.bbDamageMultiplier=wrapper' in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf6800_original_heal_bb_levels.js")')<java.index('readPackagedText("bf9200_source_offensive_bb_levels.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(92,200)), "v92+ version required"
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text()
print('PASS v92 signed offline APK contains source-level BB combat modifier, v7 saves and signing kept')
