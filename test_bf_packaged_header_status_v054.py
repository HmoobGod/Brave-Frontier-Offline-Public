"""v0.54 signed APK: intact original Global header art, cropped UI and honest progress."""
from pathlib import Path
from zipfile import ZipFile
import hashlib

R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
    header=apk.read('assets/content/header/header_ui3.png')
    assert len(header)==46548
    assert hashlib.sha256(header).hexdigest()==(
        'dbf3ee6e3893880f9f701aee8e3b807cc530b676463e7fdefe85a552e125e063')
    js=apk.read('assets/bf054_header_status.js').decode('utf-8')
    assert js.count('/* BF_HEADER_STATUS_FIDELITY_V054 */')==1
    assert 'aspect-ratio:644/174!important' in js
    assert '5*(level-1)*level/2' in js
    assert 'energyAvailable(){return false}' in js
    assert 'localStorage.setItem' not in js
    assert b'bf_global_offline_demo_v7' in apk.read('assets/index.html')
    assert b'/* BF_MONSTER_TRAINING_HOOK_V053 */' in apk.read('assets/index.html')
    assert 'assets/bf_home_nav.js' in apk.namelist()
    assert 'assets/bf053_monster_training.js' in apk.namelist()
    assert 'assets/content/monster/img/bf053_training_monsters.png' in apk.namelist()
    assert len(apk.read('assets/bf_home_nav.js'))<65536
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
assert 'readPackagedText("bf054_header_status.js")' in java
print('PASS v0.54 packaged original header bytes, accurate EXP overlay, demo Energy, v0.53 and v7 intact')
