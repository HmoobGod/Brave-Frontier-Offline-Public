"""v0.60: idempotent, read-only recovery of raw 2022 Mistral mission metadata.

Does not infer enemy-wave assignments, native reward meanings, mimic chances,
monster sprite IDs, battle math, AI or cutscene availability.
Keeps save v7 and every existing game option untouched.
"""
from pathlib import Path
import json,subprocess,sys

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
subprocess.run([sys.executable,str(ROOT/'verify_original_mistral_evidence_v059.py')],check=True)
source=json.loads((ROOT/'source_data/bf_global_mistral_raw_mission_evidence_v056.json').read_text('utf-8'))
encoded=json.dumps(source,ensure_ascii=True,separators=(',',':')).replace('<',r'\u003c')
loader=(ASSETS/'bf057_mission_evidence.js').read_text('utf-8')
inspector=(ASSETS/'bf058_mission_inspector.js').read_text('utf-8')
assert loader.count('/* BF_ORIGINAL_MISSION_EVIDENCE_V057 */')==1
assert inspector.count('/* BF_ORIGINAL_MISSION_INSPECTOR_V058 */')==1
assert loader.count('__BF_MISSION_EVIDENCE_ROWS__')==1
assert 'localStorage' not in loader and 'localStorage' not in inspector
script=loader.replace('__BF_MISSION_EVIDENCE_ROWS__',encoded)
assert '</script' not in script.lower() and '</script' not in inspector.lower()

html=ASSETS/'index.html'
s=html.read_text('utf-8')
for original in ('/* BF_TOWER_BOSS_FORMATION_HOOK_V055 */',
                 '/* BF_MONSTER_TRAINING_HOOK_V053 */',
                 '/* BF_MISTRAL_BOSS_HOOK_V052 */',
                 '/* BF_TOWER_OF_MISTRAL_V051 */'):
    assert s.count(original)==1,original
assert 'bf_global_offline_demo_v7' in s
assert s.count('</script><!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->')==1
marker='/* BF_ORIGINAL_MISSION_INSPECTOR_STAGED_V060 */'
if s.count(marker)==1:
    assert s.count(script)==s.count(inspector)==1
    assert s.count('/* BF_ORIGINAL_MISSION_EVIDENCE_V057 */')==1
    assert s.count('/* BF_ORIGINAL_MISSION_INSPECTOR_V058 */')==1
    print('PASS v0.60 original mission evidence already staged; idempotent')
else:
    assert s.count(marker)==s.count(script)==s.count(inspector)==0
    assert s.count('/* BF_ORIGINAL_MISSION_EVIDENCE_V057 */')==0
    assert s.count('/* BF_ORIGINAL_MISSION_INSPECTOR_V058 */')==0
    boundary='</script><!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->'
    replacement='</script><script>'+marker+script+'</script><script>'+inspector+'</script><!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->'
    s=s.replace(boundary,replacement,1)
    assert s.count(marker)==s.count(script)==s.count(inspector)==1
    html.write_text(s,'utf-8')
    print('PASS v0.60 34 source-backed opaque quest references staged; no combat/save changes')
