"""v0.55: stage historical Tower boss formations without inventing original sprites.

Only final-wave names and group composition are historical community records;
Mission 81's two 15k HP values are referenced, all other HP/ATK/DEF remain
DEMO. This feature is session-only, off by default, and leaves save v7 intact.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
data=json.loads((ROOT/'source_data/bf_global_mistral_boss_intel_v052.json').read_text('utf-8'))
assert data['schema']=='bf-global-mistral-boss-intel-v052'
assert data['provenance']['classification']=='historical-community-record, not 2022 MST combat formula'
assert [r['missionId'] for r in data['entries']]==[81,82,83,84,85]
expected={
    81:['King Glowy','King Gloomy'],
    82:['Behemoth','Skeleton','Skeleton'],
    83:['Wyvern'],
    84:['King Burny','King Squirty','King Mossy','King Sparky']
}
for mission,names in expected.items():
    r=next(v for v in data['entries'] if v['missionId']==mission)
    expanded=[b['name'] for b in r['bosses'] for _ in range(b.get('count',1))]
    assert expanded==names,(mission,expanded)
assert [b['hp'] for b in data['entries'][0]['bosses']]==[15000,15000]
assert data['optIn']['activeByDefault'] is False

js=(ASSETS/'bf055_tower_formations.js').read_text('utf-8')
assert js.count('/* BF_HISTORICAL_TOWER_FORMATIONS_V055 */')==1
assert "toggle.checked = false" in js
assert "historicalBossPreview:true" in js
assert "drawPlaceholder(e,ctx,x,y)" in js
assert "missionId,wave,totalWaves,mode,fallback" in js
assert "window.BF_debug?.reset()" in js
assert "bf_global_offline_demo_v7" not in js
assert "localStorage" not in js
assert '</script' not in js.lower()

html=ASSETS/'index.html'
s=html.read_text('utf-8')
for mark in ('/* BF_MISTRAL_BOSS_HOOK_V052 */','/* BF_MISTRAL_BOSS_INTEL_V052 */',
             '/* BF_MONSTER_TRAINING_HOOK_V053 */','/* BF_MONSTER_TRAINING_DRAW_V053 */',
             '/* BF_TOWER_OF_MISTRAL_V051 */'):
    assert s.count(mark)==1,mark
assert 'bf_global_offline_demo_v7' in s
assert s.count('</script><!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->')==1
marker='/* BF_TOWER_BOSS_FORMATION_HOOK_V055 */'
draw_marker='/* BF_TOWER_BOSS_PLACEHOLDER_V055 */'
script_marker='/* BF_HISTORICAL_TOWER_FORMATIONS_V055 */'
if marker in s:
    assert s.count(marker)==s.count(draw_marker)==s.count(script_marker)==1
    assert s.count(js)==1
    print('PASS v0.55 historical formations already staged')
else:
    assert s.count(marker)==s.count(draw_marker)==s.count(script_marker)==0
    old="""return window.BF053TrainingMonsters?.encounter(E.mode.value,wave,originalBoss) || originalBoss;
}"""
    new="""const trainingResult=window.BF053TrainingMonsters?.encounter(E.mode.value,wave,originalBoss) || originalBoss;
 /* BF_TOWER_BOSS_FORMATION_HOOK_V055 */
 return window.BF055TowerBosses?.encounter(
   QUEST.missionId,wave,QUEST.battles,E.mode.value,trainingResult) || trainingResult;
}"""
    assert s.count(old)==1,'v0.53 archived monster hook changed'
    s=s.replace(old,new,1)
    source_position='const xyEnemy=[[120,95],[101,179],[133,263]];'
    assert s.count(source_position)==1
    # Fourth demo slot is only reachable when player explicitly opts into
    # four historical boss NAMES for Mission 84. No original coordinates claimed.
    s=s.replace(source_position,'const xyEnemy=[[120,95],[101,179],[133,263],[180,181]];',1)
    old_draw="""const additionalArt=window.BF053TrainingMonsters?.drawSprite(e,now,ctx,x,y)===true;"""
    new_draw=old_draw+"""
 /* BF_TOWER_BOSS_PLACEHOLDER_V055 */
 const missingOriginalArt=window.BF055TowerBosses?.drawPlaceholder(e,ctx,x,y)===true;"""
    assert s.count(old_draw)==1
    s=s.replace(old_draw,new_draw,1)
    old_guard='if(!additionalArt&&monsterAtlas.complete&&monsterAtlas.naturalWidth&&mon){'
    assert s.count(old_guard)==1
    s=s.replace(old_guard,'if(!missingOriginalArt&&!additionalArt&&monsterAtlas.complete&&monsterAtlas.naturalWidth&&mon){',1)
    boundary='</script><!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->'
    s=s.replace(boundary,'</script><script>'+js+'</script><!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->',1)
    assert s.count(marker)==s.count(draw_marker)==s.count(script_marker)==1
    assert s.count(js)==1
    html.write_text(s,'utf-8')
    print('PASS v0.55 opt-in historical Tower final waves 81–84, neutral art, demo stats, save v7 unchanged')
