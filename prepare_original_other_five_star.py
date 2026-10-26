"""v0.36: six archived Global 5-star evolutions in existing v7 progression.

Authentic source: original 2022 sprite PNG/CGG/CGS, translated unit/stat,
English BB and evolution master. Native damage formulas are NOT decoded:
for unfamiliar effect codes we deliberately preserve the demo fallback scalar.
"""
from __future__ import annotations
import base64,collections,csv,hashlib,io,json,math,re,zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets';D=ROOT/'source_data';ASSET=ROOT/'source_assets/bf1'
M=json.loads((D/'bf_global_other_five_star_v036.json').read_text('utf-8'))
IDS={10024,20024,30024,40024,50024,60024}
assert M['schema']=='bf-global-six-other-five-star-2022-v036'
assert M['provenance']['mstZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert set(map(int,M['records']))==IDS
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=base64.b64decode((ASSET/'BF1_Global_2022_Other_Five_Star.zip.b64').read_text('ascii'))
assert sha(blob)==M['sourcePackSha256']
index=A/'index.html';html=index.read_text('utf8')
for tag in ['/* BF_GLOBAL_FIVE_STAR_STARTERS_V035 */','/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */','/* BF_GLOBAL_SECOND_EVOLUTIONS_V033 */']:
 assert html.count(tag)==1,(tag,html.count(tag))
assert 'bf_global_offline_demo_v7' in html

def embedded(tag):
 m=re.search(r'<script type="application/json" id="'+re.escape(tag)+r'">(.*?)</script>',html,re.S)
 assert m,tag
 return {r['id']:r for r in json.loads(m.group(1))['units']}
unit_catalog=embedded('bf-global-unit-catalog-data')
lore=embedded('bf-original-unit-lore-data')
def parse(b):return [[int(v) for v in row if v.strip()] for row in csv.reader(io.StringIO(b.decode('utf-8-sig')))]

def bake(z,uid):
 sprite=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
 assert sprite.size in ((512,512),(640,640))
 frames=parse(z.read(f'content/unit/cgg/unit_cgg_{uid}.csv'))
 assert 10<=len(frames)<=40
 w,h,cols,ox,oy=480,400,5,220,190
 atlas=Image.new('RGBA',(w*cols,h*math.ceil(len(frames)/cols)),(0,0,0,0))
 undecoded=[]
 for fi,row in enumerate(frames):
  assert row[0]==0 and len(row)==2+row[1]*11
  frame=Image.new('RGBA',(w,h),(0,0,0,0))
  for li in range(row[1]):
   dx,dy,orientation,reserved,scale,unused,x,y,bw,bh,mode=row[2+11*li:2+11*(li+1)]
   assert orientation==0 and scale==100 and unused==mode==0
   assert reserved in (0,1) and bw>0 and bh>0 and x>=0 and y>=0 and x+bw<=sprite.width and y+bh<=sprite.height
   px,py=ox+dx,oy+dy
   assert 0<=px and 0<=py and px+bw<=w and py+bh<=h
   frame.alpha_composite(sprite.crop((x,y,x+bw,y+bh)),(px,py))
   if reserved:undecoded.append({'frame':fi,'layer':li,'reservedFlag':reserved})
  assert frame.getbbox() or row[1]==0,(uid,fi,'unexpected empty frame')
  atlas.alpha_composite(frame,((fi%cols)*w,(fi//cols)*h))
 buf=io.BytesIO();atlas.save(buf,format='PNG',optimize=True)
 move=f'content/unit/cgs/unit_move_cgs_{uid}.csv'
 anim={}
 for kind in ('idle','atk','move'):
  name=f'content/unit/cgs/unit_{kind}_cgs_{uid}.csv'
  if kind=='move' and name not in z.namelist():name=f'content/unit/cgs/unit_idle_cgs_{uid}.csv'
  seq=parse(z.read(name));assert seq and all(len(f)==4 and 0<=f[0]<len(frames) and f[3]>0 for f in seq)
  anim[kind]=seq
 return buf.getvalue(),anim,len(frames),undecoded,move not in z.namelist()

units=[];recipes=[];hits={};scopes={};support={};source_levels={}
with zipfile.ZipFile(io.BytesIO(blob)) as z:
 for key,row in M['records'].items():
  uid=int(key);base=row['ownedBaseId'];frm=row['fromId'];original=unit_catalog[uid]
  assert uid==frm+1 and base==uid-3
  assert (original['name'],original['element'],original['rarity'])==(row['name'],row['element'],5)
  assert original['nameSource']=='2022_Global_English'
  assert (original['unitMaxLevel'],original['unitCost'])==(row['originalMaxLevel'],row['originalUnitCost'])
  assert {v:original['unitBase'+v.title()] for v in ('hp','atk','def','rec')}==row['stats']
  assert {v:original['unitLord'+v.title()] for v in ('hp','atk','def','rec')}==row['lordStats']
  rec=lore[frm]['recipes'];assert len(rec)==1 and rec[0]['target']==uid
  src=rec[0];assert (src['zel'],src['karma'])==(200000,0) and src['zel']==row['sourceRecipe']['zel']
  materials=dict(collections.Counter(str(t['id']) for t in src['materials']))
  assert len(src['materials'])==5 and all(t['type']==1 for t in src['materials'])
  assert materials==row['sourceRecipe']['materials']
  bb=row['bb'];assert lore[uid]['bb']['name']==bb['name'] and lore[uid]['bb']['description']==bb['description']
  assert len(bb['levels'])==10
  for lvl,part in zip(bb['levels'],bb['levelInfo'].split('|')):
   n,code,params=part.split('@')[0].split(':')
   assert lvl['level']==int(n) and lvl['effectCode']==int(code) and lvl['params']==list(map(int,params.split(',')))
  if uid==40024:
   assert bb['target']=='support' and bb['levels'][0]['effectCode']==2500 and bb['levels'][0]['params']==[0,80,0,0,0,3,90]
  else:
   assert bb['target'] in ('single_enemy','all_enemies')
   assert bb['levels'][0]['effectCode'] in (1600,2300,3300,3400)
  for path,digest in row['sourceFilesSha256'].items():assert sha(z.read(path))==digest,(uid,path)
  atlas,animations,nframe,flags,missing=bake(z,uid)
  assert nframe==row['frameCount'] and missing==row['missingOriginalMoveCGS']
  assert (collections.Counter(str(f['reservedFlag']) for f in flags))==collections.Counter(row['unverifiedReservedFlags'])
  for filename,data in ((f'unit_anime_atlas_{uid}.png',atlas),(f'unit_ills_thum_{uid}.png',z.read(f'content/unit/img/unit_ills_thum_{uid}.png'))):
   path=A/'content/other_five_star'/filename
   path.parent.mkdir(parents=True,exist_ok=True)
   if path.exists():assert path.read_bytes()==data,(uid,filename,'asset conflicts')
   else:path.write_bytes(data)
  units.append({'id':uid,'name':row['name'],'element':['','Fire','Water','Earth','Thunder','Light','Dark'][row['element']],
                'rarity':5,'stats':row['stats'],'animation':animations,'atlas':f'content/other_five_star/unit_anime_atlas_{uid}.png',
                'portrait':f'content/other_five_star/unit_ills_thum_{uid}.png','frameWidth':480,'frameHeight':400,
                'columns':5,'frameCount':nframe,'scale':0.5,'anchorX':220,'anchorY':190,
                'originalMaxLevel':row['originalMaxLevel'],'originalUnitCost':row['originalUnitCost'],
                'originalLordStats':row['lordStats']})
  recipes.append({'baseId':base,'fromId':frm,'evolvedId':uid,'sourceRarity':4,'targetRarity':5,
                  'archivedZel':200000,'demoZel':7500,'materials':materials,'targetStats':row['stats'],
                  'frameCount':nframe,'animationNote':'2022 CGG source layers; reserved animation flags remain unverified where present'})
  scopes[key]={'name':bb['name'],'target':bb['target'],'skillId':uid}
  source_levels[key]={'name':bb['name'],'target':bb['target'],'levels':bb['levels'],'originalNativeDamageFormulaDecoded':False}
  if uid==40024:support[key]={'name':bb['name'],'kind':'atk_buff_all','pct':80,'rounds':3}
  groups=[]
  for section in bb['damageFramesRaw'].split('@'):
   parts=[list(map(int,p.split(':'))) for p in section.split(',') if p]
   assert parts and all(len(p)==4 for p in parts)
   groups.append(parts)
  hits[key]={'unitId':uid,'bbId':uid,'skillNameSource':f'MST_SKILLS_{uid}_NAME',
             'skillTypeRaw':bb['sourceType'],'targetTypeRaw':bb['sourceTargetType'],'targetAreaRaw':bb['sourceTargetArea'],
             'effectFramesRaw':bb['effectFramesRaw'],'skillStartFrameRaw':'0','damageFramesRaw':bb['damageFramesRaw'],
             'groups':groups,'groupWeights':[100 for _ in groups],'offensiveCandidate':bb['target']!='support',
             'firstGroupHitCount':len(groups[0])}
assert len(units)==len(recipes)==len(scopes)==len(hits)==len(source_levels)==6 and len(support)==1
mark='/* BF_GLOBAL_OTHER_FIVE_STAR_V036 */'
if mark in html:
 assert html.count(mark)==1 and all(f'unit_anime_atlas_{uid}.png' in html for uid in IDS)
 print('PASS existing v0.36 original playable source and sprites intact; no changes')
else:
 dec=json.JSONDecoder()
 def grow(text,anchor,add,old_count):
  assert text.count(anchor)==1,(anchor,text.count(anchor))
  i=text.index(anchor)+len(anchor);old,length=dec.raw_decode(text[i:]);assert len(old)==old_count,(anchor,len(old))
  if isinstance(old,list):
   key='id' if anchor=='window.BF_EVOLVED_UNITS=' else 'evolvedId'
   assert set(d[key] for d in old).isdisjoint(d[key] for d in add)
   old.extend(add)
  else:
   assert set(old).isdisjoint(add);old.update(add)
  return text[:i]+json.dumps(old,separators=(',',':'),ensure_ascii=True)+text[i+length:]
 html=grow(html,'window.BF_EVOLVED_UNITS=',units,36)
 html=grow(html,'const EVO_RECIPES=',recipes,36)
 html=grow(html,'window.BF_ARCHIVE_BB_HITS=',hits,54)
 safe=lambda obj:json.dumps(obj,ensure_ascii=True,separators=(',',':')).replace('</','<\\/')
 changes=[
  ('with first evolutions priced at 2,500 demo Zel and eligible second-stage evolutions at 5,000 demo Zel.',
   'with first, second and third evolutions priced at 2,500 / 5,000 / 7,500 demo Zel, respectively. Original archive costs are displayed separately.'),
  ('const bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||BF_VERIFIED_BB_V034[String(id)]||BF_VERIFIED_BB_V035[String(id)]||null;',
   'const BF_VERIFIED_BB_V036=Object.freeze('+safe(scopes)+');\nconst bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||BF_VERIFIED_BB_V034[String(id)]||BF_VERIFIED_BB_V035[String(id)]||BF_VERIFIED_BB_V036[String(id)]||null;'),
  ('function originalSupport(id){return BF_VERIFIED_BB_SUPPORT[String(id)]||BF_VERIFIED_SUPPORT_V032[String(id)]||BF_VERIFIED_SUPPORT_V034[String(id)]||null;}',
   'const BF_VERIFIED_SUPPORT_V036=Object.freeze('+safe(support)+');\nfunction originalSupport(id){return BF_VERIFIED_BB_SUPPORT[String(id)]||BF_VERIFIED_SUPPORT_V032[String(id)]||BF_VERIFIED_SUPPORT_V034[String(id)]||BF_VERIFIED_SUPPORT_V036[String(id)]||null;}\nwindow.BFOriginalFiveStarOther=Object.freeze({count:6,forUnit:id=>BF_VERIFIED_BB_V036[String(id)]||null,sourceLevelsFor:id=>BF_VERIFIED_RAW_LEVELS_V036[String(id)]?.levels||null});\nconst BF_VERIFIED_RAW_LEVELS_V036=Object.freeze('+safe(source_levels)+');'),
  ('const QUEST_DEMO_TIER4_MATERIALS=[10133,20133,30133,40133,50123,60123];',
   'const QUEST_DEMO_TIER4_MATERIALS=[10133,20133,30133,40133,50123,60123];\n// v0.36: original 5-star alternate recipe special materials; availability is DEMO only.\nconst QUEST_DEMO_SPECIAL_MATERIALS=[10191,20191,30191,40191,50191,60201];'),
  ("if(tier4)P.materials[tier4]=(P.materials[tier4]||0)+1;\n E.evoresult.textContent=`Quest reward: +1 demo catalyst ${mat}`+(tier4?` and +1 demo five-star catalyst ${tier4}`:'')+' (original enemy drop tables not recovered).';",
   "if(tier4)P.materials[tier4]=(P.materials[tier4]||0)+1;\n const special=P.questClears[QUEST.missionId]%18===0?QUEST_DEMO_SPECIAL_MATERIALS[Math.max(0,missionIdx)%6]:null;\n if(special)P.materials[special]=(P.materials[special]||0)+1;\n E.evoresult.textContent=`Quest reward: +1 demo catalyst ${mat}`+(tier4?` and +1 demo five-star catalyst ${tier4}`:'')+(special?` and +1 special demo catalyst ${special}`:'')+' (original enemy drop tables not recovered).';")
 ]
 for old,new in changes:
  assert html.count(old)==1,('Unexpected source anchor',old[:90],html.count(old))
  html=html.replace(old,new,1)
 assert html.count('const EVO_RECIPES=[')==1
 html=html.replace('const EVO_RECIPES=[',mark+'\nconst EVO_RECIPES=[',1)
 assert html.count(mark)==1
 index.write_text(html,'utf8')
 print('PASS v0.36: six original 5-star other forms, original scope/ATK support, DEMO attack-power fallback and special catalyst rewards')
