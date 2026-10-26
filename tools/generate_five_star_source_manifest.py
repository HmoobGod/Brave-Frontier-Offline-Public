"""Regenerate v0.35 playable Global 5-star starter evolutions from original user archives.

Usage: python tools/generate_five_star_source_manifest.py --mst mst-decoded.zip \
  --sprites BF1_unit_part001.zip --thumbs BF1_unit_part007.zip \
  --apk BraveFrontierGlobal-v0.34-Build59.apk
No network or write access to originals is needed.
"""
from __future__ import annotations
import argparse,base64,collections,csv,hashlib,io,json,re,zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--mst',type=Path,required=True);p.add_argument('--sprites',type=Path,required=True);p.add_argument('--thumbs',type=Path,required=True);p.add_argument('--apk',type=Path,required=True);a=p.parse_args()
IDS=(10014,20014,30014,40014,50014,60014)
sha=lambda b:hashlib.sha256(b).hexdigest()
original={"mst":"69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9",
          "sprites":"c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846",
          "thumbs":"ad937083a4d023228f8796d45e5edd6adaf575872270476be994121941db3556"}
for k,path in [('mst',a.mst),('sprites',a.sprites),('thumbs',a.thumbs)]:assert sha(path.read_bytes())==original[k],k
with zipfile.ZipFile(a.apk) as apk:
    html=apk.read('assets/index.html').decode('utf8')
def table(id):
    match=re.search(r'<script type="application/json" id="'+re.escape(id)+r'">(.*?)</script>',html,re.S)
    assert match,id
    return {u['id']:u for u in json.loads(match.group(1))['units']}
units=table('bf-global-unit-catalog-data');lore=table('bf-original-unit-lore-data')
master={};level={};master_sources={};level_sources={}
with zipfile.ZipFile(a.mst) as z:
    for name in z.namelist():
        if name.startswith('3-mst-translated/F_SKILL_MST_'):
            for row in json.loads(z.read(name)):
                key=int(row['bbId'])
                if key in IDS:
                    assert key not in master
                    master[key]=row;master_sources[key]=name
        if name.startswith('3-mst-translated/F_SKILL_LEVEL_MST_'):
            for row in json.loads(z.read(name)):
                key=int(row['bbId'])
                if key in IDS:
                    assert key not in level
                    level[key]=row;level_sources[key]=name
assert set(master)==set(level)==set(IDS)
def parse(b):return [[int(v) for v in rec if v.strip()] for rec in csv.reader(io.StringIO(b.decode('utf-8-sig')))]
archive=io.BytesIO()
manifest={"schema":"bf-global-six-five-star-starters-2022-v035","provenance":{
    "mstZipSha256":original['mst'],"originalUnitZipSha256":original['sprites'],"originalThumbnailsZipSha256":original['thumbs'],
    "source":"2022 translated F_UNIT_MST / F_SKILL_MST / F_SKILL_LEVEL_MST / F_UNIT_EVO_MST plus Global English sgtext and archived CGG/CGS/PNG"},
    "records":{}}
with zipfile.ZipFile(a.sprites) as sprites, zipfile.ZipFile(a.thumbs) as thumbs, zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as out:
 for id in IDS:
    u=units[id];prev=id-1;recipe=lore[prev]['recipes']
    assert len(recipe)==1 and recipe[0]['target']==id
    recipe=recipe[0];assert recipe['zel']==200000 and recipe['karma']==0
    mat=collections.Counter(str(m['id']) for m in recipe['materials'])
    assert all(m['type']==1 for m in recipe['materials'])
    assert len(mat)==4 and sum(mat.values())==5
    skill=master[id];ll=level[id]['activeSkillInfoByLevel'];bb=lore[id]['bb']
    assert bb['id']==id and skill['skillTypeId']=='1' and skill['skillTargetArea']=='2' and 'all enemies' in bb['description'].lower()
    parsed=[]
    for num,segment in enumerate(ll.split('|'),start=1):
        first=segment.split('@')[0];n,code,params=first.split(':');arr=list(map(int,params.split(',')))
        assert int(n)==num and int(code)==2500 and len(arr)==6 and arr[1:]==[60,0,0,0,0]
        parsed.append(arr[0])
    assert len(parsed)==10 and parsed==[70,80,90,100,110,120,130,140,150,160]
    input_paths=[f'content/unit/img/unit_anime_{id}.png',f'content/unit/cgg/unit_cgg_{id}.csv',
        *[f'content/unit/cgs/unit_{kind}_cgs_{id}.csv' for kind in ('idle','atk','move')],
        f'content/unit/img/unit_ills_thum_{id}.png']
    shas={}
    for path in input_paths:
        data=thumbs.read(path) if 'ills_thum' in path else sprites.read(path)
        shas[path]=sha(data);out.writestr(path,data)
    image=Image.open(io.BytesIO(sprites.read(input_paths[0])));assert image.size==(512,512)
    frames=parse(sprites.read(input_paths[1]));assert 8<=len(frames)<=35
    transforms=[]
    for fi,row in enumerate(frames):
        assert row[0]==0 and len(row)==2+11*row[1]
        for n in range(row[1]):
            dx,dy,angle,rsv,scale,unused,x,y,w,h,mode=row[2+n*11:2+(n+1)*11]
            assert angle in (0,2) and rsv==unused==mode==0 and scale in (30,40,60,80,100)
            assert w>0 and h>0 and x>=0 and y>=0 and x+w<=512 and y+h<=512
            W=max(1,round(w*scale/100));H=max(1,round(h*scale/100))
            assert 0<=220+dx and 0<=190+dy and 220+dx+W<=480 and 190+dy+H<=400
            if angle or scale!=100:transforms.append({'frame':fi,'layer':n,'orientationCode':angle,'scalePercent':scale})
    for kind in ('idle','atk','move'):
        anim=parse(sprites.read(f'content/unit/cgs/unit_{kind}_cgs_{id}.csv'))
        assert anim and all(len(p)==4 and 0<=p[0]<len(frames) and p[3]>0 for p in anim)
    manifest['records'][str(id)]={
        'id':id,'ownedBaseId':id-3,'fromId':prev,'name':u['name'],'element':u['element'],'rarity':u['rarity'],
        'stats':{k:u['unitBase'+k.title()] for k in ('hp','atk','def','rec')},
        'lordStats':{k:u['unitLord'+k.title()] for k in ('hp','atk','def','rec')},
        'originalMaxLevel':u['unitMaxLevel'],'originalUnitCost':u['unitCost'],
        'sourceRecipe':{'zel':recipe['zel'],'karma':recipe['karma'],'materials':dict(mat)},
        'bb':{'name':bb['name'],'description':bb['description'],'target':'all_enemies','skillId':id,
            'sourceTable':master_sources[id],'sourceLevelTable':level_sources[id],
            'sourceType':skill['skillTypeId'],'sourceTargetType':skill['targetType'],'sourceTargetArea':skill['skillTargetArea'],
            'effectFramesRaw':skill['effectFrames'],'damageFramesRaw':skill['damageFrames'],'levelInfo':ll,
            'effectCode':2500,'firstParameterByLevel':parsed,'otherParamsNotDecoded':[60,0,0,0,0]},
        'frameCount':len(frames),'sourceFilesSha256':shas,'unverifiedSpriteTransformLayers':transforms
    }
manifest['sourcePackSha256']=sha(archive.getvalue());assert len(manifest['records'])==6
(ROOT/'source_data').mkdir(exist_ok=True,parents=True)
(ROOT/'source_assets/bf1').mkdir(exist_ok=True,parents=True)
(ROOT/'source_data/bf_global_six_five_star_v035.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
(ROOT/'source_assets/bf1/BF1_Global_2022_Six_Five_Star.zip.b64').write_text(base64.b64encode(archive.getvalue()).decode('ascii')+'\n')
print('PASS original manifest',len(manifest['records']),'source archive slice bytes',len(archive.getvalue()))
for id,r in manifest['records'].items():print(id,r['name'],'recipe',r['sourceRecipe']['materials'],'transforms',len(r['unverifiedSpriteTransformLayers']))
