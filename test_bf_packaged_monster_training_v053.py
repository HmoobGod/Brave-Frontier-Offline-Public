"""v0.53 verify exact archived BF1 additional monster atlas in signed Android APK."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,struct
R=Path(__file__).resolve().parent
m=json.loads((R/'source_data/bf_global_monster_training_v053.json').read_text('utf-8'))
atlas=m['derivedAtlas']
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    img=z.read('assets/'+atlas['apkPath'])
    assert len(img)==atlas['bytes']==914491
    assert hashlib.sha256(img).hexdigest()==atlas['sha256']
    assert img==(R/atlas['sourcePath']).read_bytes()
    assert img[:8]==bytes((137,80,78,71,13,10,26,10))
    assert struct.unpack('>II',img[16:24])==(1536,2048)
    html=z.read('assets/index.html').decode('utf8')
    addon=z.read('assets/bf053_monster_training.js').decode('utf8')
    assert addon.count('/* BF_ORIGINAL_MONSTER_TRAINING_V053 */')==1
    assert addon.count('__BF053_MANIFEST__')==1
    assert html.count('/* BF_ORIGINAL_MONSTER_TRAINING_V053 */')==1
    assert html.count('/* BF_MONSTER_TRAINING_HOOK_V053 */')==1
    assert html.count('/* BF_MONSTER_TRAINING_DRAW_V053 */')==1
    assert 'bf053_training_monsters.png' in html
    assert 'sourceArtOriginal:true' in html
    assert 'box.checked=false' in html
    assert 'bf_global_offline_demo_v7' in html
    assert '/* BF_MISTRAL_BOSS_HOOK_V052 */' in html
    assert '/* BF_TOWER_OF_MISTRAL_V051 */' in html
    assert len(z.read('assets/bf_home_nav.js'))<65536
print('PASS v0.53 Android APK: 0009–0016 original 2022 BF1 sprite atlas, optional training, prior combat + save v7')
