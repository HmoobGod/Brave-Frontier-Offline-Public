"""v0.38 — six source-authenticated alternate-path 6-star Global forms.

Original 2022 unit stats, English BB skill names/scopes, source sprite art,
CGG/CGS animation timing and evolution materials are SHA-verified. Native CGG
orientation/reserved/extra-transform semantics and offensive effect formulae
are not decoded, and stay transparently marked DEMO. Save version 7 untouched.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image
import base64,collections,csv,hashlib,io,json,math,re,zipfile
ROOT=Path(__file__).resolve().parent;A=ROOT/'app/src/main/assets';D=ROOT/'source_data'
M=json.loads((D/'bf_global_other_six_star_v038.json').read_text('utf8'))
IDS={10025,20025,30025,40025,50025,60025}
assert M['schema']=='bf-global-six-other-six-star-2022-v038'
assert M['provenance']['mstZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert set(map(int,M['records']))==IDS
sha=lambda b:hashlib.sha256(b).hexdigest()
pack=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Other_Six_Star.zip.b64').read_text('ascii'))
assert sha(pack)==M['sourcePackSha256']
index=A/'index.html';html=index.read_text('utf8')
for marker in ('/* BF_GLOBAL_SIX_STAR_STARTERS_V037 */','/* BF_GLOBAL_OTHER_FIVE_STAR_V036 */','/* BF_GLOBAL_BB_POWER_V030 */'):
 assert html.count(marker)==1,marker
assert 'bf_global_offline_demo_v7' in html

def embedded(key):
 found=re.search(r'<script type="application/json" id="'+re.escape(key)+r'">(.*?)</script>',html,re.S)
 assert found,key
 return {row['id']:row for row in json.loads(found.group(1))['units']}
source_units=embedded('bf-global-unit-catalog-data');source_lore=embedded('bf-original-unit-lore-data')
def parse(b):return [[int(v) for v in row if v.strip()] for row in csv.reader(io.StringIO(b.decode('utf-8-sig')))]

def bake(z,uid):
 sheet=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
 assert 512<=sheet.width<=1280 and 512<=sheet.height<=1280
 frames=parse(z.read(f'content/unit/cgg/unit_cgg_{uid}.csv'))
 assert 12<=len(frames)<=40
 fw,fh,cols,ox,oy=480,400,5,220,190
 atlas=Image.new('RGBA',(fw*cols,fh*math.ceil(len(frames)/cols)),(0,0,0,0))
 uncertain=[];clipped=0
 for fi,row in enumerate(frames):
  assert row[0]==0 and len(row)==2+row[1]*11
  frame=Image.new('RGBA',(fw,fh),(0,0,0,0))
  for li in range(row[1]):
   dx,dy,orientation,reserved,scale,extra,sx,sy,w,h,mode=row[2+li*11:2+(li+1)*11]
   assert orientation in (0,1,2) and reserved in (0,1) and extra in (0,90) and mode==0 and 0<scale<=100
   assert sx>=0 and sy>=0 and w>0 and h>0 and sx+w<=sheet.width and sy+h<=sheet.height
   tile=sheet.crop((sx,sy,sx+w,sy+h))
   # BF_GLOBAL_6STAR_THUNDER_FLIP_OPACITY_V13200: only the three
   # sourced transform layers of 6-star Thunder alternate #40025.
   # Community CGG mapping: orientation=horizontal flip, scale=opacity %.
   # No source blend/rotation/Page transforms on this particular form.
   if uid==40025:
    assert (reserved,extra,mode)==(0,0,0)
    assert orientation in (0,1) and scale in (50,100)
    if orientation:
     assert (fi,li,scale)==(15,1,100)
     tile=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if scale!=100:
     assert (fi,li,orientation) in ((6,6,0),(24,0,0))
     tile.putalpha(tile.getchannel('A').point(lambda a:round(a*scale/100)))
   elif scale!=100:
    # BF_GLOBAL_6STAR_OPACITY_FIX_V13100: verified 2022 #30025 source
    # Original column 4 is opacity, not sprite scale. This single form has
    # six 50%-opacity layers in source frame 19, no flips/blend/rotation.
    # Keep the old generator unchanged for all other forms until their
    # native blend/transform semantics receive independent visual proof.
    if uid==30025:
     assert fi==19 and li in range(3,9) and scale==50
     assert (orientation,reserved,extra,mode)==(0,0,0,0)
     tile.putalpha(tile.getchannel('A').point(lambda a:round(a*scale/100)))
    else:
     tile=tile.resize((max(1,round(w*scale/100)),max(1,round(h*scale/100))),Image.Resampling.NEAREST)
   x,y=ox+dx,oy+dy
   if x<0 or y<0 or x+tile.width>fw or y+tile.height>fh:clipped+=1
   frame.alpha_composite(tile,(x,y))  # native clipping, source pixel content unchanged
   if (orientation,reserved,scale,extra)!=(0,0,100,0):
    uncertain.append({'frame':fi,'layer':li,'orientationCode':orientation,'reservedFlag':reserved,'scalePercent':scale,'extraTransformRaw':extra})
  if not frame.getbbox():
   assert fi in M['records'][str(uid)]['emptySourceFrames'],(uid,fi,'unexpected fully transparent frame')
  atlas.alpha_composite(frame,((fi%cols)*fw,(fi//cols)*fh))
 buf=io.BytesIO();atlas.save(buf,format='PNG',optimize=True)
 sequences={}
 allfiles=set(z.namelist())
 for kind in ('idle','atk','move'):
  file=f'content/unit/cgs/unit_{kind}_cgs_{uid}.csv'
  if kind=='move' and file not in allfiles:file=f'content/unit/cgs/unit_idle_cgs_{uid}.csv'
  sequence=parse(z.read(file))
  assert sequence and all(len(v)==4 and 0<=v[0]<len(frames) and v[3]>0 for v in sequence)
  sequences[kind]=sequence
 return buf.getvalue(),sequences,len(frames),uncertain,clipped

forms=[];recipes=[];scopes={};hits={};support={};rawlevels={}
with zipfile.ZipFile(io.BytesIO(pack)) as z:
 for key,item in M['records'].items():
  uid=int(key);base=item['ownedBaseId'];frm=item['fromId'];unit=source_units[uid]
  assert uid==frm+1 and base==uid-4
  assert unit['nameSource']=='2022_Global_English'
  assert (unit['name'],unit['element'],unit['rarity'])==(item['name'],item['element'],6)
  assert unit['unitMaxLevel']==item['originalMaxLevel']==100 and unit['unitCost']==item['originalUnitCost']
  assert {p:unit['unitBase'+p.title()] for p in ('hp','atk','def','rec')}==item['stats']
  assert {p:unit['unitLord'+p.title()] for p in ('hp','atk','def','rec')}==item['lordStats']
  rec=source_lore[frm]['recipes'];assert len(rec)==1 and rec[0]['target']==uid
  origin=rec[0];assert origin['zel']==item['sourceRecipe']['zel']==500000 and origin['karma']==0
  assert all(m['type']==1 for m in origin['materials'])
  materials=dict(collections.Counter(str(m['id']) for m in origin['materials']))
  assert materials==item['sourceRecipe']['materials'] and materials['50354']==1
  bb=item['bb'];assert (source_lore[uid]['bb']['name'],source_lore[uid]['bb']['description'])==(bb['name'],bb['description'])
  assert len(bb['levels'])==10
  for i,part in enumerate(bb['levelInfo'].split('|')):
   n,code,params=part.split('@')[0].split(':')
   assert bb['levels'][i]['level']==int(n)==i+1
   assert bb['levels'][i]['effectCode']==int(code) and bb['levels'][i]['params']==[int(v) for v in params.split(',')]
   assert bb['levels'][i]['extraGroupsRaw']==part.split('@')[1:]
  if uid==40025:
   assert bb['target']=='support' and bb['levels'][0]['effectCode']==2500 and bb['levels'][0]['params']==[0,94,0,0,0,3,170]
   # 94 point source parameter, interpreted through existing DEMO support implementation.
   support[key]={'name':bb['name'],'kind':'atk_buff_all','pct':94,'rounds':3}
  else:
   assert bb['target'] in ('single_enemy','all_enemies')
   assert bb['levels'][0]['effectCode'] in (1800,2300,3300,3400)
   # These effect codes are NOT decoded; no new original damage-power values.
  for file,digest in item['sourceFilesSha256'].items():assert sha(z.read(file))==digest,(uid,file)
  atlas,anim,nframes,flags,clipped=bake(z,uid)
  assert nframes==item['frameCount'] and flags==item['unverifiedSpriteLayers']
  for filename,src in ((f'unit_anime_atlas_{uid}.png',atlas),(f'unit_ills_thum_{uid}.png',z.read(f'content/unit/img/unit_ills_thum_{uid}.png'))):
   dest=A/'content/other_six_star'/filename;dest.parent.mkdir(parents=True,exist_ok=True)
   if dest.exists():assert dest.read_bytes()==src,(uid,'source art conflict',filename)
   else:dest.write_bytes(src)
  forms.append({'id':uid,'name':item['name'],'element':['','Fire','Water','Earth','Thunder','Light','Dark'][item['element']],
      'rarity':6,'stats':item['stats'],'animation':anim,
      'atlas':f'content/other_six_star/unit_anime_atlas_{uid}.png','portrait':f'content/other_six_star/unit_ills_thum_{uid}.png',
      'frameWidth':480,'frameHeight':400,'columns':5,'frameCount':nframes,'scale':0.5,'anchorX':220,'anchorY':190,
      'originalMaxLevel':item['originalMaxLevel'],'originalUnitCost':item['originalUnitCost'],'originalLordStats':item['lordStats']})
  recipes.append({'baseId':base,'fromId':frm,'evolvedId':uid,'sourceRarity':5,'targetRarity':6,
      'archivedZel':500000,'demoZel':10000,'materials':materials,'targetStats':item['stats'],'frameCount':nframes,
      'animationNote':'2022 source CGG/CGS; unverified orientation and extra 90-degree transform intentionally not guessed'})
  scopes[key]={'name':bb['name'],'target':bb['target'],'skillId':uid}
  rawlevels[key]={'name':bb['name'],'target':bb['target'],'levels':bb['levels'],'originalNativeDamageFormulaDecoded':False}
  groups=[]
  for group in bb['damageFramesRaw'].split('@'):
   seq=[[int(v) for v in hit.split(':')] for hit in group.split(',') if hit]
   assert seq and all(len(row)==4 for row in seq)
   groups.append(seq)
  hits[key]={'unitId':uid,'bbId':uid,'skillNameSource':f'MST_SKILLS_{uid}_NAME',
    'skillTypeRaw':bb['sourceType'],'targetTypeRaw':bb['sourceTargetType'],'targetAreaRaw':bb['sourceTargetArea'],
    'effectFramesRaw':bb['effectFramesRaw'],'skillStartFrameRaw':'0','damageFramesRaw':bb['damageFramesRaw'],
    'groups':groups,'groupWeights':[100 for _ in groups],'offensiveCandidate':bb['target']!='support','firstGroupHitCount':len(groups[0])}
  print('Verified original 6-star',uid,item['name'],'source frames',nframes,'uncertain layers',len(flags),'clipped',clipped)
assert len(forms)==len(recipes)==len(scopes)==len(hits)==len(rawlevels)==6 and len(support)==1
mark='/* BF_GLOBAL_OTHER_SIX_STAR_V038 */'
if mark in html:
 assert html.count(mark)==1 and all(f'unit_anime_atlas_{uid}.png' in html for uid in IDS)
 print('PASS v0.38 idempotent original 6-star source and artwork unchanged')
else:
 decoder=json.JSONDecoder()
 def grow(text,anchor,new,expected):
  assert text.count(anchor)==1,(anchor,text.count(anchor))
  p=text.index(anchor)+len(anchor);old,used=decoder.raw_decode(text[p:]);assert len(old)==expected,(anchor,len(old))
  if isinstance(old,list):
   attr='id' if anchor=='window.BF_EVOLVED_UNITS=' else 'evolvedId'
   assert {row[attr] for row in old}.isdisjoint(row[attr] for row in new)
   old.extend(new)
  else:
   assert set(old).isdisjoint(new);old.update(new)
  return text[:p]+json.dumps(old,separators=(',',':'),ensure_ascii=True)+text[p+used:]
 html=grow(html,'window.BF_EVOLVED_UNITS=',forms,48)
 html=grow(html,'const EVO_RECIPES=',recipes,48)
 html=grow(html,'window.BF_ARCHIVE_BB_HITS=',hits,66)
 safe=lambda obj:json.dumps(obj,separators=(',',':'),ensure_ascii=True).replace('</','<\\/')
 changes=[
  ('const bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||BF_VERIFIED_BB_V034[String(id)]||BF_VERIFIED_BB_V035[String(id)]||BF_VERIFIED_BB_V036[String(id)]||BF_VERIFIED_BB_V037[String(id)]||null;',
   'const BF_VERIFIED_BB_V038=Object.freeze('+safe(scopes)+');\nconst bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||BF_VERIFIED_BB_V034[String(id)]||BF_VERIFIED_BB_V035[String(id)]||BF_VERIFIED_BB_V036[String(id)]||BF_VERIFIED_BB_V037[String(id)]||BF_VERIFIED_BB_V038[String(id)]||null;'),
  ('function originalSupport(id){return BF_VERIFIED_BB_SUPPORT[String(id)]||BF_VERIFIED_SUPPORT_V032[String(id)]||BF_VERIFIED_SUPPORT_V034[String(id)]||BF_VERIFIED_SUPPORT_V036[String(id)]||null;}',
   'const BF_VERIFIED_SUPPORT_V038=Object.freeze('+safe(support)+');\nfunction originalSupport(id){return BF_VERIFIED_BB_SUPPORT[String(id)]||BF_VERIFIED_SUPPORT_V032[String(id)]||BF_VERIFIED_SUPPORT_V034[String(id)]||BF_VERIFIED_SUPPORT_V036[String(id)]||BF_VERIFIED_SUPPORT_V038[String(id)]||null;}\nconst BF_VERIFIED_RAW_LEVELS_V038=Object.freeze('+safe(rawlevels)+');\nwindow.BFOriginalOtherSixStar=Object.freeze({count:6,forUnit:id=>BF_VERIFIED_BB_V038[String(id)]||null,sourceLevelsFor:id=>BF_VERIFIED_RAW_LEVELS_V038[String(id)]?.levels||null});'),
  ('const QUEST_DEMO_SIX_STAR_CATALYST=50354;',
   'const QUEST_DEMO_SIX_STAR_CATALYST=50354;\n// Source IDs for six-star alternate lines: guaranteed availability DEMO only.\nconst QUEST_DEMO_OTHER_SIX_STAR_CATALYSTS=[60144,60224];')
 ]
 for old,new in changes:
  assert html.count(old)==1,('unexpected patched code',old[:95],html.count(old))
  html=html.replace(old,new,1)
 needle='if(holy)P.materials[holy]=(P.materials[holy]||0)+1;'
 assert html.count(needle)==1
 html=html.replace(needle,needle+'\n const special6=P.questClears[QUEST.missionId]%30===0?60144:null;\n const special7=P.questClears[QUEST.missionId]%36===0?60224:null;\n if(special6)P.materials[special6]=(P.materials[special6]||0)+1;\n if(special7)P.materials[special7]=(P.materials[special7]||0)+1;',1)
 # Expose to users which new DEMO materials were granted.
 prior='(holy?` and +1 six-star demo catalyst ${holy}`:\'\')'
 assert html.count(prior)==1
 html=html.replace(prior,prior+'+(special6?` and +1 alternate six-star demo catalyst ${special6}`:\'\')+(special7?` and +1 alternate six-star demo catalyst ${special7}`:\'\')',1)
 assert html.count('const EVO_RECIPES=[')==1
 html=html.replace('const EVO_RECIPES=[',mark+'\nconst EVO_RECIPES=[',1)
 index.write_text(html,'utf8')
 print('PASS v0.38 six other original 6-star evolutions, source skill scopes/support and separate DEMO catalysts, saved v7 retained')
