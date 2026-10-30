"""v199: count reused opaque mission-reference strings in authenticated 2022 fixtures.

Read-only research, NOT original enemy formation, encounter ID, weight or AI data.
The 142 raw references have already been checked against the original 2022
mission master in v152. The v199 report exposes aggregate counts only.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from pathlib import Path
import base64
import gzip
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'source_data'
SOURCES={
 'mistral':('bf_global_mistral_raw_mission_evidence_v056.json',
            '87fe678b1fe70a041212fdf9050dfa4003072312','missionId','rows',34),
 'morgan':('bf_global_morgan_original_v080.json',
           '3f5d07b55efc2676704d7a261ef9ea02f7abc23b','missionId','quests',36),
 'stlamia':('bf_global_st_lamia_raw_encounter_refs_v109.json',
            '5489144b43d1a07285d3a20001babd2810668b99','missionId','rows',36),
 'amdahl':('bf_global_2022_amdahl_quest_readiness_v147.json',
           'c8781b653027267ebfec06d4944d332628b88e51','id','quests',36),
}
ZIP2022='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
MASTER2022='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
CROSSPACK='cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a'
CROSSJSON='2f5daf4b5c74fcc53965f1115e5e1ce37bf788f03e372900f57bb1bd9843f2f7'
CROSSROWS='2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284'


def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\\0'+raw).hexdigest()


def read_original():
    """Read byte-pinned public excerpts, crosscheck all 142 v152 mission rows."""
    rows=[]
    for area,(filename,blob,id_field,key,count) in SOURCES.items():
        raw=(DATA/filename).read_bytes()
        assert git_blob(raw)==blob, ('source bytes changed',filename)
        doc=json.loads(raw)
        items=doc[key]
        assert len(items)==count
        if area=='mistral':
            assert doc['source']['archiveSha256']==ZIP2022
            assert doc['source']['fileSha256']==MASTER2022
        elif area=='stlamia':
            assert doc['provenance']['masterSha256']==MASTER2022
        elif area=='amdahl':
            assert doc['provenance']['missionTableSha256']==MASTER2022
            assert doc['area']['playableNow'] is False
        for item in items:
            rows.append({'area':area,'missionId':item[id_field],
                         'rawEncounterRef':item['rawEncounterRef']})
    payload=base64.b64decode(
        (DATA/'bf_global_2022_mission_cross_table_v152.json.gz.b64').read_text('ascii').strip(),
        validate=True)
    assert hashlib.sha256(payload).hexdigest()==CROSSPACK
    data=gzip.decompress(payload)
    assert hashlib.sha256(data).hexdigest()==CROSSJSON
    cross=json.loads(data)
    assert cross['schema']=='bf-global-original-2022-142-mission-cross-table-evidence-v152'
    assert cross['sourceZipSha256']==ZIP2022
    assert cross['canonicalRowsSha256']==CROSSROWS
    assert len(cross['rows'])==142
    assert hashlib.sha256(json.dumps(
        cross['rows'],separators=(',',':'),ensure_ascii=False
    ).encode()).hexdigest()==CROSSROWS
    lookup={r[0]:r[1] for r in cross['rows']}
    assert len(lookup)==142
    assert {r['missionId']:r['rawEncounterRef'] for r in rows}==lookup
    return rows


def analyze(rows):
    """Require strict identifiers, exact preserved strings, and area boundaries."""
    areas=Counter()
    groups=defaultdict(list)
    seen=set()
    for row in rows:
        assert type(row) is dict
        assert set(row)=={'area','missionId','rawEncounterRef'}
        area,id,ref=row['area'],row['missionId'],row['rawEncounterRef']
        assert area in SOURCES and type(id) is int and id>0
        assert id not in seen
        assert type(ref) is str and re.fullmatch(r'\\d+:\\d+(?:,\\d+:\\d+)*',ref)
        seen.add(id)
        areas[area]+=1
        groups[ref].append((area,id))
    assert areas==Counter({k:spec[4] for k,spec in SOURCES.items()})
    assert len(rows)==142 and len(groups)==29
    hist=Counter(len(members) for members in groups.values())
    cross=sum(len({area for area,_ in members})>1 for members in groups.values())
    parts=Counter(min(3,len(row['rawEncounterRef'].split(','))) for row in rows)
    assert hist=={4:6,5:20,6:3}
    assert cross==0
    assert parts=={1:31,2:84,3:27}
    assert all(len(members)>1 for members in groups.values())
    return {
      'schema':'bf-global-v199-2022-opaque-encounter-reference-collisions',
      'sourceArchiveSha256':ZIP2022,
      'sourceMissionMasterSha256':MASTER2022,
      'fixtureCrossref':'v152 pinned 142-row original mission reference excerpt',
      'sourceAreas':{k:areas[k] for k in SOURCES},
      'missionCount':len(rows),
      'distinctRawReferenceStrings':len(groups),
      'missionsSharingSomeRawReference':sum(len(v) for v in groups.values() if len(v)>1),
      'referenceReuseSizeHistogram':{str(k):hist[k] for k in sorted(hist)},
      'crossAreaExactReuseGroups':cross,
      'rawTokenPairCountBuckets':{
          'one':parts[1],'two':parts[2],'threeOrMore':parts[3]},
      'native2022EnemyIdsVerified':False,
      'native2022WaveFormationsVerified':False,
      'native2022EncounterWeightsVerified':False,
      'native2022EnemyAIAndDropsVerified':False,
      'changesGameplay':False,'changesSaves':False,'changesAndroid':False,
    }


def compare():
    return analyze(read_original())


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,
                        help='Optional aggregate research JSON outside this repository')
    args=parser.parse_args()
    report=compare()
    if args.output is None:
        print('PASS v199: 142 missions reuse 29 opaque 2022 strings; 6x4, 20x5, 3x6, no cross-area reuse')
        print('No native enemy identity, formation, weights, AI or drops authenticated.')
        return
    target=args.output.resolve()
    assert not target.is_relative_to(ROOT.resolve()),'Repository overwrite forbidden'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2)+'\\n',encoding='utf8')


if __name__=='__main__':
    main()
