"""Optional offline reproducibility tool: needs user's exact immutable master/sprite archives."""
from pathlib import Path
from collections import Counter
from PIL import Image
import zipfile, json, re, base64, io, hashlib, csv, math
ROOT=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser(description='Regenerate v0.33 source manifest from the user-owned original 2022 archives')
parser.add_argument('--master',required=True,type=Path,help='Exact mst-decoded.zip')
parser.add_argument('--units',required=True,type=Path,help='Exact BF1_unit_part001.zip')
parser.add_argument('--thumbs',required=True,type=Path,help='Exact BF1_unit_part007.zip')
parser.add_argument('--index',required=True,type=Path,help='Prior v0.32 packaged index.html')
args=parser.parse_args()
DEST=ROOT
IDS=(10013,20013,30013,40013,50013,60023)
sha=lambda b:hashlib.sha256(b).hexdigest()
master=args.master; sprites=args.units; thumbs=args.thumbs; html=args.index.read_text('utf-8')
assert sha(master.read_bytes())=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert sha(sprites.read_bytes())=='c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846'
assert sha(thumbs.read_bytes())=='ad937083a4d023228f8796d45e5edd6adaf575872270476be994121941db3556'

def extracted(dom):return json.loads(re.search(r'<script type="application/json" id="'+dom+r'">(.*?)</script>',html,re.S).group(1))
units={u['id']:u for u in extracted('bf-global-unit-catalog-data')['units']}
lore={u['id']:u for u in extracted('bf-original-unit-lore-data')['units']}
with zipfile.ZipFile(master) as archive:
  rows={}
  for tab in ('SKILL_MST_','SKILL_LEVEL_MST_'):
    found={}
    for name in archive.namelist():
      if name.startswith('3-mst-translated/F_'+tab):
        for row in json.loads(archive.read(name)):
          try:unitid=int(row['bbId'])
          except (KeyError,ValueError):continue
          if unitid in IDS:
            assert unitid not in found
            found[unitid]=(name,row)
    assert set(found)==set(IDS),(tab,found.keys())
    rows[tab]=found

def parse(raw):return [[int(v) for v in r if v.strip()] for r in csv.reader(io.StringIO(raw.decode('utf-8-sig')))]
rawpack=io.BytesIO(); manifest={'schema':'bf-global-second-stage-evolutions-2022-v033','provenance':{'sourceMstSha256':sha(master.read_bytes()),'sourceUnitPart001Sha256':sha(sprites.read_bytes()),'sourceUnitPart007Sha256':sha(thumbs.read_bytes()),'source':'original 2022 Global source ZIP + English sgtext + decoded MST'},'records':{}}
with zipfile.ZipFile(rawpack,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as out, zipfile.ZipFile(sprites) as source,zipfile.ZipFile(thumbs) as art:
  for uid in IDS:
    previous=uid-1
    original=units[uid]
    recipe=lore[previous]['recipes']
    assert len(recipe)==1 and recipe[0]['target']==uid
    recipe=recipe[0]
    mats=dict(Counter(str(m['id']) for m in recipe['materials']))
    assert all(m['type']==1 for m in recipe['materials'])
    file_paths=[f'content/unit/img/unit_anime_{uid}.png',f'content/unit/cgg/unit_cgg_{uid}.csv',f'content/unit/cgs/unit_idle_cgs_{uid}.csv',f'content/unit/cgs/unit_atk_cgs_{uid}.csv',f'content/unit/cgs/unit_move_cgs_{uid}.csv',f'content/unit/img/unit_ills_thum_{uid}.png']
    digests={}
    for p in file_paths:
      raw=art.read(p) if 'ills_thum' in p else source.read(p)
      digests[p]=sha(raw);out.writestr(p,raw)
    frames=parse(source.read(f'content/unit/cgg/unit_cgg_{uid}.csv'))
    assert all(r[0]==0 and len(r)==2+11*r[1] for r in frames)
    for r in frames:
      for i in range(r[1]):
        layer=r[2+11*i:2+11*(i+1)]
        assert layer[2]==0 and layer[3]==0 and layer[4]==100 and layer[5]==0 and layer[10]==0,(uid,layer)
        x,y=220+layer[0],190+layer[1]
        assert 0<=x<480 and 0<=y<400 and x+layer[8]<=480 and y+layer[9]<=400,(uid,layer)
    skill=rows['SKILL_MST_'][uid][1]; levels=rows['SKILL_LEVEL_MST_'][uid][1]['activeSkillInfoByLevel']; english=lore[uid]['bb']
    assert int(skill['bbId'])==uid and english['id']==uid
    assert skill['skillTargetArea']=='2' and skill['skillTypeId']=='1'
    assert 'all enemies' in english['description'].lower()
    mod=[]
    for level,part in enumerate(levels.split('|'),1):
      levelstr,code,param=part.split('@')[0].split(':')
      numbers=[int(x) for x in param.split(',')]
      assert int(levelstr)==level and int(code) in (1500,1800,2000,2500) and len(numbers)>=6
      mod.append(numbers[0])
    assert len(mod)==10
    manifest['records'][str(uid)]={
      'id':uid,'ownedBaseId':60021 if uid==60023 else uid-2,'fromId':previous,'name':original['name'],'element':original['element'],'rarity':original['rarity'],
      'stats':{k:original['unitBase'+k.title()] for k in ('hp','atk','def','rec')},'originalLordStats':{k:original['unitLord'+k.title()] for k in ('hp','atk','def','rec')},
      'originalMaxLevel':original['unitMaxLevel'],'originalUnitCost':original['unitCost'],'sourceRecipe':{'zel':recipe['zel'],'karma':recipe['karma'],'materials':mats},
      'bb':{'name':english['name'],'description':english['description'],'target':'all_enemies','skillId':uid,
         'sourceType':skill['skillTypeId'],'sourceTargetType':skill['targetType'],'sourceTargetArea':skill['skillTargetArea'],
         'effectFramesRaw':skill['effectFrames'],'damageFramesRaw':skill['damageFrames'],'levelInfo':levels,'effectCode':int(levels.split('|')[0].split(':')[1]),'levelPower':mod},
      'frameCount':len(frames),'sourceFilesSha256':digests}
manifest['sourcePackSha256']=sha(rawpack.getvalue())
assert len(manifest['records'])==6
(DEST/'source_data/bf_global_second_stage_evolutions_v033.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(DEST/'source_assets/bf1/BF1_Global_2022_Second_Stage_Evolutions.zip.b64').write_text(base64.b64encode(rawpack.getvalue()).decode()+'\n')
print('source zip',len(rawpack.getvalue()),'base64',len(base64.b64encode(rawpack.getvalue())))
for uid,rec in manifest['records'].items():print(uid,rec['name'],rec['fromId'],rec['ownedBaseId'],rec['sourceRecipe']['zel'],rec['sourceRecipe']['materials'],rec['bb']['effectCode'],rec['bb']['levelPower'][:2])
