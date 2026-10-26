"""v0.52: Historical Global Mistral boss intelligence with opt-in partial boss simulation.

The original 2022 archive supplies quest order and monster sprite 0001.
The community wiki documents Tower encounters and Juggernaut's 50,000 HP.
These sources DO NOT establish native combat math, drops, full wave spawning,
or enemy AI. This patch must never alter persisted save version 7.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
catalog=json.loads((ROOT/'source_data/bf_global_mistral_boss_intel_v052.json').read_text('utf-8'))
assert catalog['schema']=='bf-global-mistral-boss-intel-v052'
assert [row['missionId'] for row in catalog['entries']]==[81,82,83,84,85]
boss=catalog['entries'][-1]['bosses'][0]
assert (boss['name'],boss['hp'],boss['element'],boss['monsterGraphicId'],boss['bundledSpriteKey'])==(
    'Juggernaut',50000,'Thunder','0001','gel')
assert catalog['optIn']['activeByDefault'] is False
js=(ASSETS/'bf052_story_boss.js').read_text('utf-8')
assert js.count('/* BF_MISTRAL_BOSS_INTEL_V052 */')==1
assert js.count('__BOSS_SOURCE_JSON__')==1
encoded=json.dumps(catalog,separators=(',',':'),ensure_ascii=True).replace('<',r'\u003c')
script=js.replace('__BOSS_SOURCE_JSON__',encoded)
assert '</script' not in script.lower()
html=ASSETS/'index.html'
s=html.read_text('utf-8')
assert 'bf_global_offline_demo_v7' in s
assert '/* BF_TOWER_OF_MISTRAL_V051 */' in s
assert '/* BF_MONSTERS_NEST_V050 */' in s
assert 'function buildEncounter(wave){' in s
assert 'window.BF_MONSTER_DATA=' in s
marker='/* BF_MISTRAL_BOSS_HOOK_V052 */'
hook=marker+"""
 return window.BF052BossIntel?.encounter(
   QUEST.missionId,wave,QUEST.battles,E.mode.value,candidates) || candidates;
}"""
boundary='</script><!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->'
assert s.count(boundary)==1
if marker in s:
    assert s.count(marker)==1 and s.count('/* BF_MISTRAL_BOSS_INTEL_V052 */')==1
    assert s.count(script)==1, 'v0.52 inline source data changed after staging'
    print('PASS v0.52 documented boss intel already staged')
else:
    assert s.count('return candidates;\n}')==1, 'unmodified vanilla encounter hook missing'
    assert s.count('/* BF_MISTRAL_BOSS_INTEL_V052 */')==0
    s=s.replace('return candidates;\n}',hook,1)
    s=s.replace(boundary,'</script><script>'+script+'</script><!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->',1)
    assert s.count(marker)==s.count('/* BF_MISTRAL_BOSS_INTEL_V052 */')==1
    assert s.count(script)==1
    html.write_text(s,'utf-8')
    print('PASS v0.52 optional Juggernaut original 50,000 HP and wiki boss references; save v7 intact')
