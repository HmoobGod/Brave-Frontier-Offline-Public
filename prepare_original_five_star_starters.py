"""v0.35: append six original 5-star Global starter evolutions without save migration.

Checks unchanged original Global MST/English codex records and SHA256 archive PNG,
CGG, CGS, thumbs. Renders original sprite layers into battle atlases with the
established v0.34 renderer. CGG orientation-code semantics for Death Magress
remain UNKNOWN; we preserve native PNG pixels/layer positions/recorded scale
without inventing a rotation/flip algorithm. Level-1 BB power uses existing
DEMO 1+first-source-parameter/100 interpretation, not original damage formula.
"""
from __future__ import annotations
import base64,collections,csv,gzip,hashlib,io,json,math,re,zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets';D=ROOT/'source_data'
M=json.loads((D/'bf_global_six_five_star_v035.json').read_text('utf8'))
IDS={10014,20014,30014,40014,50014,60014}
assert M['schema']=='bf-global-six-five-star-starters-2022-v035'
assert M['provenance']['mstZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert {int(k) for k in M['records']}==IDS
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Six_Five_Star.zip.b64').read_text('ascii'))
assert sha(blob)==M['sourcePackSha256']
html=(A/'index.html').read_text('utf8')
for marker in ['/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */','/* BF_GLOBAL_SECOND_EVOLUTIONS_V033 */','/* BF_GLOBAL_BB_POWER_V030 */']:
    assert html.count(marker)==1
assert 'bf_global_offline_demo_v7' in html

def embedded(key):
    match=re.search(r'<script type="application/json" id="'+re.escape(key)+r'">(.*?)</script>',html,re.S)
    assert match,key
    return {row['id']:row for row in json.loads(match.group(1))['units']}
original=embedded('bf-global-unit-catalog-data')
lore=embedded('bf-original-unit-lore-data')
def parse(data):return [[int(x) for x in row if x.strip()] for row in csv.reader(io.StringIO(data.decode('utf-8-sig')))]

def bake(z,id):
    sprite=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{id}.png'))).convert('RGBA')
    assert sprite.size==(512,512)
    frames=parse(z.read(f'content/unit/cgg/unit_cgg_{id}.csv'))
    assert 8<=len(frames)<=35
    fw,fh,ncol,originx,originy=480,400,5,220,190
    atlas=Image.new('RGBA',(fw*ncol,fh*math.ceil(len(frames)/ncol)),(0,0,0,0));unknown=[]
    for fi,row in enumerate(frames):
        assert row[0]==0 and len(row)==2+row[1]*11
        frame=Image.new('RGBA',(fw,fh),(0,0,0,0))
        for j in range(row[1]):
            dx,dy,orientation,rsv,scale,unused,x,y,w,h,mode=row[2+j*11:2+(j+1)*11]
            assert orientation in (0,2) and rsv==unused==mode==0
            assert scale in (30,40,60,80,100)
            assert x>=0 and y>=0 and w>0 and h>0 and x+w<=sprite.width and y+h<=sprite.height
            patch=sprite.crop((x,y,x+w,y+h))
            # BF_GLOBAL_5STAR_DARK_SOURCE_CGG_V14600:
            # Original 2022 Global #60014 (Death Magress) CGG uses code 2
            # for vertical flip, and field five is opacity, not size scale.
            # This is an isolated source-based correction: original blend
            # and rotation codes are zero for ALL 251 source sprite layers.
            if id==60014:
                expected_flip={(24,1),(24,8),(25,8),(25,12),
                               (26,8),(26,9),(26,11),(26,12)}
                expected_alpha={
                   (26,0):60,(26,1):60,(26,2):60,(26,3):60,
                   (26,4):60,(26,5):60,(26,6):60,(26,7):60,
                   (26,8):60,(26,9):60,(26,11):80,(26,12):80,
                   (26,13):80,(27,0):30,(27,1):30,(27,2):30,
                   (27,3):30,(28,0):40}
                assert rsv==unused==mode==0
                assert (orientation==2)==((fi,j) in expected_flip)
                assert scale==expected_alpha.get((fi,j),100)
                if orientation==2:
                    patch=patch.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                if scale!=100:
                    patch.putalpha(patch.getchannel('A').point(
                        lambda a:round(a*scale/100)))
            elif scale!=100:
                patch=patch.resize((max(1,round(w*scale/100)),
                    max(1,round(h*scale/100))),Image.Resampling.NEAREST)
            dest=(originx+dx,originy+dy)
            assert dest[0]>=0 and dest[1]>=0 and dest[0]+patch.width<=fw and dest[1]+patch.height<=fh
            frame.alpha_composite(patch,dest)
            if orientation or scale!=100:unknown.append({'frame':fi,'layer':j,'orientationCode':orientation,'scalePercent':scale})
        assert frame.getbbox(),(id,fi,'empty animation frame')
        atlas.alpha_composite(frame,((fi%ncol)*fw,(fi//ncol)*fh))
    buf=io.BytesIO();atlas.save(buf,format='PNG',optimize=True)
    anim={}
    for kind in ('idle','atk','move'):
        seq=parse(z.read(f'content/unit/cgs/unit_{kind}_cgs_{id}.csv'))
        assert seq and all(len(key)==4 and 0<=key[0]<len(frames) and key[3]>0 for key in seq)
        anim[kind]=seq
    return buf.getvalue(),anim,len(frames),unknown

units=[];recipes=[];power={};scopes={};hits={}
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    assert len(z.namelist())==6*6
    for key,item in M['records'].items():
        id=int(key);base=item['ownedBaseId'];frm=item['fromId'];db=original[id]
        assert id==frm+1 and base==id-3
        assert (db['name'],db['element'],db['rarity'])==(item['name'],item['element'],5)
        assert db['nameSource']=='2022_Global_English'
        assert (db['unitMaxLevel'],db['unitCost'])==(item['originalMaxLevel'],item['originalUnitCost'])
        assert {k:db['unitBase'+k.title()] for k in ('hp','atk','def','rec')}==item['stats']
        assert {k:db['unitLord'+k.title()] for k in ('hp','atk','def','rec')}==item['lordStats']
        source_recipes=lore[frm]['recipes']
        assert len(source_recipes)==1 and source_recipes[0]['target']==id
        src=source_recipes[0];assert src['zel']==item['sourceRecipe']['zel']==200000 and src['karma']==0
        amounts=collections.Counter(str(m['id']) for m in src['materials'])
        assert all(m['type']==1 for m in src['materials']) and dict(amounts)==item['sourceRecipe']['materials']
        bb=item['bb'];assert lore[id]['bb']['name']==bb['name'] and lore[id]['bb']['description']==bb['description']
        assert bb['target']=='all_enemies' and bb['effectCode']==2500
        assert len(bb['firstParameterByLevel'])==10 and bb['firstParameterByLevel']==[70,80,90,100,110,120,130,140,150,160]
        for i,section in enumerate(bb['levelInfo'].split('|')):
            n,code,params=section.split('@')[0].split(':');numbers=list(map(int,params.split(',')))
            assert int(n)==i+1 and int(code)==2500 and numbers==[bb['firstParameterByLevel'][i],60,0,0,0,0]
        for name,digest in item['sourceFilesSha256'].items():assert sha(z.read(name))==digest,(id,name)
        atlas,animation,num,transforms=bake(z,id)
        assert num==item['frameCount'] and transforms==item['unverifiedSpriteTransformLayers']
        assets=[(f'unit_anime_atlas_{id}.png',atlas),
                (f'unit_ills_thum_{id}.png',z.read(f'content/unit/img/unit_ills_thum_{id}.png'))]
        for name,data in assets:
            file=A/'content/five_star_evolution'/name
            file.parent.mkdir(parents=True,exist_ok=True)
            if file.is_file():assert file.read_bytes()==data,(id,'unexpected modified source art')
            else:file.write_bytes(data)
        units.append({'id':id,'name':item['name'],'element':['','Fire','Water','Earth','Thunder','Light','Dark'][db['element']],
            'rarity':5,'stats':item['stats'],'animation':animation,'atlas':f'content/five_star_evolution/unit_anime_atlas_{id}.png',
            'portrait':f'content/five_star_evolution/unit_ills_thum_{id}.png',
            'frameWidth':480,'frameHeight':400,'columns':5,'frameCount':num,'scale':0.5,'anchorX':220,'anchorY':190,
            'originalMaxLevel':item['originalMaxLevel'],'originalUnitCost':item['originalUnitCost'],'originalLordStats':item['lordStats']})
        recipes.append({'baseId':base,'fromId':frm,'evolvedId':id,'sourceRarity':4,'targetRarity':5,
            'archivedZel':200000,'demoZel':7500,'materials':dict(amounts),'targetStats':item['stats'],
            'frameCount':num,'animationNote':'Original 2022 CGG/CGS/PNG, native orientation-code effects not fully decoded'})
        scopes[key]={'name':bb['name'],'target':'all_enemies','skillId':id}
        power[key]={'name':bb['name'],'target':'all_enemies','base':bb['firstParameterByLevel'][0],
            'levels':bb['firstParameterByLevel'],'secondaryUnmodeled':True}
        groups=[]
        for part in bb['damageFramesRaw'].split('@'):
            seq=[list(map(int,v.split(':'))) for v in part.split(',') if v]
            assert seq and all(len(v)==4 for v in seq)
            groups.append(seq)
        hits[key]={'unitId':id,'bbId':id,'skillNameSource':f'MST_SKILLS_{id}_NAME',
            'skillTypeRaw':bb['sourceType'],'targetTypeRaw':bb['sourceTargetType'],
            'targetAreaRaw':bb['sourceTargetArea'],'effectFramesRaw':bb['effectFramesRaw'],
            'skillStartFrameRaw':'0','damageFramesRaw':bb['damageFramesRaw'],
            'groups':groups,'groupWeights':[100 for _ in groups],
            'offensiveCandidate':True,'firstGroupHitCount':len(groups[0])}
assert len(units)==len(recipes)==len(power)==len(scopes)==len(hits)==6
mark='/* BF_GLOBAL_FIVE_STAR_STARTERS_V035 */'
if mark in html:
    assert html.count(mark)==1 and all(f'unit_anime_atlas_{id}.png' in html for id in IDS)
    print('PASS existing v0.35 six original Global 5-star forms and sprites unchanged')
else:
    dec=json.JSONDecoder()
    def grow(text,anchor,new,expected):
        assert text.count(anchor)==1,(anchor,text.count(anchor))
        i=text.index(anchor)+len(anchor);old,end=dec.raw_decode(text[i:]);assert len(old)==expected,(anchor,len(old))
        if isinstance(old,list):
            attr='id' if anchor=='window.BF_EVOLVED_UNITS=' else 'evolvedId'
            assert {x[attr] for x in old}.isdisjoint({x[attr] for x in new})
            old.extend(new)
        else:
            assert set(old).isdisjoint(new);old.update(new)
        return text[:i]+json.dumps(old,ensure_ascii=True,separators=(',',':'))+text[i+end:]
    html=grow(html,'window.BF_EVOLVED_UNITS=',units,30)
    html=grow(html,'const EVO_RECIPES=',recipes,30)
    html=grow(html,'window.BF_ARCHIVE_BB_HITS=',hits,48)
    safe=lambda obj:json.dumps(obj,ensure_ascii=True,separators=(',',':')).replace('</','<\\/')
    repl=[
      ('const bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||BF_VERIFIED_BB_V034[String(id)]||null;',
       'const BF_VERIFIED_BB_V035=Object.freeze('+safe(scopes)+');\nconst bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||BF_VERIFIED_BB_V034[String(id)]||BF_VERIFIED_BB_V035[String(id)]||null;'),
      ('const bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||BF_VERIFIED_POWER_V032[String(id)]||BF_VERIFIED_POWER_V033[String(id)]||BF_VERIFIED_POWER_V034[String(id)]||null;',
       'const BF_VERIFIED_POWER_V035=Object.freeze('+safe(power)+');\nconst bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||BF_VERIFIED_POWER_V032[String(id)]||BF_VERIFIED_POWER_V033[String(id)]||BF_VERIFIED_POWER_V034[String(id)]||BF_VERIFIED_POWER_V035[String(id)]||null;'),
      ('const QUEST_DEMO_TIER3_MATERIALS=[10132,20132,30132,40132,50122,60122];',
       'const QUEST_DEMO_TIER3_MATERIALS=[10132,20132,30132,40132,50122,60122];\n// v0.35: higher-tier DEMO quest reward to make archived 5-star recipes attainable.\nconst QUEST_DEMO_TIER4_MATERIALS=[10133,20133,30133,40133,50123,60123];'),
      ("P.materials[mat]=(P.materials[mat]||0)+1;\n E.evoresult.textContent=`Quest reward: +1 demo catalyst ${mat} (original enemy drop tables not recovered).`;",
       "P.materials[mat]=(P.materials[mat]||0)+1;\n const tier4=P.questClears[QUEST.missionId]%12===0?QUEST_DEMO_TIER4_MATERIALS[Math.max(0,missionIdx)%6]:null;\n if(tier4)P.materials[tier4]=(P.materials[tier4]||0)+1;\n E.evoresult.textContent=`Quest reward: +1 demo catalyst ${mat}`+(tier4?` and +1 demo five-star catalyst ${tier4}`:'')+' (original enemy drop tables not recovered).';")
    ]
    for before,after in repl:
        assert html.count(before)==1,('Mismatch',before[:80],html.count(before))
        html=html.replace(before,after,1)
    html=html.replace('const EVO_RECIPES=[',mark+'\nconst EVO_RECIPES=[',1)
    assert html.count(mark)==1
    (A/'index.html').write_text(html,'utf8')
    print('PASS v0.35: six original starter 5-star forms, linked 3rd-stage v7 evolution, original BB scopes, tier4 DEMO catalysts')
