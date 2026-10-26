'''Rebuild v0.30 source-backed offensive BB Level 1-10 power manifest.

Requires the user's original mst-decoded.zip as an explicit command argument.
No network access. It asserts the exact 2022 archival source digest.
'''
from pathlib import Path
import sys,json,hashlib,zipfile
root=Path(__file__).resolve().parent.parent
target=root/'source_data/bf_global_original_bb_power_v030.json'
reference=json.loads(target.read_text('utf-8'))
source=Path(sys.argv[1]) if len(sys.argv)>1 else Path('mst-decoded.zip')
assert source.is_file(),f'Provide original Global archive: {source}'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
assert digest==reference['provenance']['mstZipSha256']
rows={}
with zipfile.ZipFile(source) as z:
    for path in z.namelist():
        if path.startswith('3-mst-translated/F_SKILL_LEVEL_MST_'):
            for r in json.loads(z.read(path)):
                rows.setdefault(r['bbId'],(r,path))
for uid,r in reference['skills'].items():
    raw,path=rows[uid]
    assert path==r['sourceTable'] and raw['activeSkillInfoByLevel']==r['rawLevelData']
    for i,segment in enumerate(raw['activeSkillInfoByLevel'].split('|'),1):
        primary=segment.split('@')[0]
        n,code,par=primary.split(':')
        values=[int(x) for x in par.split(',')]
        assert r['levels'][i-1]=={'level':i,'effectCode':int(code),'damageModifierPct':values[0],
                                   'otherUndecodedParams':values[1:]}
print(f'PASS original archive {digest}; verified {len(reference["skills"])} offensive BBs and 10 exact source levels each')
