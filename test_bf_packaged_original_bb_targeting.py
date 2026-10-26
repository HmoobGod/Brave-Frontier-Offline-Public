"""Built APK must contain the verified target-scope patch and all 30 records."""
from pathlib import Path
import base64,gzip,hashlib,json,re,zipfile

ROOT=Path(__file__).resolve().parent
apk=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert apk.is_file(),apk
M=json.loads((ROOT/'source_data/bf_global_original_bb_targeting.json').read_text())
with zipfile.ZipFile(apk) as z:
    src=z.read('assets/index.html').decode('utf-8')
    assert src.count('/* BF_GLOBAL_BB_TARGETING_V028 */')==1
    assert src.count('const attackTargets=allEnemyBB?livingEnemies():[target];')==1
    assert 'prototypeDamage(effectivePlayerAtk(p),foe.def,bbDamageMultiplier(p,burst))' in src
    assert 'original single-enemy targeting' in src
    assert 'ORIGINAL ATK BOOST BASE' in src
    assert 'source Lv1 base healing range' in src
    assert 'bf_global_offline_demo_v7' in src
    match=re.search(r'const BF_VERIFIED_BB_SCOPES=Object.freeze\((\{.*?\})\);',src)
    assert match,'Missing v0.28 original BB scope index in compiled APK'
    compiled=json.loads(match.group(1))
    expected={k:{'name':v['name'],'target':v['target'],'skillId':v['skillId']}
              for k,v in M['targets'].items()}
    assert compiled==expected,'Game BB target classifications differ from archival source'
    assert len(compiled)==30
    assert len([x for x in compiled.values() if x['target']=='all_enemies'])==19
    assert len([x for x in compiled.values() if x['target']=='single_enemy'])==5
    assert len([x for x in compiled.values() if x['target']=='support'])==6
    assert 'assets/bf_global_unit_archive.js' in z.namelist()
    assert 'assets/bf_home_nav.js' in z.namelist()
print('PASS v0.28 APK includes exact archived Global BB scopes (19 AoE / 5 single / 6 support) and existing UI/save')
