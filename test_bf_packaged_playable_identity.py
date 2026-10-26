"""Verify v0.31 Global playable identities in the assembled Android APK."""
import json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'source_data/bf_global_original_playable_identity_v031.json').read_text())
APK=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert APK.is_file(),APK
with zipfile.ZipFile(APK) as apk:
    src=apk.read('assets/index.html').decode('utf-8')
    assert src.count('/* BF_ORIGINAL_GLOBAL_PLAYABLE_IDENTITY_V031 */')==1
    literal=re.search(r'const BF_ORIGINAL_PLAYABLE_IDENTITY=Object\.freeze\((\{.*?\})\);',src,re.S)
    assert literal,'Missing original playable identity in compiled APK'
    actual=json.loads(literal.group(1))
    assert actual==manifest['records']
    assert len(actual)==30
    assert actual['10011']['name']=='Fencer Vargas'
    assert actual['40021']['name']=='Advisor Weiss'
    assert actual['60022']['name']=='Samurai Mifune'
    assert actual['10012']['name']=='Burning Vargas'
    assert 'Original cap Lv.' in src and 'Original cost ' in src
    assert 'function playerUnit(' in src and 'bf_global_offline_demo_v7' in src
    assert 'function effectivePlayerAtk(' in src
    assert 'const BF_ORIGINAL_BB_POWER' in src and 'const BF_VERIFIED_BB_SUPPORT' in src
    paths=apk.namelist()
    assert sum(n.startswith('assets/content/unit_archive/') and n.endswith('.png') for n in paths)==127
    assert 'assets/bf_home_nav.js' in paths and len(apk.read('assets/bf_home_nav.js'))<=65536
print('PASS compiled v0.31 APK: 30 verified original Global names, original levels/costs, saved BB mechanics and archive portraits')
