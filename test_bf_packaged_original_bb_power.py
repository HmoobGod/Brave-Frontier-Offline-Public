'''Verify compiled APK has all 24 source-matched Global offensive BB Lv1 modifiers.'''
from pathlib import Path
import json,re,zipfile
ROOT=Path(__file__).resolve().parent
APK=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
M=json.loads((ROOT/'source_data/bf_global_original_bb_power_v030.json').read_text('utf-8'))['skills']
assert len(M)==24
with zipfile.ZipFile(APK) as apk:
    html=apk.read('assets/index.html').decode('utf-8')
    nav=apk.read('assets/bf_home_nav.js')
    archive=apk.read('assets/bf_global_unit_archive.js')
    assert html.count('/* BF_GLOBAL_BB_TARGETING_V028 */')==1
    assert html.count('/* BF_GLOBAL_BB_SUPPORT_V029 */')==1
    assert html.count('/* BF_GLOBAL_BB_POWER_V030 */')==1
    assert 'prototypeDamage(effectivePlayerAtk(p),foe.def,bbDamageMultiplier(p,burst))' in html
    assert 'bf_global_offline_demo_v7' in html
    pattern=r'const BF_ORIGINAL_BB_POWER=Object\.freeze\((\{.*?\})\);'
    record=re.search(pattern,html,re.S)
    assert record,'No archived offensive BB power table in final APK'
    data=json.loads(record.group(1))
    assert len(data)==24
    for unit,power in data.items():
        source=M[unit]
        assert power['base']==source['levels'][0]['damageModifierPct']
        assert power['levels']==[x['damageModifierPct'] for x in source['levels']]
        assert power['target']==source['target']
    assert b'bf-codex-bb-levels' in archive
    assert len(nav)<=65536 and len(archive)<=65536
    images=[x for x in apk.namelist() if x.startswith('assets/content/unit_archive/') and x.endswith('.png')]
    assert len(images)==127
print('PASS APK contains all 24 original Global Lv1 offensive BB modifiers, levels 2–10, archive UI and save v7')
