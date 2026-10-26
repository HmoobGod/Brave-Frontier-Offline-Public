"""v100 packaged Android keeps original saves/signing and loads optional squads."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    data=z.read('assets/bf10000_qol_squad_presets.js').decode('utf8')
    assert data.count('BF_GLOBAL_QOL_SQUAD_PRESETS_V10000')==1
    assert "P.squad=slot.squad.slice()" in data
    assert "if(!saveProgress())" in data
    assert 'assets/bf9900_qol_battle_speed.js' in z.namelist()
    assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf9900_qol_battle_speed.js")')<java.index('readPackagedText("bf10000_qol_squad_presets.js")')
gradle=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in gradle for v in range(100,200))
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v100 packaged squad presets with v7 save, native key and package identity')
