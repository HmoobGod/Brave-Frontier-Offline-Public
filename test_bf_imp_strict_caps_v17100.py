"""v171 source-proof: 2291 original Imp cap forms, strictly <=125% QoL round-down."""
from pathlib import Path
import re,base64,struct
R=Path(__file__).resolve().parent
src=(R/'app/src/main/assets/bf_global_unit_archive.js').read_text('utf8')
engine=(R/'app/src/main/assets/bf16900_optional_imp_fusion.js').read_text('utf8')
assert 'Math.max(n,Math.floor((n*5/4)/steps[i])*steps[i])' in engine
assert 'Math.round((n*1.25)/steps[i])' not in engine
which=base64.b64decode(re.search(r"const which=atob\('([A-Za-z0-9+/=]+)'\)",src).group(1))
table=base64.b64decode(re.search(r"const data=atob\('([A-Za-z0-9+/=]+)'\)",src).group(1))
assert len(which)==2291 and len(table)==147*8
patterns=[struct.unpack_from('>4H',table,8*i) for i in range(147)]
caps=[patterns[x] for x in which]
count=0;strict=0;zero=0
for item in caps:
 if not any(item):zero+=1
 for i,n in enumerate(item):
  step=(50,20,20,20)[i]
  target=max(n,(n*5//4//step)*step) if n else 0
  assert n<=target<=n*1.25,(n,target,i)
  if target<n*1.25:strict+=1
  count+=1
assert count==2291*4 and zero==129
assert max(500,(500*5//4//50)*50)==600 # old nearest became 650
assert max(120,(120*5//4//20)*20)==140 # old nearest became 160
assert all(max(x,(x*5//4//step)*step)==0 for x,step in zip((0,0,0,0),(50,20,20,20)))
print('PASS v171 2291 original Imp cap profiles, 9164 source fields, strict <=125%, 129 zero forms')
