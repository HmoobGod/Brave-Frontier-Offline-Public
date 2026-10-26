"""v93 Android signed artifact contains source-qualified critical hit combat."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 assert 'assets/bf9300_single_hit_critical_combat.js' in names
 assert 'assets/bf9200_source_offensive_bb_levels.js' in names
 assert 'assets/bf9100_innate_status_resistance.js' in names
 assert 'assets/bf8400_original_normal_crystal_checks.js' in names
 src=z.read('assets/bf9300_single_hit_critical_combat.js').decode('utf8')
 assert src.count('BF_GLOBAL_SINGLE_HIT_CRITICAL_COMBAT_V9300')==1
 assert 'window.prototypeDamage=function' in src
 assert 'source.lookup(unit.unitId)' in src
 assert 'bf9400-critical-notice' in src
 assert 'bf9400-critical-banner' in src
 assert 'CRITICAL HIT!' in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf9200_source_offensive_bb_levels.js")')<java.index('readPackagedText("bf9300_single_hit_critical_combat.js")')
g=(R/'app/build.gradle').read_text()
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(93,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text()
print('PASS v93 offline signed APK has one-hit critical combat; v7 saves/signature unchanged')
