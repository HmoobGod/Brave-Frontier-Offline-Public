'''Restore original 2022 Global offensive BB Lv1 power modifiers.

Only modifier percentages are source-backed; prototype damage, DEF, hit
simulation, spark, elements, BC and BB progression remain DEMO.
Idempotent/fail-closed. No saved player data is changed.
'''
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source_data'
HTML=ROOT/'app/src/main/assets/index.html'
manifest=json.loads((SOURCE/'bf_global_original_bb_power_v030.json').read_text('utf-8'))
targets=json.loads((SOURCE/'bf_global_original_bb_targeting.json').read_text('utf-8'))['targets']
assert manifest['schema']=='bf-global-original-offensive-bb-power-v030'
assert manifest['provenance']['mstZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert len(targets)==30 and len(manifest['skills'])==24
assert set(manifest['skills'])=={k for k,v in targets.items() if v['target']!='support'}
source_codes={1500:21,1800:1,2000:2}
seen={1500:0,1800:0,2000:0}
compressed={}
for uid,entry in manifest['skills'].items():
    assert uid.isdecimal() and int(uid)==entry['skillId']
    assert (entry['name'],entry['target'])==(targets[uid]['name'],targets[uid]['target'])
    assert entry['sourceTable'].startswith('3-mst-translated/F_SKILL_LEVEL_MST_')
    raw=entry['rawLevelData'].split('|')
    assert len(raw)==len(entry['levels'])==10
    for level,(part,rec) in enumerate(zip(raw,entry['levels']),start=1):
        core=part.split('@')[0]
        number,code,params=core.split(':')
        all_params=[int(x) for x in params.split(',')]
        assert int(number)==level and len(all_params)==6
        assert rec=={'level':level,'effectCode':int(code),'damageModifierPct':all_params[0],
                     'otherUndecodedParams':all_params[1:]}
        assert 0<=rec['damageModifierPct']<=400
    code=entry['levels'][0]['effectCode']
    assert code in seen and all(r['effectCode']==code for r in entry['levels'])
    assert all(x['damageModifierPct']<=y['damageModifierPct'] for x,y in zip(entry['levels'],entry['levels'][1:]))
    seen[code]+=1
    compressed[uid]={
        'name':entry['name'],
        'target':entry['target'],
        'base':entry['levels'][0]['damageModifierPct'],
        'levels':[r['damageModifierPct'] for r in entry['levels']],
        'secondaryUnmodeled':entry['hasSecondaryUnmodeledEffects']
    }
assert seen==source_codes,seen
assert compressed['10011']['levels']==[30,35,40,45,50,55,60,65,70,75]
assert compressed['10021']['levels'][0]==150 and compressed['10021']['levels'][-1]==240
assert compressed['30022']['levels'][-1]==100

html=HTML.read_text('utf-8')
assert html.count('/* BF_GLOBAL_BB_TARGETING_V028 */')==1
assert html.count('/* BF_GLOBAL_BB_SUPPORT_V029 */')==1
assert 'bf_global_offline_demo_v7' in html
marker='/* BF_GLOBAL_BB_POWER_V030 */'
if marker in html:
    assert html.count(marker)==1
    assert 'bbDamageMultiplier(p,burst)' in html
    assert 'window.BFOriginalBBPower' in html
    print('PASS existing v0.30 original offensive BB modifiers and Lv1 battle implementation unchanged.')
else:
    power='''/* BF_GLOBAL_BB_POWER_V030 */
// Original 2022 F_SKILL_LEVEL_MST damage-modifier percent for 24 BBs.
// Only Lv1 powers a DEMO battle formula. Source Lv2-10 are reference data.
// The 6 original support BBs are kept separate in the v0.29 support patch.
const BF_ORIGINAL_BB_POWER=Object.freeze(__SOURCE__);
const bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||null;
function bbDamageMultiplier(p,burst){
  if(!burst)return 1;
  const skill=bfOriginalBBPower(p.unitId);
  return skill?1+skill.base/100:2.1;
}
window.BFOriginalBBPower=Object.freeze({
  count:24,
  forUnit:id=>bfOriginalBBPower(id),
  multiplierFor:id=>bbDamageMultiplier({unitId:Number(id)},true),
  levelsFor:id=>bfOriginalBBPower(id)?.levels.slice()||null
});
'''.replace('__SOURCE__',json.dumps(compressed,separators=(',',':'),ensure_ascii=True))
    changes=[
       ('function prototypeDamage(atk,def,mult=1){',power+'function prototypeDamage(atk,def,mult=1){'),
       ('prototypeDamage(effectivePlayerAtk(p),foe.def,burst?2.1:1)',
        'prototypeDamage(effectivePlayerAtk(p),foe.def,bbDamageMultiplier(p,burst))'),
       ("${allEnemyBB?'original all-enemy targeting':bbOriginal?.target==='single_enemy'?'original single-enemy targeting':'single-target DEMO fallback'}; ${events?'original hit timing':'fallback timing'}, DEMO damage/effects.",
        "${allEnemyBB?'original all-enemy targeting':bbOriginal?.target==='single_enemy'?'original single-enemy targeting':'single-target DEMO fallback'}; ${bfOriginalBBPower(p.unitId)?'original BB Lv1 +'+bfOriginalBBPower(p.unitId).base+'% power':'DEMO power fallback'}, ${events?'original hit timing':'fallback timing'}, DEMO damage/DEF."),
       ("burstText.textContent=active?(p.bb>=100?'BRAVE BURST READY':'BRAVE BURST '+p.bb+'%'):'—';",
        "burstText.textContent=active?(p.bb>=100?'BRAVE BURST READY'+(bfOriginalBBPower(p.unitId)?' · Lv1 +'+bfOriginalBBPower(p.unitId).base+'% power':''):'BRAVE BURST '+p.bb+'%'):'—';")
    ]
    for old,new in changes:
        assert html.count(old)==1,('Source unexpectedly changed; refusing patch',old[:100],html.count(old))
        html=html.replace(old,new,1)
    assert html.count(marker)==1
    HTML.write_text(html,'utf-8')
    print('PASS v0.30 original Global BB Lv1 damage modifiers: 24 attacks; levels 2-10 preserved as reference.')
