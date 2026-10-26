"""v0.63–0.65: stage original 2022 normal-hit frames for 72 playable forms.

Only the archived four-number frame/weight tuples are original. Gameplay
still uses DEMO damage and the UNVERIFIED 60 ticks/s playback assumption.
The unit with a 130% total is excluded rather than normalized to 100.
No save/state writes and no new unit ownership.
"""
from pathlib import Path
import json, re

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
source=json.loads((ROOT/'source_data/bf_global_playable_attack_frames_v061.json').read_text('utf-8'))
assert source['schema']=='bf-global-playable-original-normal-hit-frames-v061'
pr=source['provenance']
assert pr['archiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert [p['sha256'] for p in pr['masterParts']]==[
 '1146f09489a07b9187cd3f04bf7dc3ef3bb74e35385869534671af95bf8ea645',
 '0696ccda59fccf48598c5267eaeb8a306e994618384151cead38cec6a9195b2b']
rows=source['rows']
assert len(rows)==72 and len({r['unitId'] for r in rows})==72
assert [r['unitId'] for r in rows]==sorted(r['unitId'] for r in rows)
assert set(str(r['unitId'])[:1] for r in rows)==set('123456')
assert all(r['unitId']>=10011 for r in rows)
counts={}
for row in rows:
  raw=row['damageFrames']
  assert re.fullmatch(r'\d+:\d+:\d+:\d+(?:,\d+:\d+:\d+:\d+)*',raw)
  frames=[[int(v) for v in a.split(':')] for a in raw.split(',')]
  assert frames and all(len(ev)==4 and all(v>=0 for v in ev) for ev in frames)
  assert frames==sorted(frames,key=lambda x:x[0]),row['unitId']
  counts[row['unitId']]=sum(ev[1] for ev in frames)
assert len([v for v in counts.values() if v==100])==71
assert {id:weight for id,weight in counts.items() if weight!=100}=={10023:130}
for uid in (10011,20011,30011,40011,50011,60011):
  assert uid in counts and counts[uid]==100

addon=(ASSETS/'bf062_playable_attack_frames.js').read_text('utf-8')
assert addon.count('/* BF_PLAYABLE_ORIGINAL_HITS_V062 */')==1
assert addon.count('__BF_PLAYABLE_ATTACK_FRAMES__')==1
assert 'localStorage' not in addon
assert 'bf_global_offline_demo_v7' not in addon
encoded=json.dumps(source,separators=(',',':'),ensure_ascii=True).replace('<',r'\u003c')
js=addon.replace('__BF_PLAYABLE_ATTACK_FRAMES__',encoded)
assert '</script' not in js.lower()
html=ASSETS/'index.html'
s=html.read_text('utf-8')
assert 'bf_global_offline_demo_v7' in s
assert s.count('window.BF_ARCHIVE_NORMAL_HITS=')==1
assert s.count('const BF_HIT_TICKS_PER_SECOND_UNVERIFIED=60;')==1
assert s.count('/* BF_ORIGINAL_MISSION_INSPECTOR_STAGED_V060 */')==1
original=re.search(r'window\.BF_ARCHIVE_NORMAL_HITS=(\{[^;]+\});',s)
assert original, 'missing six original frame records'
base=json.loads(original.group(1))
assert len(base)==30,'existing source-backed hit profiles must be preserved'
byid={str(q['unitId']):q['damageFrames'] for q in rows}
for id,entry in base.items():
  assert entry['raw']==byid[id],('existing hit-profile mismatch',id)
  assert entry['weightsTotal']==100,('existing weights altered',id)
marker='/* BF_EXTENDED_PLAYABLE_ATTACK_FRAMES_V065 */'
if marker in s:
    assert s.count(marker)==1 and s.count(js)==1
    print('PASS v0.65 playable original hit frame extension already staged')
else:
    assert s.count(js)==0 and s.count(marker)==0
    anchor='const BF_HIT_TICKS_PER_SECOND_UNVERIFIED=60;'
    # Parse the all-72 source data only after the base 6 are established;
    # lookup helper is present before any original normal attack plays.
    s=s.replace(anchor,marker+js+'\n'+anchor,1)
    assert s.count(marker)==s.count(js)==1
    html.write_text(s,'utf-8')
    print('PASS v0.65 original hit frames for 71 playable units, exclude 10023 130%, v7 unchanged')
