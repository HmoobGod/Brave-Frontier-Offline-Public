"""v0.28: Restore source-verified Global BB target scope for existing 30 demo forms.

The unit's original target scope (all enemies / single foe / support) is proven
from the user-provided 2022 Global English skill archive. Actual damage, effects,
combo formulas, BB charging and enemy encounters are still clearly DEMO.

This patch is checked, additive, idempotent and fails closed if the original
combat source changes unexpectedly. It preserves save v7 without writing state.
"""
from __future__ import annotations
import base64,gzip,hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
M=json.loads((ROOT/'source_data/bf_global_original_bb_targeting.json').read_text('utf-8'))
assert M['schema']=='bf-global-original-bb-targets-2022-v1'
meta=json.loads((ROOT/'source_data/bf_global_original_lore_meta.json').read_text('utf-8'))
z=base64.b64decode((ROOT/'source_data/bf_global_original_lore_codex.json.gz.b64').read_text('ascii'))
assert hashlib.sha256(z).hexdigest()==meta['payloadGzipSha256']==M['provenance']['loreGzipSha256']
original=gzip.decompress(z)
assert hashlib.sha256(original).hexdigest()==meta['payloadJsonSha256']==M['provenance']['loreJsonSha256']
source={str(u['id']):u for u in json.loads(original)['units']}
records=M['targets']
assert len(records)==30
assert sum(v['target']=='all_enemies' for v in records.values())==19
assert sum(v['target']=='single_enemy' for v in records.values())==5
assert sum(v['target']=='support' for v in records.values())==6
for key,item in records.items():
    assert item['target'] in ('all_enemies','single_enemy','support')
    assert key.isdecimal() and source[key]['bb']['name']==item['name']
    assert source[key]['bb']['id']==item['skillId']
    assert source[key]['bb']['description']==item['description']
    desc=item['description'].casefold()
    if item['target']=='all_enemies': assert re.search(r'\ball enemies\b|\ball foes\b',desc)
    if item['target']=='single_enemy': assert re.search(r'\bsingle enemy\b|\bsingle foe\b',desc)
    if item['target']=='support': assert 'all allies' in desc

index=ASSETS/'index.html'
html=index.read_text('utf-8')
marker='/* BF_GLOBAL_BB_TARGETING_V028 */'
# Cross-check archived target metadata embedded in the older combat demo.
# Scope 2 in the original decoded BB area record corresponds to all enemies;
# 1@1 is the original single-enemy group. English descriptions must agree.
found=re.search(r'window\.BF_ARCHIVE_BB_HITS=(\{.*?\});',html,re.DOTALL)
assert found, 'Missing previous BB master table from demo source'
bb_master=json.loads(found.group(1))
extra=set(bb_master)-set(records)
expected_new={'10042','20042','30042','40042','50042','60042'}
assert set(records).issubset(bb_master),'Original 30 audited BB entries have been lost'
assert not extra or (
    ('/* BF_GLOBAL_SIX_EVOLUTIONS_V032 */' in html and extra==expected_new) or
    ('/* BF_GLOBAL_SECOND_EVOLUTIONS_V033 */' in html and
     extra==expected_new|{'10013','20013','30013','40013','50013','60023'}) or
    ('/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */' in html and
     extra==expected_new|{'10013','20013','30013','40013','50013','60023'}|{'60013','10023','20023','30023','40023','50023'}) or
    ('/* BF_GLOBAL_FIVE_STAR_STARTERS_V035 */' in html and
     extra==expected_new|{'10013','20013','30013','40013','50013','60023'}|{'60013','10023','20023','30023','40023','50023'}|{'10014','20014','30014','40014','50014','60014'}) or
    ('/* BF_GLOBAL_OTHER_FIVE_STAR_V036 */' in html and
     extra==expected_new|{'10013','20013','30013','40013','50013','60023'}|{'60013','10023','20023','30023','40023','50023'}|{'10014','20014','30014','40014','50014','60014'}|{'10024','20024','30024','40024','50024','60024'}) or
    ('/* BF_GLOBAL_SIX_STAR_STARTERS_V037 */' in html and
     extra==expected_new|{'10013','20013','30013','40013','50013','60023'}|{'60013','10023','20023','30023','40023','50023'}|{'10014','20014','30014','40014','50014','60014'}|{'10024','20024','30024','40024','50024','60024'}|{'10015','20015','30015','40015','50015','60015'}) or
    ('/* BF_GLOBAL_OTHER_SIX_STAR_V038 */' in html and
     extra==expected_new|{'10013','20013','30013','40013','50013','60023'}|{'60013','10023','20023','30023','40023','50023'}|{'10014','20014','30014','40014','50014','60014'}|{'10024','20024','30024','40024','50024','60024'}|{'10015','20015','30015','40015','50015','60015'}|{'10025','20025','30025','40025','50025','60025'})
),('Unknown unaudited BB entries in source',extra)
# Verify the original 30 records against their historic source manifest below;
# v0.32 separately verifies each of the exactly six new entries.
for unit_id,item in records.items():
    row=bb_master[unit_id]
    assert row['bbId']==item['skillId']
    if item['target']=='all_enemies':
        assert row['targetAreaRaw']=='2' and row['offensiveCandidate'] is True
    elif item['target']=='single_enemy':
        assert row['targetAreaRaw']=='1@1' and row['offensiveCandidate'] is True
    else:
        assert row['offensiveCandidate'] is False

# Names are static source strings; never user input. Avoid duplicating lore prose
# in executable JS; the full descriptions remain in the read-only codex JSON.
safe={key:{'name':val['name'],'target':val['target'],'skillId':val['skillId']}
      for key,val in records.items()}
source_literal=json.dumps(safe,ensure_ascii=True,separators=(',',':')).replace('</','<\\/')
constant='''/* BF_GLOBAL_BB_TARGETING_V028 */
// Only target area and names are original. Effects, damage and charge remain DEMO.
const BF_VERIFIED_BB_SCOPES=Object.freeze(__SOURCE_LITERAL__);
const bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||null;
window.BFOriginalBBTargets=Object.freeze({
 get count(){return Object.keys(BF_VERIFIED_BB_SCOPES).length;},
 get allEnemyCount(){return Object.values(BF_VERIFIED_BB_SCOPES).filter(x=>x.target==='all_enemies').length;},
 scopeFor:id=>bfOriginalBB(id)?.target||null,
 skillFor:id=>bfOriginalBB(id)?.name||null
});
'''.replace('__SOURCE_LITERAL__',source_literal)

old1='''function prototypeDamage(atk,def,mult=1){return Math.max(1,Math.round((atk*.62-def*.18)*mult*(.96+rand()*.08)))}'''
new1=constant+old1
old2=''' const bbProfile=burst?window.BF_ARCHIVE_BB_HITS[String(p.unitId)]:null;
 const isDemoSupport=burst&&bbProfile?.offensiveCandidate===false;
 const target=isDemoSupport?null:pickTarget(action.target);'''
new2=''' const bbProfile=burst?window.BF_ARCHIVE_BB_HITS[String(p.unitId)]:null;
 const bbOriginal=burst?bfOriginalBB(p.unitId):null;
 const isDemoSupport=burst&&bbProfile?.offensiveCandidate===false;
 // Archived English description and area MST agree for all 19 AoE demo forms.
 // Buff/healing support remains a labeled demo fallback, never fabricated.
 const allEnemyBB=burst&&!isDemoSupport&&bbOriginal?.target==='all_enemies';
 const target=isDemoSupport?null:pickTarget(action.target);'''
old3='''  msg(`${p.name} activates DEMO SUPPORT BB (skillType ${bbProfile.skillTypeRaw} / targetType ${bbProfile.targetTypeRaw}; true effect not decoded).`);'''
new3='''  msg(`${p.name} activates ${bbOriginal?.name||'BB'} — DEMO SUPPORT fallback (skillType ${bbProfile.skillTypeRaw} / targetType ${bbProfile.targetTypeRaw}; original support effect not applied).`);'''
old4=''' const totalDamage=prototypeDamage(p.atk,target.def,burst?2.1:1);
 const damages=splitDemoDamage(totalDamage,strikes);
 if(burst){p.bb=0;msg(`${p.name} activates DEMO BB ${bbProfile?.bbId||''} (${events?'first archived hit group':'simulated fallback'}).`)}
 let lastTick=0,applied=0;
 for(let i=0;i<strikes.length;i++){
  const [tick]=strikes[i],delay=Math.max(0,tick-lastTick)*1000/BF_HIT_TICKS_PER_SECOND_UNVERIFIED/spd();
  await wait(delay);if(token!==epoch)return;
  const damage=damages[i]||0;
  if(target.hp>0&&damage>0){
   const actual=Math.min(target.hp,damage);
   target.hp=Math.max(0,target.hp-damage);applied+=actual;
   const [x,y]=xyEnemy[target.slot];floatAt(x+(i%3-1)*9,y-36-(i%2)*11,actual,burst?'burst':'');
   effects.push({x,y:y-24,at:clock(),life:360/spd(),color:burst?'#8ddbff':'#fbe2a0',isBurst:burst});
  }
  if(target.hp===0)S.target=livingEnemies()[0]?.slot??target.slot;
  update();lastTick=tick;
 }
 if(!burst)p.bb=Math.min(100,p.bb+34); // DEMO BB gauge, NOT original BC drops.
 msg(`${p.name} ${burst?'uses DEMO BB on':'attacks'} ${target.name}: ${applied} applied demo damage across ${strikes.length} ${burst?(events?'archived-timed BB events (demo formula)':'simulated BB event'):'archived-timed event'+(strikes.length===1?'':'s')}.`);'''
new4=''' // An original all-enemy BB hits EVERY living foe at each archived event.
 // Damage is still the prototype formula; it is computed independently using
 // each enemy's demo DEF. No original multiplier or BC logic is inferred.
 const attackTargets=allEnemyBB?livingEnemies():[target];
 const damageByTarget=new Map(attackTargets.map(foe=>[
  foe.slot,splitDemoDamage(prototypeDamage(p.atk,foe.def,burst?2.1:1),strikes)
 ]));
 if(burst){
  p.bb=0;
  msg(`${p.name} activates ${bbOriginal?.name||'DEMO BB'} — ${allEnemyBB?'original all-enemy targeting':bbOriginal?.target==='single_enemy'?'original single-enemy targeting':'single-target DEMO fallback'}; ${events?'original hit timing':'fallback timing'}, DEMO damage/effects.`);
 }
 let lastTick=0,applied=0;
 for(let i=0;i<strikes.length;i++){
  const [tick]=strikes[i],delay=Math.max(0,tick-lastTick)*1000/BF_HIT_TICKS_PER_SECOND_UNVERIFIED/spd();
  await wait(delay);if(token!==epoch)return;
  for(const foe of attackTargets){
   const damage=damageByTarget.get(foe.slot)?.[i]||0;
   if(foe.hp<=0||damage<=0)continue;
   const actual=Math.min(foe.hp,damage);
   foe.hp=Math.max(0,foe.hp-damage);applied+=actual;
   const [x,y]=xyEnemy[foe.slot];floatAt(x+(i%3-1)*9,y-36-(i%2)*11,actual,burst?'burst':'');
   effects.push({x,y:y-24,at:clock(),life:360/spd(),color:burst?'#8ddbff':'#fbe2a0',isBurst:burst});
  }
  if(S.enemies[S.target]?.hp===0)S.target=livingEnemies()[0]?.slot??S.target;
  update();lastTick=tick;
 }
 if(!burst)p.bb=Math.min(100,p.bb+34); // DEMO BB gauge, NOT original BC drops.
 msg(`${p.name} ${burst?'uses DEMO BB on':'attacks'} ${allEnemyBB?attackTargets.length+' foes':target.name}: ${applied} applied DEMO damage across ${strikes.length} ${burst?(events?'archived-timed BB events':'simulated BB event'):'archived-timed event'+(strikes.length===1?'':'s')}.`);'''
old5='''msg(`${p.name}: ${kind==='burst'?'Brave Burst':kind==='guard'?'Guard':'Attack'} queued.`);'''
new5='''msg(`${p.name}: ${kind==='burst'?'Brave Burst'+(bfOriginalBB(p.unitId)?' · '+bfOriginalBB(p.unitId).name+' (original name; demo effects)':''):kind==='guard'?'Guard':'Attack'} queued.`);'''

replacements=[(old1,new1),(old2,new2),(old3,new3),(old4,new4),(old5,new5)]
if marker in html:
    assert html.count(marker)==1 and 'original all-enemy targeting' in html
    print('Verified existing source-backed BB targeting patch; no changes.')
else:
    for old,new in replacements:
        assert html.count(old)==1,('Combat patch anchor missing or duplicated',old[:90],html.count(old))
        html=html.replace(old,new,1)
    assert marker in html
    index.write_text(html,'utf-8')
    print('PASS v0.28: original Global BB targeting restored for 19 AoE / 5 single / 6 support records; formulas remain DEMO.')
