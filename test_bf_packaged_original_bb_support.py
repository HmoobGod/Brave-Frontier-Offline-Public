"""v0.29 verify compiled Android APK retains source-backed BB support and v7 saves."""
from pathlib import Path
import json,re,zipfile
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'source_data/bf_global_original_bb_support_v029.json').read_text('utf-8'))
scopes=json.loads((ROOT/'source_data/bf_global_original_bb_targeting.json').read_text('utf-8'))['targets']
APK=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert APK.is_file(),f'Missing assembled APK {APK}'
with zipfile.ZipFile(APK) as apk:
    files=set(apk.namelist())
    html=apk.read('assets/index.html').decode('utf-8')
    assert html.count('/* BF_GLOBAL_BB_TARGETING_V028 */')==1
    assert html.count('/* BF_GLOBAL_BB_SUPPORT_V029 */')==1
    assert html.count('function effectivePlayerAtk(p)')==1
    assert 'bf_global_offline_demo_v7' in html
    assert 'function originalSupport(id)' in html
    m=re.search(r'const BF_VERIFIED_BB_SUPPORT=Object\.freeze\((\{.*?\})\);',html,re.S)
    assert m,'Missing source-backed support table inside APK'
    embedded=json.loads(m.group(1))
    assert set(embedded)==set(manifest['skills'])
    for id,v in embedded.items():
        original=manifest['skills'][id]
        assert scopes[id]['target']=='support'
        assert v['name']==original['name']
        effect=original['level1DemoEffect']
        assert v['kind']==effect['type']
        if v['kind']=='atk_buff_all':
            assert (v['pct'],v['rounds'])==(effect['pctAtLv1'],effect['roundsAtLv1'])
        else:assert (v['low'],v['high'])==(effect['lowAtLv1'],effect['highAtLv1'])
    assert 'assets/bf_home_nav.css' in files
    assert b'bf-atk-buff-status' in apk.read('assets/bf_home_nav.css')
    assert sum(n.startswith('assets/content/unit_archive/') and n.endswith('.png') for n in files)==127
print('PASS compiled Android APK: 6 original support BB Lv1 effects, buff badge, 127 original portraits and unchanged save key')
