"""v0.37: source-backed original Global 6-star starter evolutions.

Only source assets and recovered fields are labeled original. Native CGG
orientation/reserved semantics, damage formula, spark and economy remain DEMO.
Existing 18 owned base IDs and v7 saved progress are never migrated.
"""
from __future__ import annotations
import base64,csv,hashlib,io,json,math,re,zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets';D=ROOT/'source_data'
M=json.loads((D/'bf_global_six_star_starters_v037.json').read_text('utf8'))
IDS={10015,20015,30015,40015,50015,60015}
assert M['schema']=='bf-global-six-original-six-star-starters-2022-v037'
assert M['provenance']['mstZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert set(map(int,M['records']))==IDS
sha=lambda b:hashlib.sha256(b).hexdigest()
pack=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Six_Star_Starters.zip.b64').read_text('ascii'))
assert sha(pack)==M['sourcePackSha256']
html=(A/'index.html').read_text('utf8')
for marker in ('/* BF_GLOBAL_OTHER_FIVE_STAR_V036 */','/* BF_GLOBAL_FIVE_STAR_STARTERS_V035 */','/* BF_GLOBAL_BB_POWER_V030 */'):
 assert html.count(marker)==1,marker
assert 'bf_global_offline_demo_v7' in html

def embedded(tag):
 m=re.search(r'<script type="application/json" id="'+re.escape(tag)+r'">(.*?)</script>',html,re.S)
 assert m,tag
 return {x['id']:x for x in json.loads(m.group(1))['units']}
units_catalog=embedded('bf-global-unit-catalog-data');lore=embedded('bf-original-unit-lore-data')
def parse(data):return [[int(x) for x in row if x.strip()] for row in csv.reader(io.StringIO(data.decode('utf-8-sig')))]

def bake(z,id):
 sprite=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{id}.png'))).convert('RGBA')
 assert sprite.width in (640,720,800) and sprite.height==sprite.width
 frames=parse(z.read(f'content/unit/cgg/unit_cgg_{id}.csv'))
 assert 12<=len(frames)<=40
 fw,fh,cols,ox,oy=480,400,5,220,190
 atlas=Image.new('RGBA',(fw*cols,fh*math.ceil(len(frames)/cols)),(0,0,0,0))
 uncertain=[];clip_count=0
 for fi,row in enumerate(frames):
  assert row[0]==0 and len(row)==2+row[1]*11
  frame=Image.new('RGBA',(fw,fh),(0,0,0,0))
  for li in range(row[1]):
   dx,dy,orientation,reserved,scale,unused,x,y,bw,bh,mode=row[2+11*li:2+11*(li+1)]
   assert orientation in (0,1,2) and reserved in (0,1) and unused==mode==0
   assert scale in (30,40,50,60,70,80,100)
   assert x>=0 and y>=0 and bw>0 and bh>0 and x+bw<=sprite.width and y+bh<=sprite.height
   tile=sprite.crop((x,y,x+bw,y+bh))
   if scale!=100:
    tile=tile.resize((max(1,round(bw*scale/100)),max(1,round(bh*scale/100))),Image.Resampling.NEAREST)
   px,py=ox+dx,oy+dy
   if not (0<=px and 0<=py and px+tile.width<=fw and py+tile.height<=fh):clip_count+=1
   # Pillow clips layers crossing atlas-cell edges, preserving transparency.
   frame.alpha_composite(tile,(px,py))
   if (orientation,reserved,scale)!=(0,0,100):
    uncertain.append({'frame':fi,'layer':li,'orientationCode':orientation,'reservedFlag':reserved,'scalePercent':scale})
  if not frame.getbbox():assert row[1]==0,(id,fi,'unexpected invisible original source frame')
  atlas.alpha_composite(frame,((fi%cols)*fw,(fi//cols)*fh))
 buf=io.BytesIO();atlas.save(buf,format='PNG',optimize=True)
 animation={}
 for mode in ('idle','atk','move'):
  sequence=parse(z.read(f'content/unit/cgs/unit_{mode}_cgs_{id}.csv'))
  assert sequence and all(len(x)==4 and 0<=x[0]<len(frames) and x[3]>0 for x in sequence)
  animation[mode]=sequence
 return buf.getvalue(),animation,len(frames),uncertain,clip_count

forms=[];recipes=[];scopes={};powers={};hits={};rawlevels={}
with zipfile.ZipFile(io.BytesIO(pack)) as z:
 for key,item in M['records'].items():
  uid=int(key);original=units_catalog[uid];prev=item['fromId'];base=item['ownedBaseId']
  assert uid==prev+1 and base==uid-4
  assert original['nameSource']=='2022_Global_English'
  assert (original['name'],original['element'],original['rarity'])==(item['name'],item['element'],6)
  assert original['unitMaxLevel']==item['originalMaxLevel']==100 and original['unitCost']==item['originalUnitCost']
  assert item['stats']=={x:original['unitBase'+x.title()] for x in ('hp','atk','def','rec')}
  assert item['lordStats']=={x:original['unitLord'+x.title()] for x in ('hp','atk','def','rec')}
  source=lore[prev]['recipes'];assert len(source)==1 and source[0]['target']==uid
  assert source[0]['zel']==item['sourceRecipe']['zel']==500000 and source[0]['karma']==item['sourceRecipe']['karma']==0
  assert sorted(str(m['id']) for m in source[0]['materials'])==sorted(str(k) for k in item['sourceRecipe']['materials'] for _ in range(item['sourceRecipe']['materials'][k]))
  assert all(m['type']==1 for m in source[0]['materials'])
  assert item['sourceRecipe']['materials']['50354']==1
  bb=item['bb'];assert lore[uid]['bb']['name']==bb['name'] and lore[uid]['bb']['description']==bb['description']
  assert bb['target']=='all_enemies' and len(bb['levels'])==10
  for i,part in enumerate(bb['levelInfo'].split('|')):
   level,code,params=part.split('@')[0].split(':')
   assert bb['levels'][i]=={'level':i+1,'effectCode':2500,'params':[int(v) for v in params.split(',')]}
   assert int(level)==i+1 and int(code)==2500
  assert bb['levels'][0]['params']==[100,80,0,0,0,0]
  for file,digest in item['sourceFilesSha256'].items():assert sha(z.read(file))==digest,(uid,file)
  atlas,animation,frames,unknown,clipped=bake(z,uid)
  assert frames==item['frameCount'] and unknown==item['unverifiedSpriteLayers']
  for name,data in ((f'unit_anime_atlas_{uid}.png',atlas),(f'unit_ills_thum_{uid}.png',z.read(f'content/unit/img/unit_ills_thum_{uid}.png'))):
   target=A/'content/six_star_evolution'/name;target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists():assert target.read_bytes()==data,(uid,'modified original atlas/portrait')
   else:target.write_bytes(data)
  forms.append({'id':uid,'name':item['name'],'element':['','Fire','Water','Earth','Thunder','Light','Dark'][item['element']],
   'rarity':6,'stats':item['stats'],'animation':animation,
   'atlas':f'content/six_star_evolution/unit_anime_atlas_{uid}.png',
   'portrait':f'content/six_star_evolution/unit_ills_thum_{uid}.png',
   'frameWidth':480,'frameHeight':400,'columns':5,'frameCount':frames,'scale':0.5,'anchorX':220,'anchorY':190,
   'originalMaxLevel':item['originalMaxLevel'],'originalUnitCost':item['originalUnitCost'],'originalLordStats':item['lordStats']})
  recipes.append({'baseId':base,'fromId':prev,'evolvedId':uid,'sourceRarity':5,'targetRarity':6,
   'archivedZel':500000,'demoZel':10000,'materials':item['sourceRecipe']['materials'],
   'targetStats':item['stats'],'frameCount':frames,
   'animationNote':'Source CGG/CGS/PNG: clipping preserved; native nonzero orientation and reserved flags unverified'})
  scopes[key]={'name':bb['name'],'target':'all_enemies','skillId':uid}
  # First numeric source parameter is applied only as labeled DEMO scalar,
  # just as the existing 5-star source-effect 2500 case; 80 remains unmodeled.
  powers[key]={'name':bb['name'],'target':'all_enemies','base':100,
   'levels':[x['params'][0] for x in bb['levels']],'secondaryUnmodeled':True}
  rawlevels[key]={'name':bb['name'],'levels':bb['levels']}
  groups=[]
  for group in bb['damageFramesRaw'].split('@'):
   seq=[[int(n) for n in hit.split(':')] for hit in group.split(',') if hit]
   assert seq and all(len(hit)==4 for hit in seq)
   groups.append(seq)
  hits[key]={'unitId':uid,'bbId':uid,'skillNameSource':f'MST_SKILLS_{uid}_NAME',
   'skillTypeRaw':bb['sourceType'],'targetTypeRaw':bb['sourceTargetType'],
   'targetAreaRaw':bb['sourceTargetArea'],'effectFramesRaw':bb['effectFramesRaw'],
   'skillStartFrameRaw':'0','damageFramesRaw':bb['damageFramesRaw'],
   'groups':groups,'groupWeights':[100 for _ in groups],
   'offensiveCandidate':True,'firstGroupHitCount':len(groups[0])}
  print('Verified original',uid,item['name'],'frames',frames,'clipped source layers',clipped)
assert len(forms)==len(recipes)==len(scopes)==len(powers)==len(hits)==6
mark='/* BF_GLOBAL_SIX_STAR_STARTERS_V037 */'
if mark in html:
 assert html.count(mark)==1 and all(f'unit_anime_atlas_{uid}.png' in html for uid in IDS)
 print('PASS v0.37 six-star source and existing built HTML unchanged')
else:
 decoder=json.JSONDecoder()
 def grow(text,anchor,new,expected):
  assert text.count(anchor)==1,(anchor,text.count(anchor))
  p=text.index(anchor)+len(anchor);old,used=decoder.raw_decode(text[p:]);assert len(old)==expected,(anchor,len(old))
  if isinstance(old,list):
   attr='id' if anchor=='window.BF_EVOLVED_UNITS=' else 'evolvedId'
   assert set(x[attr] for x in old).isdisjoint(x[attr] for x in new)
   old+=new
  else:
   assert set(old).isdisjoint(new);old.update(new)
  return text[:p]+json.dumps(old,separators=(',',':'),ensure_ascii=True)+text[p+used:]
 html=grow(html,'window.BF_EVOLVED_UNITS=',forms,42)
 html=grow(html,'const EVO_RECIPES=',recipes,42)
 html=grow(html,'window.BF_ARCHIVE_BB_HITS=',hits,60)
 compact=lambda x:json.dumps(x,separators=(',',':'),ensure_ascii=True)
 pairs=[
  ('const bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||BF_VERIFIED_BB_V034[String(id)]||BF_VERIFIED_BB_V035[String(id)]||BF_VERIFIED_BB_V036[String(id)]||null;',
   'const BF_VERIFIED_BB_V037=Object.freeze('+compact(scopes)+');\nconst bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||BF_VERIFIED_BB_V034[String(id)]||BF_VERIFIED_BB_V035[String(id)]||BF_VERIFIED_BB_V036[String(id)]||BF_VERIFIED_BB_V037[String(id)]||null;'),
  ('const bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||BF_VERIFIED_POWER_V032[String(id)]||BF_VERIFIED_POWER_V033[String(id)]||BF_VERIFIED_POWER_V034[String(id)]||BF_VERIFIED_POWER_V035[String(id)]||null;',
   'const BF_VERIFIED_POWER_V037=Object.freeze('+compact(powers)+');\nconst BF_VERIFIED_RAW_LEVELS_V037=Object.freeze('+compact(rawlevels)+');\nwindow.BFOriginalSixStar=Object.freeze({count:6,sourceLevelsFor:id=>BF_VERIFIED_RAW_LEVELS_V037[String(id)]?.levels||null});\nconst bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||BF_VERIFIED_POWER_V032[String(id)]||BF_VERIFIED_POWER_V033[String(id)]||BF_VERIFIED_POWER_V034[String(id)]||BF_VERIFIED_POWER_V035[String(id)]||BF_VERIFIED_POWER_V037[String(id)]||null;'),
  ('const QUEST_DEMO_SPECIAL_MATERIALS=[10191,20191,30191,40191,50191,60201];',
   'const QUEST_DEMO_SPECIAL_MATERIALS=[10191,20191,30191,40191,50191,60201];\n// Original ID 50354 is source-backed; guaranteed availability is DEMO only.\nconst QUEST_DEMO_SIX_STAR_CATALYST=50354;')]
 for old,new in pairs:
  assert html.count(old)==1,('Original source insertion anchor shifted',old[:80],html.count(old))
  html=html.replace(old,new,1)
 # Preserve earlier 6th/12th/18th quest rewards, add shared 50354 every 24th.
 marker='P.materials[special]=(P.materials[special]||0)+1;'
 where=html.find(marker)
 if where<0:
  p=html.find('function awardDemoRewards(){')
  print('ERROR reward snippet:',html[p:p+1300]);raise ValueError('Unexpected prior award schedule')
 assert html.count(marker)==1
 html=html.replace(marker,marker+'\n const holy=P.questClears[QUEST.missionId]%24===0?QUEST_DEMO_SIX_STAR_CATALYST:null;\n if(holy)P.materials[holy]=(P.materials[holy]||0)+1;',1)
 # original html quest text now includes additional reward when present;
 # differentiate the shared item source ID from actual guaranteed demo drop.
 message='(original enemy drop tables not recovered).'
 assert html.count(message)>=1
 html=html.replace(message,"(original enemy drop tables not recovered; six-star catalyst rewards are DEMO).",1)
 # Show the extra catalyst actually granted by the 24th-clear milestone.
 before="(special?` and +1 special demo catalyst ${special}`:'')+' (original enemy drop tables not recovered; six-star catalyst rewards are DEMO).'"
 after="(special?` and +1 special demo catalyst ${special}`:'')+(holy?` and +1 six-star demo catalyst ${holy}`:'')+' (original enemy drop tables not recovered; six-star catalyst rewards are DEMO).'"
 assert html.count(before)==1
 html=html.replace(before,after,1)
 assert html.count('const EVO_RECIPES=[')==1
 html=html.replace('const EVO_RECIPES=[',mark+'\nconst EVO_RECIPES=[',1)
 (A/'index.html').write_text(html,'utf8')
 print('PASS v0.37 six original 6-star starter evolutions, source BB data, v7 chained progression, DEMO 50354 reward')
