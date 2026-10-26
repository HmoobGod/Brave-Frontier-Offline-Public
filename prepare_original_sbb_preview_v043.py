"""v0.43 — original Global six-star SBB source preview, not a playable skill.

Read-only reference from SHA-verified 2022 English lore; no invented gauge, hit
timing, multiplier or effects. Compatible with v7 save and old APK signature.
"""
from pathlib import Path
import base64, gzip, hashlib, json, re
ROOT=Path(__file__).resolve().parent
ASSET=ROOT/'app/src/main/assets/index.html'
DATA=ROOT/'source_data'
s=ASSET.read_text('utf8')
assert s.count('/* BF_COORDINATED_AUTO_V042 */')==1
assert s.count('/* BF_BATTLE_BB_GUIDE_V040 */')==1
assert 'bf_global_offline_demo_v7' in s
meta=json.loads((DATA/'bf_global_original_lore_meta.json').read_text('utf8'))
packed=base64.b64decode((DATA/'bf_global_original_lore_codex.json.gz.b64').read_text('ascii'))
assert hashlib.sha256(packed).hexdigest()==meta['payloadGzipSha256']
raw=gzip.decompress(packed)
assert hashlib.sha256(raw).hexdigest()==meta['payloadJsonSha256']
source=json.loads(raw)
assert source['stats']['sbb']>=860
units={u['id']:u for u in source['units']}
embedded=re.search(r'<script type="application/json" id="bf-original-unit-lore-data">(.*?)</script>',s,re.S)
assert embedded
archived={u['id']:u for u in json.loads(embedded.group(1))['units']}
ids=(10015,20015,30015,40015,50015,60015,10025,20025,30025,40025,50025,60025)
forms=[]
for path in ('bf_global_six_star_starters_v037.json','bf_global_other_six_star_v038.json'):
    forms.extend(map(int,json.loads((DATA/path).read_text('utf8'))['records']))
assert set(forms)==set(ids)
skills={}
for uid in ids:
    original=units[uid]
    assert archived[uid].get('sbb')==original.get('sbb'),uid
    skill=original['sbb']
    assert skill['id']!=0 and skill['name'] and skill['description']
    assert 'all enemies' in skill['description'].casefold(),uid
    combo=re.search(r'\b(\d+) combo\b',skill['description'],re.I)
    assert (combo is None)==(uid==60025)
    skills[str(uid)]={'unitId':uid,'skillId':skill['id'],'name':skill['name'],
                       'description':skill['description'],'target':'all_enemies',
                       'combo':int(combo.group(1)) if combo else None}
assert len(skills)==12 and len({x['skillId'] for x in skills.values()})==12
MARK='/* BF_GLOBAL_SBB_PREVIEW_V043 */'
js=r"""
<style id="bf043-sbb-preview-style">
#bf043-sbb-preview{box-sizing:border-box;width:100%;margin:4px 0 9px;padding:6px 9px;
 border:1px solid #776e91;border-radius:6px;background:#201c2b;color:#eee3fd;font-size:12px;line-height:1.35}
#bf043-sbb-preview summary{cursor:pointer;font-weight:700;color:#d7c6ff}
#bf043-sbb-preview p{margin:6px 0}
</style>
<script>
/* BF_GLOBAL_SBB_PREVIEW_V043 */
(() => {
  'use strict';
  // Original names, combo text and English descriptions ONLY.
  // SBB meter, charging, animations, status and effect formulas NOT decoded.
  const original=Object.freeze(__TABLE__);
  const key='bf043-sbb-preview';
  function infoFor(unitId){
    const id=Number(unitId);
    if(!Number.isSafeInteger(id) || id<1 || typeof UNIT_BY_ID==='undefined' ||
       !UNIT_BY_ID.has(id) || !Object.hasOwn(original,String(id)))return null;
    return {...original[String(id)]};
  }
  function current(){
    if(typeof S==='undefined' || !Array.isArray(S.party))return null;
    const idx=Number(S.selected);
    return Number.isSafeInteger(idx)?infoFor(S.party[idx]?.unitId):null;
  }
  function refresh(){
    const details=document.getElementById(key);
    if(!details || !details.open)return;
    const body=details.querySelector('.bf043-body');
    const skill=current();
    const lines=skill?[
      'Original SBB: '+skill.name+' · #'+skill.skillId,
      'Original Global description: '+skill.description,
      'Target: all enemies'+(skill.combo===null?'':' · '+skill.combo+' combo'),
      'REFERENCE ONLY — SBB is not playable. Native SBB charging, effects and gauge thresholds are not yet restored.'
    ]:['This selected unit has no verified playable six-star SBB preview in this build.'];
    const digest=JSON.stringify(lines);
    if(body.dataset.digest===digest)return;
    body.dataset.digest=digest;
    body.replaceChildren(...lines.map(line=>{
      const p=document.createElement('p');p.textContent=line;return p;
    }));
  }
  function mount(){
    if(document.getElementById(key))return;
    const prior=document.getElementById('bf040-bb-guide')||document.getElementById('burst');
    if(!prior)return;
    const root=document.createElement('details');root.id=key;
    const title=document.createElement('summary');
    title.textContent='ORIGINAL SBB · SOURCE PREVIEW (NOT PLAYABLE)';
    const body=document.createElement('div');body.className='bf043-body';
    root.append(title,body);root.addEventListener('toggle',refresh);
    prior.insertAdjacentElement('afterend',root);
    document.body.addEventListener('click',()=>queueMicrotask(refresh),true);
    document.body.addEventListener('change',()=>queueMicrotask(refresh),true);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});
  else mount();
  window.BF043SBBSource=Object.freeze({infoFor,refresh,count:Object.keys(original).length});
})();
</script>
"""
if MARK in s:
    assert s.count(MARK)==1 and s.count('id="bf043-sbb-preview-style"')==1
    assert 'window.BF043SBBSource=Object.freeze' in s
    print('PASS v0.43 source SBB preview already installed')
else:
    assert s.count(MARK)==0 and s.count('</body>')==1
    js=js.replace('__TABLE__',json.dumps(skills,separators=(',',':'),ensure_ascii=True).replace('</','<\\/'+'')) 
    s=s.replace('</body>',js+'\n</body>',1)
    assert s.count(MARK)==1
    ASSET.write_text(s,'utf8')
    print('PASS v0.43 original 12 six-star SBB names/target/combo references; v7 untouched')
