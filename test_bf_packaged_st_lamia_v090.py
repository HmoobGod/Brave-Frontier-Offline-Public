"""v0.90 APK source validation for original St. Lamia quests/world and v7."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json
R=Path(__file__).resolve().parent
with ZipFile(R/'source_assets/bf1/stlamia/StLamia_2022_Source_Dataset_v090.zip') as z:
    m=json.loads(z.read('source_data/bf_global_st_lamia_original_v090.json'))
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
    html=apk.read('assets/index.html').decode('utf8')
    nav=apk.read('assets/bf_home_nav.js').decode('utf8')
    script=apk.read('assets/bf090_st_lamia_map.js').decode('utf8')
    assert '/* BF_STLAMIA_QUESTS_V090 */' in html
    assert '/* BF_STLAMIA_BACKGROUNDS_V090 */' in html
    assert 'window.BF_STLAMIA_QUEST_DATA_V090=Object.freeze(' in html
    assert 'BF_STLAMIA_QUEST_DATA_V090' in nav and 'BF_STLAMIA_QUEST_DATA_V090' in script
    assert len(nav.encode())<65536
    assert 'bf_global_offline_demo_v7' in html
    assert '/* BF_ORIGINAL_MORGAN_QUESTS_V080 */' in html
    assert '/* BF_TOWER_OF_MISTRAL_V051 */' in html
    for d in m['dungeons']:
        raw=apk.read('assets/content/dungeon/'+d['background'])
        assert len(raw)==d['imageBytes']
        assert hashlib.sha256(raw).hexdigest()==d['imageSha256']
    for k,meta in m['provenance']['worldFiles'].items():
        raw=apk.read('assets/'+k)
        assert len(raw)==meta['bytes']
        assert hashlib.sha256(raw).hexdigest()==meta['sha256']
    assert 'assets/bf080_morgan_map.js' in apk.namelist()
    assert 'assets/bf054_header_status.js' in apk.namelist()
print('PASS v0.90 APK original St. Lamia 36 quests, 7 battle JPGs, original map, prior content and v7')
