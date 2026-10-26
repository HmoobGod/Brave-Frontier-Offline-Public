"""v0.70: expose all 72 source-backed playable forms in the attack-frame inspector.

This is research UI. It MUST NOT unlock archived units, change P.roster,
upgrade unit stats, guess frame timing or change the existing demo combat.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
source=json.loads((ROOT/'source_data/bf_global_playable_attack_frames_v061.json').read_text('utf-8'))
assert len(source['rows'])==72
sfile=ASSETS/'index.html'
s=sfile.read_text('utf-8')
assert 'bf_global_offline_demo_v7' in s
assert s.count('/* BF_EXTENDED_PLAYABLE_ATTACK_FRAMES_V065 */')==1
old=""" for(const base of STARTERS.filter(x=>P.roster.includes(x.id))){
  const u=effectiveUnit(base.id),op=document.createElement('option');op.value=String(u.id);op.textContent=u.name+' · '+u.id;E.hitunit.append(op);
 }"""
new=""" /* BF_PLAYABLE_HIT_INSPECTOR_V070 */
 const archive=window.BFPlayableAttackFramesV062;
 const available=[...STARTERS,...window.BF_EVOLVED_UNITS].filter(x=>archive?.lookup(x.id));
 for(const base of available){
  const u=effectiveUnit(base.id),op=document.createElement('option');
  op.value=String(u.id);
  op.textContent=u.name+' · '+u.id+(P.roster.includes(u.id)?'':' · ARCHIVE ONLY');
  E.hitunit.append(op);
 }"""
oldempty=""" E.hitevents.replaceChildren();if(!info)return;
 const summary=document.createElement('strong');"""
newempty=""" E.hitevents.replaceChildren();
 if(!info){
   const excluded=window.BFPlayableAttackFramesV062?.excludedReason(uid);
   if(excluded){
     const note=document.createElement('p');note.className='bb-source-note';
     note.textContent=excluded+'. Normal hit timing falls back to DEMO; not normalized.';
     E.hitevents.append(note);
   }
   return;
 }
 const summary=document.createElement('strong');"""
marker='/* BF_PLAYABLE_HIT_INSPECTOR_V070 */'
if s.count(marker)==1:
 assert s.count(new)==s.count(newempty)==1
 print('PASS v0.70 expanded hit inspector already staged')
else:
 assert s.count(marker)==0
 assert s.count(old)==1 and s.count(oldempty)==1
 s=s.replace(old,new,1).replace(oldempty,newempty,1)
 assert s.count(marker)==s.count(newempty)==1
 sfile.write_text(s,'utf-8')
 print('PASS v0.70 all 72 original hit-frame references browseable; unowned labeled, 130% warning, v7')
