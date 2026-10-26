"""Reproduce v0.34 from immutable user-provided BF Global 2022 asset/master archives.

Usage: python tools/generate_more_second_stage_source_manifest.py --master ... --units ... --thumbs ... --index ...
No network, no new invented source records, never edits original source zips.
"""
from __future__ import annotations
import argparse, base64, collections, hashlib, io, json, re, zipfile, csv
from pathlib import Path

parser=argparse.ArgumentParser()
for name in ('master','units','thumbs','index'):
    parser.add_argument('--'+name, type=Path, required=True)
a=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1]
IDS=(60013,10023,20023,30023,40023,50023)
sha=lambda b:hashlib.sha256(b).hexdigest()
expected={
 'master':'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
 'units':'c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846',
 'thumbs':'ad937083a4d023228f8796d45e5edd6adaf575872270476be994121941db3556'}
for name,val in expected.items(): assert sha(getattr(a,name).read_bytes())==val,name
html=a.index.read_text('utf-8')
def loaded(dom):
    match=re.search(r'<script type="application/json" id="'+dom+r'">(.*?)</script>',html,re.S)
    assert match,dom
    return json.loads(match.group(1))['units']
units={u['id']:u for u in loaded('bf-global-unit-catalog-data')}
lore={u['id']:u for u in loaded('bf-original-unit-lore-data')}
ms={}
with zipfile.ZipFile(a.master) as source:
    for table in ('SKILL_MST_','SKILL_LEVEL_MST_'):
        found={}
        for name in source.namelist():
            if name.startswith('3-mst-translated/F_'+table):
                for row in json.loads(source.read(name)):
                    if str(row.get('bbId')) in {str(x) for x in IDS}:
                        uid=int(row['bbId']);assert uid not in found,(uid,table)
                        found[uid]=(name,row)
        assert set(found)==set(IDS),(table,list(found))
        ms[table]=found

manifest={
 'schema':'bf-global-more-second-stage-2022-v034',
 'provenance':{'sourceMstSha256':expected['master'],'sourceUnitPart001Sha256':expected['units'],
               'sourceUnitPart007Sha256':expected['thumbs'],
               'source':'decoded 2022 Global F_UNIT/F_SKILL/F_SKILL_LEVEL/F_EVO MST and English sgtext'},
 'records':{}}
output=io.BytesIO()
with zipfile.ZipFile(a.units) as sprites,zipfile.ZipFile(a.thumbs) as thumbs,zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as out:
    for uid in IDS:
        original=units[uid]; previous=uid-1;owned=60011 if uid==60013 else uid-2
        archived=lore[previous]['recipes']
        assert len(archived)==1 and archived[0]['target']==uid
        recipe=archived[0]; mats=dict(collections.Counter(str(m['id']) for m in recipe['materials']))
        assert all(m['type']==1 for m in recipe['materials']) and recipe['zel']==100000
        s=ms['SKILL_MST_'][uid][1];levels=ms['SKILL_LEVEL_MST_'][uid][1]['activeSkillInfoByLevel'];english=lore[uid]['bb']
        assert english['id']==uid and int(s['bbId'])==uid
        assert s['skillTargetArea'] in ('1@1','2')
        target='support' if s['skillTypeId']=='5' else 'all_enemies' if s['skillTargetArea']=='2' else 'single_enemy'
        if target=='support':
            assert 'ATK for 3 turns' in english['description'];assert uid==40023
        elif target=='all_enemies':assert 'all enemies' in english['description'].lower()
        else:assert 'single enemy' in english['description'].lower()
        power=[];effects=[]
        for level,item in enumerate(levels.split('|'),1):
            code,typ,param=item.split('@')[0].split(':');p=[int(x) for x in param.split(',')]
            assert int(code)==level and len(p)>=6
            power.append(p[1] if target=='support' else p[0]);effects.append(int(typ))
        assert len(power)==10 and all(0<=x<=400 for x in power)
        assert len(set(effects))==1
        if target=='support':assert power[0]==50 and effects[0]==2000
        files=[f'content/unit/img/unit_anime_{uid}.png',f'content/unit/cgg/unit_cgg_{uid}.csv',
               f'content/unit/cgs/unit_idle_cgs_{uid}.csv',f'content/unit/cgs/unit_atk_cgs_{uid}.csv',
               f'content/unit/img/unit_ills_thum_{uid}.png']
        move=f'content/unit/cgs/unit_move_cgs_{uid}.csv'
        if move in sprites.namelist():files.append(move)
        d={}
        for file in files:
            raw=(thumbs if 'ills_thum' in file else sprites).read(file)
            d[file]=sha(raw);out.writestr(file,raw)
        cgg=[[int(v) for v in r if v.strip()] for r in csv.reader(io.StringIO(sprites.read(f'content/unit/cgg/unit_cgg_{uid}.csv').decode('utf-8-sig')))]
        assert cgg and all(r[0]==0 and len(r)==2+11*r[1] for r in cgg)
        non_default=[]
        for fi,row in enumerate(cgg):
            for j in range(row[1]):
                layer=row[2+11*j:2+11*(j+1)]
                dx,dy,angle,reserved,scale,unused,sx,sy,w,h,mode=layer
                assert angle in (0,1,2) and reserved==unused==mode==0 and scale in (30,50,70,100)
                assert min(sx,sy)>=0 and min(w,h)>0
                if angle!=0 or scale!=100:non_default.append({'frame':fi,'layer':j,'angleCode':angle,'scalePct':scale})
        manifest['records'][str(uid)]={
            'id':uid,'ownedBaseId':owned,'fromId':previous,'name':original['name'],'element':original['element'],
            'rarity':original['rarity'],'stats':{k:original['unitBase'+k.title()] for k in ('hp','atk','def','rec')},
            'lordStats':{k:original['unitLord'+k.title()] for k in ('hp','atk','def','rec')},
            'originalMaxLevel':original['unitMaxLevel'],'originalUnitCost':original['unitCost'],
            'sourceRecipe':{'zel':recipe['zel'],'karma':recipe['karma'],'materials':mats},
            'bb':{'name':english['name'],'description':english['description'],'target':target,'skillId':uid,
                  'sourceType':s['skillTypeId'],'sourceTargetType':s['targetType'],'sourceTargetArea':s['skillTargetArea'],
                  'effectFramesRaw':s['effectFrames'],'damageFramesRaw':s['damageFrames'],'levelInfo':levels,
                  'effectCode':effects[0],'levelPower':power,'secondaryUnmodeled':'@' in levels},
            'frameCount':len(cgg),'sourceFilesSha256':d,
            'spriteTransformNotes':{'angleCodes':[0,1,2],'scalePercentRange':[30,100],
                                    'nonDefaultLayers':non_default,
                                    'geometryInterpretation':'ANGLE CODE treated as archival orientation metadata; scale percent resizes PNG layer. Full native transforms not verified.'}
        }
manifest['sourcePackSha256']=sha(output.getvalue())
(ROOT/'source_data/bf_global_more_second_stage_v034.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
(ROOT/'source_assets/bf1/BF1_Global_2022_More_Second_Stage.zip.b64').write_text(base64.b64encode(output.getvalue()).decode()+'\n')
print('Prepared',len(IDS),'four-star forms, asset bytes',len(output.getvalue()))
for uid,data in manifest['records'].items():print(uid,data['name'],data['bb']['target'],data['bb']['levelPower'][:2],'transform layers',len(data['spriteTransformNotes']['nonDefaultLayers']))
