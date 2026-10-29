"""v174: generate a read-only 2022 encounter/backdrop reference ledger.
This DOES NOT resolve original enemy formations, AI, damage, or loot.
"""
from pathlib import Path
import base64,gzip,hashlib,json,re
R=Path(__file__).resolve().parent
S=R/'source_data'
A=R/'app/src/main/assets'
sha=lambda b:hashlib.sha256(b).hexdigest()
packed=base64.b64decode((S/'bf_global_2022_mission_cross_table_v152.json.gz.b64').read_text('ascii').strip(),validate=True)
assert sha(packed)=='cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a'
raw=gzip.decompress(packed)
assert sha(raw)=='2f5daf4b5c74fcc53965f1115e5e1ce37bf788f03e372900f57bb1bd9843f2f7'
v=json.loads(raw)
assert v['schema']=='bf-global-original-2022-142-mission-cross-table-evidence-v152'
assert v['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert v['canonicalRowsSha256']=='2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284'
assert v['columns']==['missionId','opaqueEncounterField','dungeonBackdrop','matchingGrandSpotRows','matchingRaidPointRows']
rows=v['rows']
assert len(rows)==142 and len({r[0] for r in rows})==142
assert sha(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode())==v['canonicalRowsSha256']
live=json.loads((S/'bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
amd=json.loads((S/'bf_global_2022_amdahl_quest_readiness_v147.json').read_text('utf8'))
assert live['total']==106 and len(live['records'])==106
assert amd['area']['missionCount']==36 and amd['area']['playableNow'] is False
assert amd['area']['originalEnemyWavesDecoded'] is False
assert live['missionMasterSha256']==amd['provenance']['missionTableSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
waves={r[0]:r[3] for r in live['records']}
for q in amd['quests']:
    assert q['id'] not in waves
    waves[q['id']]=q['waveCount']
assert len(waves)==142
assert [r[0] for r in rows[:106]]==[r[0] for r in live['records']]
assert [r[0] for r in rows[106:]]==[q['id'] for q in amd['quests']]
assert sum(r[3]>0 for r in rows)==92
assert sum(r[4]>0 for r in rows)==99
assert sum(r[3]>0 and r[4]>0 for r in rows)==73
exceptions=[r[0] for r in rows if r[2]!=('dungeon_battle_'+r[1].split(',')[0].split(':')[1]+'.jpg')]
assert exceptions==[70,71,72,73,230,231,232,233,234]
prepared=[]
for r in rows:
    id,group,backdrop,grand,raid=r
    assert (type(id) is int and type(grand) is int and type(raid) is int and
      re.fullmatch(r'\d+:\d+(?:,\d+:\d+)*',group) and
      re.fullmatch(r'dungeon_battle_\d+\.jpg',backdrop) and
      type(waves[id]) is int and waves[id]>0)
    prepared.append([id,group,backdrop,grand,raid,waves[id]])
js=r"""/* BF_GLOBAL_ORIGINAL_2022_ENCOUNTER_CROSSREFS_V17400 */
(()=>{
'use strict';
// Archived original 2022 references, NOT a wave/enemy/AI decoder.
const refs=window.BFGlobalEncounterReferencesV15100;
if(window.BFGlobalEncounterCrossrefsV17400||
   typeof P==='undefined'||P.version!==7||
   typeof QUESTS==='undefined'||!Array.isArray(QUESTS)||QUESTS.length!==106||
   !refs||refs.summary?.archivedMissions!==142||
   refs.summary?.playableMissions!==106||
   refs.summary?.amdahlSourceOnlyMissions!==36||
   refs.summary?.sha256!=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'||
   refs.summary?.meaningDecoded!==false||typeof refs.lookup!=='function')return;
const rows=__ROWS__;
const source=Object.freeze({
 year:2022,missionMasterSha256:'d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83',
 crossTableRowsSha256:'2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284',
 total:142,playable:106,amdahlReadOnly:36,
 matchingGrandSpots:92,matchingRaidPoints:99,matchingBoth:73,
 firstRefBackgroundMatches:133,firstRefBackgroundExceptions:9,
 nativeWavesDecoded:false,nativeEnemyIdsDecoded:false,
 nativeAIDecoded:false,nativeDropsDecoded:false,saveFieldsAdded:0
});
const liveIds=new Set(QUESTS.map(q=>q.missionId));
if(liveIds.size!==106||rows.length!==142)return;
const byId=new Map();
let grand=0,raid=0,both=0,match=0;
for(let i=0;i<rows.length;i++){
 const [id,opaque,background,g,r,waves]=rows[i];
 const prior=refs.lookup(id);
 const playable=i<106;
 if(!Number.isSafeInteger(id)||byId.has(id)||!prior||
    prior.missionId!==id||prior.raw!==opaque||
    (playable?!liveIds.has(id):liveIds.has(id))||
    !Number.isSafeInteger(waves)||waves<1||waves>40||
    !/^\d+:\d+(?:,\d+:\d+)*$/.test(opaque)||
    !/^dungeon_battle_\d+\.jpg$/.test(background)||
    !Number.isSafeInteger(g)||g<0||!Number.isSafeInteger(r)||r<0||
    (!playable&&prior.originalSourceWaveCount!==waves))return;
 if(g>0)grand++;if(r>0)raid++;if(g>0&&r>0)both++;
 const first=opaque.split(',')[0].split(':')[1];
 const same=background==='dungeon_battle_'+first+'.jpg';
 if(same)match++;
 byId.set(id,Object.freeze({
  missionId:id,sourceYear:2022,originalSourceWaveCount:waves,
  opaqueEncounterField:opaque,originalDungeonBattleBackground:background,
  crossTableGrandSpotMatches:g,crossTableRaidPointMatches:r,
  firstOpaqueRefMatchesBackground:same,playable,
  enemyIdsDecoded:false,enemyWavesDecoded:false,enemyAIDecoded:false,
  sourceIsOriginal2022:true
 }));
}
if(byId.size!==142||grand!==92||raid!==99||both!==73||match!==133||
   rows.slice(106).some(row=>row[0]<400||row[0]>465))return;
const panel=document.getElementById('bf10800-encounter-ledger');
const selector=document.getElementById('bf10800-mission');
if(!panel||!selector||selector.options.length!==142)return;
const body=document.createElement('p');
body.id='bf17400-encounter-crossrefs';
const note=document.createElement('small');
note.textContent='2022 source background filenames and Grand/Raid reference reuse are archival facts, '+
 'NOT decoded enemies, wave formations, probabilities, AI, drops or playable Amdahl missions. '+
 'Original battle-count fields establish only a wave count. '+
 'Nine missions have different first raw-reference/background suffixes.';
panel.append(body,note);
function lookup(id){
 return Number.isSafeInteger(id)?byId.get(id)||null:null;
}
function refresh(){
 const record=lookup(Number(selector.value));
 body.textContent=record?'2022 mission '+record.missionId+
  ' · '+record.originalSourceWaveCount+' original-counted waves'+
  ' · original battle background: '+record.originalDungeonBattleBackground+
  ' · source string also in '+record.crossTableGrandSpotMatches+
  ' Grand Spot and '+record.crossTableRaidPointMatches+' Raid Point records'+
  (record.firstOpaqueRefMatchesBackground?' · first ref/background agree':
   ' · first ref/background differ (not decoded)')+
  (record.playable?' · live quest':' · Amdahl SOURCE ONLY'):
  'No source-backed cross-table record for this mission';
 return record;
}
selector.addEventListener('change',refresh);
refresh();
window.BFGlobalEncounterCrossrefsV17400=Object.freeze({
 source,lookup,refresh
});
})();
"""
js=js.replace('__ROWS__',json.dumps(prepared,ensure_ascii=False,separators=(',',':')))
assert len(js.encode('utf8'))<65536
assert js.count('BF_GLOBAL_ORIGINAL_2022_ENCOUNTER_CROSSREFS_V17400')==1
assert not any(x in js for x in ('localStorage','saveProgress(', 'Math.random(', 'S.enemies=', 'awardDemoRewards(', 'fetch('))
(A/'bf17400_original_2022_encounter_crossrefs.js').write_text(js,'utf8')
print('PASS v174 source preparation: 142 original 2022 crossrefs, 133 background joins; no decoded waves/AI')
