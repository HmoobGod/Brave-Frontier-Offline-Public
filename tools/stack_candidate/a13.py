#!/usr/bin/env python3
"""A13: restore the public source-form lookup; explicit copy dispatch in owned consumers.
Inputs are pinned A12 prepared assets. No original generator block or test is edited.
"""
import hashlib,pathlib,re,sys
HERE=pathlib.Path(__file__).resolve().parent
BASELINE_LOOKUP='function effectiveUnit(baseId){return UNIT_BY_ID.get(P.evolutions[baseId]||baseId);}'
OLD='function effectiveUnit(baseId){const sourceId=ownedCopyBase(baseId,P[OWNED_COPY_META]);return sourceId===null?undefined:UNIT_BY_ID.get(P.evolutions[baseId]||sourceId);}'
NEW=BASELINE_LOOKUP+'''
// Copy ownership is resolved separately; never narrow the public catalogue lookup.
function stackOwnedUnit(id){
 if(typeof id==='number'&&id>=OWNED_COPY_FIRST||typeof id==='string'&&Number(id)>=OWNED_COPY_FIRST){
  if(!Number.isSafeInteger(id)||id>OWNED_COPY_LAST||!Array.isArray(P.roster)||!P.roster.includes(id))return undefined;
  const source=ownedCopyBase(id,P[OWNED_COPY_META]);
  return source===null?undefined:UNIT_BY_ID.get(P.evolutions[id]||source);
 }
 return effectiveUnit(id);
}'''
# All current external owned consumers, with pinned counts. A legacy fixture has
# no STACK resolver, so the original call remains live, including test stubs.
# Name, number of direct call sites. Do not alter typeof guards or source tests.
CONSUMERS={
 'bf10400_qol_evolution_needs.js':1,'bf11000_source_starter_leader_skills.js':1,
 'bf11100_original_starter_leader_combat.js':1,'bf11300_all_playable_leader_recipients.js':1,
 'bf11500_original_unit_level_caps.js':2,'bf11600_original_lord_stats_reference.js':2,
 'bf12600_original_squad_cost.js':1,'bf13000_original_starter_typed_evolution.js':3,
 'bf16600_original_type5_element_resist.js':1,'bf16800_original_level_one_lord_combat.js':1,
 'bf16900_optional_imp_fusion.js':1,'bf17200_original_max_level_lord_combat.js':1,
 'bf2000_story_battle_hud.js':1,'bf250_squad_training.js':1,'bf400_original_battle_dossier.js':1,
 'bf_home_battle_readiness_v420.js':1,'bf_home_nav.js':7,
 'bf_leader_critical_bonus.js':1,'bf_leader_defense_bypass.js':1,
}
ADAPTER="id=>id>=1e9&&typeof stackOwnedUnit==='function'?stackOwnedUnit(id):effectiveUnit(id)"
def one(s,a,b):
 if s.count(a)!=1:raise ValueError(('anchor',a[:100],s.count(a)))
 return s.replace(a,b,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readmanifest(p):return {n:h for h,n in (l.split() for l in p.read_text().splitlines() if l.strip())}
def transform(root):
 expected=readmanifest(HERE/'a12-hashes.txt')|readmanifest(HERE/'a13-extra-base-hashes.txt')
 for n,h in expected.items():
  if sha(root/n)!=h:raise ValueError('A12 input mismatch '+n)
 p=root/'index.html';s=p.read_text();s=one(s,OLD,NEW)
 s=one(s,'''// Read-only inspector fallback for archive-only form IDs; never used by ownership or combat.
function stackInspectorUnit(id){return effectiveUnit(id)||UNIT_BY_ID.get(id);}
function renderHitInspector(){
 const effectiveUnit=stackInspectorUnit;''','function renderHitInspector(){')
 # Only native owned paths before inspector; preserve original archive calls and
 # original v070 generator exact bytes. Native copy paths require this resolver.
 start=s.index('function ownedCopyRows(');end=s.index('function renderHitInspector(){')
 scope=s[start:end];scope,count=re.subn(r'\beffectiveUnit\(', 'stackOwnedUnit(',scope)
 if count!=12:raise ValueError(('native owned call inventory',count))
 s=s[:start]+scope+s[end:]
 if s.count(BASELINE_LOOKUP)!=1 or 'stackInspectorUnit' in s:raise ValueError('lookup contract')
 p.write_text(s)
 for n,count in CONSUMERS.items():
  p=root/n;s=p.read_text();s,k=re.subn(r'\beffectiveUnit\(', 'stackUnit(',s)
  if k!=count:raise ValueError((n,k,count))
  if n=='bf_home_nav.js':
   # Global function declaration, safe on repeated native injection; no const
   # redeclaration. All other modules scope the adapter inside their IIFE.
   s=one(s,'/* Offline home navigation pilot: display only; no save/engine changes. */',
       '/* Offline home navigation pilot: display only; no save/engine changes. */\nfunction stackUnit(id){return ('+ADAPTER+')(id)}')
  else:
   anchor="(() => {\n  'use strict';" if n=="bf_home_battle_readiness_v420.js" else "'use strict';"
   if s.count(anchor)!=1:raise ValueError(('strict anchor',n,s.count(anchor)))
   s=one(s,anchor,anchor+'\n const stackUnit='+ADAPTER+';')
  limit=131072 if n=='bf_home_nav.js' else 65536
  if len(s.encode())>limit:raise ValueError(('budget',n,len(s.encode()),limit))
  p.write_text(s)
 print('A13 restored baseline lookup, removed inspector shim, scoped copy dispatch across native owned paths and',len(CONSUMERS),'external modules')
if __name__=='__main__':transform(pathlib.Path(sys.argv[1]))
