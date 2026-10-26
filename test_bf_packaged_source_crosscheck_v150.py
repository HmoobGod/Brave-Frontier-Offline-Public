"""v1.50 packaged content, development identity and offline-only boundaries."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 for asset in ('bf150_source_crosscheck.js','bf120_historical_encounters.js',
       'bf110_quest_journal.js','bf101_story_continue.js',
       'bf100_grand_gaia_campaign.js','bf090_st_lamia_map.js',
       'bf080_morgan_map.js','bf_global_unit_archive.js'):
  assert 'assets/'+asset in names,asset
 js=z.read('assets/bf150_source_crosscheck.js').decode('utf8')
 assert js.count('/* BF_GLOBAL_SOURCE_CROSSCHECK_V150 */')==1
 assert 'actual2022BattleFormationsConfirmed:0' in js
 assert 'localStorage' not in js and 'saveProgress(' not in js
 html=z.read('assets/index.html').decode('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert 'id="bf-global-unit-catalog-data"' in html
 assert len(z.read('assets/bf_home_nav.js'))<65536
manifest=(R/'app/src/main/AndroidManifest.xml').read_text('utf8')
assert 'android.permission.INTERNET' not in manifest
assert 'usesCleartextTraffic="false"' in manifest
build=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in build
assert "applicationId 'org.bravefrontier.offline'" in build
assert 'bf-development-debug.keystore' in build
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('evaluateJavascript(catalogScript, null)')<java.index('readPackagedText("bf150_source_crosscheck.js")')
print('PASS v1.50: packaged crosscheck, original sources, offline manifest, same Android app/signing/v7 save')
