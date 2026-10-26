"""Rebuild original Global v0.36 5-star second-wave references from immutable archives.

Run with original 2022 BF master, unit sprites and original thumbnails.
The source data never depends on fabricated stats or guesswork about native formulas.
"""
from pathlib import Path
from collections import Counter
from PIL import Image
import io,zipfile,hashlib,re,json,base64,csv,argparse
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Regenerate v0.36 original source records; never edits your archive ZIPs')
parser.add_argument('--master',required=True,type=Path,help='Exact mst-decoded.zip')
parser.add_argument('--sprites',required=True,type=Path,help='Exact BF1_unit_part001.zip')
parser.add_argument('--thumbs',required=True,type=Path,help='Exact BF1_unit_part007.zip')
parser.add_argument('--baseline-apk',required=True,type=Path,help='Original v0.35 Build 62 APK with embedded English catalog and codex')
args=parser.parse_args()
MASTER=args.master;SPRITES=args.sprites;THUMBS=args.thumbs;APK=args.baseline_apk
IDS=(10024,20024,30024,40024,50024,60024)
sha=lambda b:hashlib.sha256(b).hexdigest()
expected={'mst':'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9','sprites':'c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846','thumbs':'ad937083a4d023228f8796d45e5edd6adaf575872270476be994121941db3556'}
for path,key in [(MASTER,'mst'),(SPRITES,'sprites'),(THUMBS,'thumbs')]:assert sha(path.read_bytes())==expected[key],(path,key)
with zipfile.ZipFile(APK) as z:html=z.read('assets/index.html').decode()
def embedded(key):
 m=re.search(r'<script type="application/json" id="'+re.escape(key)+r'">(.*?)</script>',html,re.S);assert m,key
 return {x['id']:x for x in json.loads(m.group(1))['units']}
units=embedded('bf-global-unit-catalog-data');lore=embedded('bf-original-unit-lore-data')
masters={}
with zipfile.ZipFile(MASTER) as z:
 for token in ('SKILL_MST_','SKILL_LEVEL_MST_'):
  rows={}
  for path in z.namelist():
   if path.startswith('3-mst-translated/F_'+token):
    for rec in json.loads(z.read(path)):
     try:uid=int(rec['bbId'])
     except (KeyError,ValueError):continue
     if uid in IDS:
      assert uid not in rows,(uid,path)
      rows[uid]=rec
  assert set(rows)==set(IDS),(token,rows.keys())
  masters[token]=rows

def parse(raw):return [[int(c) for c in row if c.strip()] for row in csv.reader(io.StringIO(raw.decode('utf-8-sig')))]
out=io.BytesIO()
manifest={'schema':'bf-global-six-other-five-star-2022-v036','provenance':{'mstZipSha256':expected['mst'],'sourceUnitPart001Sha256':expected['sprites'],'sourceUnitPart007Sha256':expected['thumbs'],'source':'2022 translated Global F_UNIT_MST, F_SKILL_MST, F_SKILL_LEVEL_MST, F_UNIT_EVO_MST and English sgtext'},'records':{}}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as pack,zipfile.ZipFile(SPRITES) as unitpack,zipfile.ZipFile(THUMBS) as thumbpack:
 for uid in IDS:
  previous=uid-1;u=units[uid];recipe=lore[previous]['recipes']
  assert u['nameSource']=='2022_Global_English' and u['rarity']==5
  assert len(recipe)==1 and recipe[0]['target']==uid
  recipe=recipe[0];assert recipe['zel']==200000 and recipe['karma']==0
  assert len(recipe['materials'])==5 and all(x['type']==1 for x in recipe['materials'])
  names=[f'content/unit/img/unit_anime_{uid}.png',f'content/unit/cgg/unit_cgg_{uid}.csv',f'content/unit/cgs/unit_idle_cgs_{uid}.csv',f'content/unit/cgs/unit_atk_cgs_{uid}.csv',f'content/unit/img/unit_ills_thum_{uid}.png']
  move=f'content/unit/cgs/unit_move_cgs_{uid}.csv';has_move=move in unitpack.namelist()
  if has_move:names.append(move)
  hashes={}
  for name in names:
   data=(thumbpack if 'ills_thum' in name else unitpack).read(name)
   hashes[name]=sha(data)
   pack.writestr(name,data)
  src_img=Image.open(io.BytesIO(unitpack.read(names[0])));assert src_img.size in ((512,512),(640,640)),(uid,src_img.size)
  frames=parse(unitpack.read(names[1]));assert 10<=len(frames)<=40
  orientations={};scales={};flags={}
  for fi,row in enumerate(frames):
   assert row[0]==0 and len(row)==2+11*row[1]
   for j in range(row[1]):
    dx,dy,ori,reserved,scale,unused,x,y,w,h,mode=row[2+j*11:2+(j+1)*11]
    assert ori==0 and scale==100 and unused==mode==0
    assert reserved in (0,1) and w>0 and h>0 and 0<=x and 0<=y and x+w<=src_img.width and y+h<=src_img.height
    assert 0<=220+dx and 0<=190+dy and 220+dx+w<=480 and 190+dy+h<=400
    orientations[str(ori)]=orientations.get(str(ori),0)+1
    if reserved:flags[str(reserved)]=flags.get(str(reserved),0)+1
  skill=masters['SKILL_MST_'][uid];levels=masters['SKILL_LEVEL_MST_'][uid]['activeSkillInfoByLevel']
  eng=lore[uid]['bb'];assert eng['id']==uid
  dtype=skill['skillTypeId'];area=skill['skillTargetArea']
  if dtype=='5' and area=='2':target='support'
  elif dtype.startswith('1') and area.startswith('1'):target='single_enemy'
  elif dtype=='1' and area=='2':target='all_enemies'
  else:raise AssertionError((uid,dtype,area))
  data_by_level=[]
  for i,part in enumerate(levels.split('|'),1):
   lvl,code,params=part.split('@')[0].split(':')
   values=[int(x) for x in params.split(',')]
   assert int(lvl)==i and len(values)>=6
   data_by_level.append({'level':i,'effectCode':int(code),'params':values,'secondaryEffectUndecoded':'@' in part})
  assert len(data_by_level)==10
  if target=='support':
   assert uid==40024 and data_by_level[0]['params']==[0,80,0,0,0,3,90]
  assert eng['name']
  entries={k:u['unitBase'+k.title()] for k in ('hp','atk','def','rec')}
  ld={k:u['unitLord'+k.title()] for k in ('hp','atk','def','rec')}
  materials=dict(Counter(str(mat['id']) for mat in recipe['materials']))
  manifest['records'][str(uid)]={
   'id':uid,'ownedBaseId':uid-3,'fromId':previous,'name':u['name'],'element':u['element'],'rarity':5,
   'stats':entries,'lordStats':ld,'originalMaxLevel':u['unitMaxLevel'],'originalUnitCost':u['unitCost'],
   'sourceRecipe':{'zel':recipe['zel'],'karma':recipe['karma'],'materials':materials},
   'bb':{'name':eng['name'],'description':eng['description'],'target':target,'sourceType':dtype,
       'sourceTargetType':skill['targetType'],'sourceTargetArea':area,'effectFramesRaw':skill['effectFrames'],
       'damageFramesRaw':skill['damageFrames'],'levelInfo':levels,'levels':data_by_level},
   'frameCount':len(frames),'missingOriginalMoveCGS':not has_move,
   'unverifiedReservedFlags':flags,'sourceFilesSha256':hashes}
manifest['sourcePackSha256']=sha(out.getvalue())
assert len(manifest['records'])==6
D=ROOT/'source_data';A=ROOT/'source_assets/bf1';D.mkdir(parents=True,exist_ok=True);A.mkdir(parents=True,exist_ok=True)
(D/'bf_global_other_five_star_v036.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
(A/'BF1_Global_2022_Other_Five_Star.zip.b64').write_text(base64.b64encode(out.getvalue()).decode()+'\n')
for id,row in manifest['records'].items():
 print(id,row['name'],row['bb']['name'],row['bb']['target'],row['bb']['levels'][0]['effectCode'],row['bb']['levels'][0]['params'][:2],row['sourceRecipe']['materials'],row['frameCount'],'move_missing',row['missingOriginalMoveCGS'],'unknown_flags',row['unverifiedReservedFlags'])
print('assets size',len(out.getvalue()))
