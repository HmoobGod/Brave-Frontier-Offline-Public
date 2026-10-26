"""Apply BF Global 2022 original support-BB effect classes to existing demo battle.

Six exact original records (Lv1 only); ATK buff values and 3-turn duration
come from F_SKILL_LEVEL_MST. Heal 600..800 is archived BASE RANGE only:
unknown REC modifiers and other original formula components are NOT applied.
Damage, wave composition, BC logic, enemy AI and save schema stay unchanged.

Idempotent; fail closed if v0.28 source anchors or provenance differs.
"""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'source_data'
HTML=ROOT/'app/src/main/assets/index.html'

support=json.loads((SRC/'bf_global_original_bb_support_v029.json').read_text('utf-8'))
old=json.loads((SRC/'bf_global_original_bb_targeting.json').read_text('utf-8'))
assert support['schema']=='bf-global-original-bb-support-v029'
assert support['provenance']['mstZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
ids={'20041','30041','40021','40022','40041','50041'}
assert set(support['skills'])==ids
compact={}
for sid,s in support['skills'].items():
    recorded=old['targets'][sid]
    assert recorded['target']=='support'
    assert s['name']==recorded['name'] and s['description']==recorded['description']
    assert s['skillId']==recorded['skillId']==int(sid)
    lines=s['rawLevelData'].split('|')
    assert len(lines)==len(s['levels'])==10
    for i,(line,lvl) in enumerate(zip(lines,s['levels'])):
        num,code,params=line.split(':')
        assert lvl=={'level':i+1,'effectCode':int(code),'params':[int(x) for x in params.split(',')]}
    first=s['levels'][0]
    effect=s['level1DemoEffect']
    if sid in ('40021','40022'):
        expected=(1300,30) if sid=='40021' else (1600,40)
        assert first['effectCode']==expected[0]
        assert first['params']==[0,expected[1],0,0,0,3,90]
        assert effect=={'type':'atk_buff_all','pctAtLv1':expected[1],'roundsAtLv1':3}
    else:
        assert first['effectCode']==1500 and first['params']==[600,800,50,50]
        assert effect=={'type':'heal_all','lowAtLv1':600,'highAtLv1':800,'recParamsNotDecoded':[50,50]}
    compact[sid]={'name':s['name'],'kind':effect['type']}
    if effect['type']=='atk_buff_all':compact[sid].update(pct=effect['pctAtLv1'],rounds=effect['roundsAtLv1'])
    else:compact[sid].update(low=effect['lowAtLv1'],high=effect['highAtLv1'])

html=HTML.read_text('utf-8')
assert html.count('/* BF_GLOBAL_BB_TARGETING_V028 */')==1
assert 'bf_global_offline_demo_v7' in html
marker='/* BF_GLOBAL_BB_SUPPORT_V029 */'
if marker in html:
    assert html.count(marker)==1
    assert 'BFOriginalSupportEffects' in html
    assert 'source Lv1 base healing range' in html
    print('PASS existing source-verified BB support patch is intact; no changes.')
else:
    patch_constant='''/* BF_GLOBAL_BB_SUPPORT_V029 */
// 2022 original F_SKILL_LEVEL_MST: skill type, ATK boost and Lv1 base heal.
// Runtime expiry/stacking and heal REC contribution remain DEMO approximations.
const BF_VERIFIED_BB_SUPPORT=Object.freeze(__DATA__);
function originalSupport(id){return BF_VERIFIED_BB_SUPPORT[String(id)]||null;}
function currentAtkBoost(p){return p.atkBuff && p.atkBuff.untilRound>=S.round?p.atkBuff.pct:0;}
function effectivePlayerAtk(p){return Math.round(p.atk*(1+currentAtkBoost(p)/100));}
window.BFOriginalSupportEffects=Object.freeze({
  ids:Object.freeze(Object.keys(BF_VERIFIED_BB_SUPPORT).map(Number)),
  forUnit:id=>originalSupport(id),
  boostForSlot:i=>S?.party[i]?currentAtkBoost(S.party[i]):0
});
'''.replace('__DATA__',json.dumps(compact,ensure_ascii=True,separators=(',',':')))
    before1='function prototypeDamage(atk,def,mult=1){return Math.max(1,Math.round((atk*.62-def*.18)*mult*(.96+rand()*.08)))}'
    after1=patch_constant+before1
    before2="// UNVERIFIED DEMO behavior; archived skillType/targetType are not decoded skill semantics.\nconst BF_DEMO_SUPPORT_MODE='heal'; // 'heal' or 'none'\nconst BF_DEMO_SUPPORT_REC_MULTIPLIER=3;"
    after2="// Only six vetted support BB records receive Lv1 source-backed base values.\n// Remaining BB level scaling/REC modifiers and status stacking are DEMO."
    before3='''  msg(`${p.name} activates ${bbOriginal?.name||'BB'} — DEMO SUPPORT fallback (skillType ${bbProfile.skillTypeRaw} / targetType ${bbProfile.targetTypeRaw}; original support effect not applied).`);
  await wait(effectTick*1000/BF_HIT_TICKS_PER_SECOND_UNVERIFIED/spd());if(token!==epoch)return;
  let totalHealed=0;
  if(BF_DEMO_SUPPORT_MODE==='heal'){
   for(const ally of liveParty()){
    const heal=Math.min(ally.maxHp-ally.hp,Math.round(p.rec*BF_DEMO_SUPPORT_REC_MULTIPLIER));
    if(heal>0){ally.hp+=heal;totalHealed+=heal;const [x,y]=xyAlly[ally.id];floatAt(x,y-35,'+'+heal,'heal');}
   }
  }
  msg(`DEMO SUPPORT BB: ${BF_DEMO_SUPPORT_MODE==='heal'?'restored '+totalHealed+' ally HP':'no simulated effect'}; dealt 0 enemy damage (original support effect unknown).`);'''
    after3='''  const support=originalSupport(p.unitId);
  msg(`${p.name} activates ${bbOriginal?.name||'BB'} — original ${support?.kind==='atk_buff_all'?'ATK buff':support?.kind==='heal_all'?'party recovery':'support'} type; BB Lv1 base values, DEMO application rules.`);
  await wait(effectTick*1000/BF_HIT_TICKS_PER_SECOND_UNVERIFIED/spd());if(token!==epoch)return;
  if(support?.kind==='atk_buff_all'){
   // Cast turn counts as turn 1. Do not stack boosts; stronger current
   // effect takes priority. Duration and stacking rules remain DEMO.
   let applied=0;
   for(const ally of liveParty()){
    if(!ally.atkBuff || ally.atkBuff.untilRound<S.round || support.pct>=ally.atkBuff.pct){
     ally.atkBuff={pct:support.pct,untilRound:S.round+support.rounds-1};applied++;
    }
   }
   msg(`ORIGINAL ATK BOOST BASE: +${support.pct}% to ${applied} allies for ${support.rounds} turns; DEMO stacking/turn timing; dealt 0 enemy damage.`);
  }else if(support?.kind==='heal_all'){
   let totalHealed=0;
   for(const ally of liveParty()){
    // Source Lv1 1500:600,800,50,50. 50,50 REC modifiers not decoded.
    // Use only original base range; missing HP caps, KO targets excluded.
    const base=support.low+Math.floor(rand()*(support.high-support.low+1));
    const heal=Math.max(0,Math.min(ally.maxHp-ally.hp,base));
    if(heal>0){ally.hp+=heal;totalHealed+=heal;const [x,y]=xyAlly[ally.id];floatAt(x,y-35,'+'+heal,'heal');}
   }
   msg(`ORIGINAL source Lv1 base healing range ${support.low}–${support.high}; ${totalHealed} HP restored, DEMO REC formula (not decoded); dealt 0 enemy damage.`);
  }else{
   msg('DEMO SUPPORT BB: source support entry unavailable; no simulated enemy damage or effect.');
  }'''
    # existing damage pass for each enemy; adjust player attack only.
    before4='foe.slot,splitDemoDamage(prototypeDamage(p.atk,foe.def,burst?2.1:1),strikes)'
    after4='foe.slot,splitDemoDamage(prototypeDamage(effectivePlayerAtk(p),foe.def,burst?2.1:1),strikes)'
    # slot labels visible, but do not modify saved stats nor attack/base stats.
    before5=" button.setAttribute('aria-label',p.name+', '+p.hp+' of '+p.maxHp+' HP, BB '+p.bb+' percent'+(p.action?', '+p.action.kind+' queued':''));"
    after5=" button.setAttribute('aria-label',p.name+', '+p.hp+' of '+p.maxHp+' HP, BB '+p.bb+' percent'+(currentAtkBoost(p)?', ATK boost '+currentAtkBoost(p)+' percent':'')+(p.action?', '+p.action.kind+' queued':''));"
    before6=' copy.append(nm,hp,hpbar,bb,burstText);button.append(av,copy);'
    after6=''' copy.append(nm,hp,hpbar,bb,burstText);
 if(active&&p.hp>0&&currentAtkBoost(p)){
  const buff=document.createElement('small');buff.className='bf-atk-buff-status';
  buff.textContent='ATK +'+currentAtkBoost(p)+'% · '+(p.atkBuff.untilRound-S.round+1)+' turn'+(p.atkBuff.untilRound===S.round?'':'s')+' (Lv1 BASE)';
  copy.append(buff);
 }
 button.append(av,copy);'''
    before7=' // Buff/healing support remains a labeled demo fallback, never fabricated.'
    after7=' // Buff/healing use verified Lv1 base values; other effect formulas remain DEMO.'
    replaces=[(before1,after1),(before2,after2),(before3,after3),(before4,after4),(before5,after5),(before6,after6),(before7,after7)]
    for old,new in replaces:
        assert html.count(old)==1,('Unexpected combat patch anchor',old[:100],html.count(old))
        html=html.replace(old,new,1)
    assert html.count(marker)==1
    HTML.write_text(html,'utf-8')
    print('PASS restored 2 Lv1 original ATK boosts and 4 source base heals; formulas/save unchanged')
