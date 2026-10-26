"""v0.44 optional, explicitly experimental SBB combat prototype.

Original 2022 English names, all-foe targets and combo descriptions are from
the SHA-checked v0.43 lore archive. Prototype damage, hit spacing, BB=100
trigger and effects are NOT original SBB mechanics. OFF by default, not saved.
"""
from pathlib import Path
import json,base64,gzip,hashlib,re
ROOT=Path(__file__).resolve().parent
HTML=ROOT/'app/src/main/assets/index.html'
D=ROOT/'source_data'
s=HTML.read_text('utf8')
for tag in ['/* BF_GLOBAL_SBB_PREVIEW_V043 */','/* BF_COORDINATED_AUTO_V042 */',
            '/* BF_BATTLE_BB_GUIDE_V040 */']:
    assert s.count(tag)==1,tag
assert 'bf_global_offline_demo_v7' in s
meta=json.loads((D/'bf_global_original_lore_meta.json').read_text('utf8'))
gz=base64.b64decode((D/'bf_global_original_lore_codex.json.gz.b64').read_text('ascii'))
assert hashlib.sha256(gz).hexdigest()==meta['payloadGzipSha256']
raw=gzip.decompress(gz)
assert hashlib.sha256(raw).hexdigest()==meta['payloadJsonSha256']
records={u['id']:u for u in json.loads(raw)['units']}
ids={10015,20015,30015,40015,50015,60015,10025,20025,30025,40025,50025,60025}
assert len(ids)==12
for uid in ids:
    entry=records[uid]['sbb']
    assert entry['id']>0 and 'all enemies' in entry['description'].casefold()
    assert entry['name'] and entry['description']
MARK='/* BF_EXPERIMENTAL_SBB_V044 */'
old="const action=p.action;if(!action||p.hp<=0)return;"
new="""const action=p.action;if(!action||p.hp<=0)return;
 if(action.kind==='sbb_demo' && window.BF044SBBDemo?.perform){
   await window.BF044SBBDemo.perform(p,token);return;
 }"""
script=r"""
<style id="bf044-experimental-sbb-style">
#bf044-sbb-controls { padding:7px; margin:5px 0 8px; border:1px solid #74628f;
 border-radius:6px; background:#272035; color:#eee3fd; font-size:12px }
#bf044-sbb-controls label { display:flex; align-items:center; gap:6px; margin-bottom:7px }
#bf044-sbb-controls button { border:1px solid #aa8fcb; color:#fff; background:#4c356c;
 border-radius:5px; padding:6px; font:inherit; font-weight:bold }
#bf044-sbb-controls button:disabled{opacity:.4}
#bf044-sbb-controls small{display:block; margin-top:6px; line-height:1.4}
</style>
<script>
/* BF_EXPERIMENTAL_SBB_V044 */
(() => {
  'use strict';
  // Not authentic Global SBB mechanics. Source names/scopes/combo only.
  const toggleId='bf044-enable',buttonId='bf044-queue';
  const enabled=()=>document.getElementById(toggleId)?.checked===true;
  const sourceFor=id=>window.BF043SBBSource?.infoFor(id)||null;
  const selected=()=>typeof S!=='undefined' && Array.isArray(S.party)?S.party[S.selected]:null;
  function canQueue(){
    const p=selected();
    return !!(enabled() && p?.active && p.hp>0 && p.bb>=100 &&
      !p.action && !S.busy && !S.over && sourceFor(p.unitId));
  }
  function queue(){
    if(!canQueue())return false;
    const p=selected(),src=sourceFor(p.unitId);
    if(!src || src.target!=='all_enemies')return false;
    p.action={kind:'sbb_demo',target:S.target};
    msg(p.name+' queues '+src.name+' — EXPERIMENTAL DEMO SBB, not original charging or effect math.');
    const next=nextUnit();if(next!==null)S.selected=next;
    update();refresh();
    return true;
  }
  async function perform(p,token){
    const src=sourceFor(p?.unitId);
    if(!enabled() || !p?.active || !(p.hp>0) || !(p.bb>=100) ||
       src?.target!=='all_enemies'){
      // Fail closed to ordinary attack if the prototype was disabled or invalid
      // after queueing. Never spend gauge on a missing/unverified SBB.
      p.action={kind:'attack',target:p.action?.target??S.target};
      return await performUnit(p,token);
    }
    const targets=livingEnemies();
    if(!targets.length)return;
    // The source number of combos is descriptive. Repeating these many
    // DEMO ticks is not a restoration of original damage/animation frames.
    const hits=Number.isSafeInteger(src.combo) && src.combo>0 &&
      src.combo<=40 ? src.combo:1;
    const sequences=UNIT_BY_ID.get(p.unitId)?.animation?.atk;
    if(!Array.isArray(sequences))return;
    const damageBySlot=new Map(targets.map(foe=>{
      const total=prototypeDamage(effectivePlayerAtk(p),foe.def,
        bbDamageMultiplier(p,true));
      const base=Math.floor(total/hits);
      const damages=Array(hits).fill(base);
      for(let i=0;i<total-base*hits;i++)damages[i]++;
      return [foe.slot,damages];
    }));
    p.bb=0;
    changeAnim(p,'atk');
    msg(p.name+' uses EXPERIMENTAL SBB DEMO '+src.name+
      ' on '+targets.length+' foes; '+hits+
      ' SIMULATED hit tick(s), original Global effects and charging NOT restored.');
    let applied=0;
    for(let i=0;i<hits;i++){
      await wait(28/spd());
      if(token!==epoch)return;
      for(const foe of targets){
        const amount=damageBySlot.get(foe.slot)?.[i]||0;
        if(amount<=0 || foe.hp<=0)continue;
        const dealt=Math.min(amount,foe.hp);
        foe.hp-=dealt;applied+=dealt;
        const xy=xyEnemy[foe.slot];
        floatAt(xy[0]+(i%3-1)*8,xy[1]-33, dealt,'burst');
      }
      if(S.enemies[S.target]?.hp===0)
        S.target=livingEnemies()[0]?.slot??S.target;
      update();
    }
    msg('EXPERIMENTAL SBB DEMO dealt '+applied+
      ' prototype damage; no original SBB secondary effects applied.');
    if(token!==epoch)return;
    changeAnim(p,'idle');
    refresh();
  }
  function refresh(){
    const btn=document.getElementById(buttonId);
    if(!btn)return;
    const p=selected(),src=sourceFor(p?.unitId);
    btn.disabled=!canQueue();
    btn.textContent=src?'Queue DEMO SBB · '+src.name:'No verified SBB for selected unit';
  }
  function mount(){
    const host=document.getElementById('bf043-sbb-preview');
    if(!host || document.getElementById('bf044-sbb-controls'))return;
    const panel=document.createElement('div');panel.id='bf044-sbb-controls';
    const label=document.createElement('label');
    const check=document.createElement('input');
    check.id=toggleId;check.type='checkbox';check.checked=false;
    const copy=document.createElement('span');
    copy.textContent='Enable experimental SBB combat (DEMO)';
    label.append(check,copy);
    const button=document.createElement('button');button.id=buttonId;
    button.type='button';button.disabled=true;
    const note=document.createElement('small');
    note.textContent='Uses the existing 100% DEMO BB gauge, source SBB names and combo descriptions, and simulated hit timing/damage. Original SBB effects are NOT implemented. Option resets when the app closes.';
    panel.append(label,button,note);host.append(panel);
    check.addEventListener('change',refresh);
    button.addEventListener('click',queue);
    host.addEventListener('toggle',refresh);
    document.body.addEventListener('click',()=>queueMicrotask(refresh),true);
    document.body.addEventListener('change',()=>queueMicrotask(refresh),true);
    refresh();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});
  else mount();
  window.BF044SBBDemo=Object.freeze({enabled,sourceFor,canQueue,queue,perform,refresh});
})();
</script>
"""
if MARK in s:
    assert s.count(MARK)==1 and s.count(new)==1
    assert s.count('id="bf044-experimental-sbb-style"')==1
    print('PASS v0.44 existing SBB prototype intact')
else:
    assert s.count(MARK)==0 and s.count(old)==1,(MARK,s.count(old))
    assert s.count('</body>')==1
    s=s.replace(old,new,1).replace('</body>',script+'\n</body>',1)
    assert s.count(MARK)==1 and s.count(new)==1
    HTML.write_text(s,'utf8')
    print('PASS v0.44 optional SBB prototype; source combo/target only; original mechanics and save v7 untouched')
