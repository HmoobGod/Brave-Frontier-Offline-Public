"""v0.53 source-verified BF1 archived monster art expansion for optional practice.

No original enemy identifiers, stats, spawn assignments or timing is claimed.
Adds ONLY original pixel frames and authentic CSV frame crops from archived
BF1 monster 0009–0016. No save v7 changes, no quest rewrite.
"""
from pathlib import Path
import json, hashlib

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
source=json.loads((ROOT/'source_data/bf_global_monster_training_v053.json').read_text('utf-8'))
assert source['schema']=='bf-global-original-monster-training-v053'
assert source['sourceArchive']['sha256']=='7487c043b31d54759fcf4bc6462c0c5e4ef50a8c66d886a37b156e0ba21804f3'
atlas=source['derivedAtlas']
assert (atlas['sha256'],atlas['bytes'],atlas['cellW'],atlas['cellH'],atlas['columns'],atlas['rows'])==(
 '781721404fa25b233b832686ca61d4998d18998e82434d2b6aefc1ed8eb2f25f',914491,192,256,8,8)
assert atlas['originalFrames'] is True and atlas['originalTiming'] is False
rows=source['entries']
assert len(rows)==8 and [r['id'] for r in rows]==[f'{i:04d}' for i in range(9,17)]
assert [r['frames'] for r in rows]==[5,8,8,5,5,5,5,5]
assert len({r['trainingKey'] for r in rows})==8
assert all(len(r['spriteSha256'])==len(r['layoutSha256'])==64 for r in rows)
assert source['runtime']['saveVersion']==7 and source['runtime']['optInDefault'] is False
raw=(ROOT/atlas['sourcePath']).read_bytes()
assert len(raw)==atlas['bytes'] and hashlib.sha256(raw).hexdigest()==atlas['sha256']
assert raw[:8]==bytes((137,80,78,71,13,10,26,10))
destination=ASSETS/atlas['apkPath']
destination.parent.mkdir(parents=True,exist_ok=True)
if not destination.is_file() or destination.read_bytes()!=raw:
    destination.write_bytes(raw)
assert destination.read_bytes()==raw
js=(ASSETS/'bf053_monster_training.js').read_text('utf-8')
assert js.count('/* BF_ORIGINAL_MONSTER_TRAINING_V053 */')==1
assert js.count('__BF053_MANIFEST__')==1
encoded=json.dumps(source,separators=(',',':'),ensure_ascii=True).replace('<',r'\\u003c')
script=js.replace('__BF053_MANIFEST__',encoded)
assert '</script' not in script.lower()
html=ASSETS/'index.html'
s=html.read_text('utf-8')
for mark in ('/* BF_MISTRAL_BOSS_HOOK_V052 */','/* BF_MISTRAL_BOSS_INTEL_V052 */',
             '/* BF_TOWER_OF_MISTRAL_V051 */'):
    assert s.count(mark)==1,mark
assert 'bf_global_offline_demo_v7' in s
marker='/* BF_MONSTER_TRAINING_HOOK_V053 */'
drawmarker='/* BF_MONSTER_TRAINING_DRAW_V053 */'
boundary='</script><!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->'
assert s.count(boundary)==1
if marker in s:
    assert s.count(marker)==s.count(drawmarker)==s.count('/* BF_ORIGINAL_MONSTER_TRAINING_V053 */')==1
    assert s.count(script)==1
    print('PASS v0.53 original training monster staging already present')
else:
    assert s.count(marker)==s.count(drawmarker)==s.count('/* BF_ORIGINAL_MONSTER_TRAINING_V053 */')==0
    old="""return window.BF052BossIntel?.encounter(
   QUEST.missionId,wave,QUEST.battles,E.mode.value,candidates) || candidates;
}"""
    assert s.count(old)==1,'v0.52 combat hook changed'
    new="""const originalBoss=window.BF052BossIntel?.encounter(
   QUEST.missionId,wave,QUEST.battles,E.mode.value,candidates) || candidates;
 /* BF_MONSTER_TRAINING_HOOK_V053 */
 return window.BF053TrainingMonsters?.encounter(E.mode.value,wave,originalBoss) || originalBoss;
}"""
    s=s.replace(old,new,1)
    art_anchor='const frame=monsterAnimationFrame(e,now);const sc=.43;'
    assert s.count(art_anchor)==1
    s=s.replace(art_anchor,art_anchor+"""
 /* BF_MONSTER_TRAINING_DRAW_V053 */
 const additionalArt=window.BF053TrainingMonsters?.drawSprite(e,now,ctx,x,y)===true;""",1)
    assert s.count('if(monsterAtlas.complete&&monsterAtlas.naturalWidth&&mon){')==1
    s=s.replace('if(monsterAtlas.complete&&monsterAtlas.naturalWidth&&mon){',
                'if(!additionalArt&&monsterAtlas.complete&&monsterAtlas.naturalWidth&&mon){',1)
    s=s.replace(boundary,'</script><script>'+script+'</script><!-- BF_GLOBAL_UNIT_ARCHIVE_BEGIN -->',1)
    assert s.count(marker)==s.count(drawmarker)==s.count('/* BF_ORIGINAL_MONSTER_TRAINING_V053 */')==1
    assert s.count(script)==1
    html.write_text(s,'utf-8')
    print('PASS v0.53 8 original BF1 monster art sheets in optional demo training; v7 save untouched')
