"""v0.34: add 6 original Global 4-star forms using preserved v7 evolution chains.

All source records, raw sprite sheets, animation keyframes and thumbnails are
recovered from the exact original BF1 2022 archives. CGG layer scale is honored
for Black Magress; angle codes remain conservative artwork-renderer metadata,
not a claimed reconstructed native sprite transformation. Strictly offline.

No owned base IDs, save fields, quest states or previous gameplay formulas change.
"""
from __future__ import annotations
import base64, csv, hashlib, io, json, math, re, zipfile
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
DATA=ROOT/'source_data'
SOURCE=DATA/'bf_global_more_second_stage_v034.json'
MAN=json.loads(SOURCE.read_text('utf8'))
EXPECTED={60013,10023,20023,30023,40023,50023}
assert MAN['schema']=='bf-global-more-second-stage-2022-v034'
assert MAN['provenance']['sourceMstSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert set(map(int,MAN['records']))==EXPECTED
sha=lambda b:hashlib.sha256(b).hexdigest()
pack=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_More_Second_Stage.zip.b64').read_text('ascii'))
assert sha(pack)==MAN['sourcePackSha256']
html=(ASSETS/'index.html').read_text('utf8')
assert html.count('/* BF_GLOBAL_SECOND_EVOLUTIONS_V033 */')==1
assert html.count('/* BF_GLOBAL_SIX_EVOLUTIONS_V032 */')==1
assert 'bf_global_offline_demo_v7' in html

def source_records(name):
    regex=r'<script type="application/json" id="'+name+r'">(.*?)</script>'
    obj=re.search(regex,html,re.S)
    assert obj,name
    return {x['id']:x for x in json.loads(obj.group(1))['units']}
source_units=source_records('bf-global-unit-catalog-data')
source_lore=source_records('bf-original-unit-lore-data')

def rows(b):
    return [[int(v) for v in r if v.strip()] for r in csv.reader(io.StringIO(b.decode('utf-8-sig')))]

def bake(z,uid):
    image=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
    assert image.width in (256,480,512) and image.height in (256,480,512)
    sheets=rows(z.read(f'content/unit/cgg/unit_cgg_{uid}.csv'))
    assert 12<=len(sheets)<=30
    fw,fh,columns,anchorx,anchory=480,400,5,220,190
    atlas=Image.new('RGBA',(fw*columns,fh*math.ceil(len(sheets)/columns)),(0,0,0,0))
    scaled=0;nonzero_angles=0
    for fi,record in enumerate(sheets):
        assert record[0]==0 and len(record)==2+11*record[1]
        frame=Image.new('RGBA',(fw,fh),(0,0,0,0))
        for part in range(record[1]):
            dx,dy,orientation,reserved,scale,unused,x,y,w,h,mode=record[2+11*part:2+11*(part+1)]
            assert orientation in (0,1,2) and reserved==unused==mode==0
            assert scale in (30,50,70,100)
            assert min(x,y)>=0 and min(w,h)>0 and x+w<=image.width and y+h<=image.height
            tile=image.crop((x,y,x+w,y+h))
            # BF_GLOBAL_4STAR_VERTICAL_FLIP_SOURCE_V13300: the archived
            # CGG code 2 is a VERTICAL FLIP (community BFFrameAnimator map),
            # not a sprite rotation. These three precise original 4-star
            # profiles have no scale/opacity, blend, rotation or page flags.
            if uid in (20023,30023,50023):
                expected={
                    20023:{(6,2),(7,2),(9,0),(10,0)},
                    30023:{(7,0),(8,0),(9,1),(11,1)},
                    50023:{(9,0),(10,0)}
                }[uid]
                assert scale==100 and orientation in (0,2)
                assert ((fi,part) in expected)==(orientation==2)
                if orientation==2:
                    tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            elif scale!=100:
                # Legacy source fields previously treated as size scaling
                # remain unchanged for other forms awaiting native verification.
                tile=tile.resize((max(1,round(w*scale/100)),max(1,round(h*scale/100))),Image.Resampling.NEAREST)
                scaled+=1
            if orientation:nonzero_angles+=1
            left,top=anchorx+dx,anchory+dy
            assert 0<=left and 0<=top and left+tile.width<=fw and top+tile.height<=fh,(uid,fi,part,left,top,tile.size)
            frame.alpha_composite(tile,(left,top))
        assert frame.getbbox(),(uid,fi)
        atlas.alpha_composite(frame,((fi%columns)*fw,(fi//columns)*fh))
    buf=io.BytesIO();atlas.save(buf,format='PNG',optimize=True)
    sequences={}
    for name in ('idle','atk','move'):
        path=f'content/unit/cgs/unit_{name}_cgs_{uid}.csv'
        if path in z.namelist():sequences[name]=rows(z.read(path))
        else:
            assert name=='move';sequences[name]=list(sequences['idle'])
        assert sequences[name] and all(len(v)==4 and 0<=v[0]<len(sheets) and v[3]>0 for v in sequences[name])
    return buf.getvalue(),sequences,len(sheets),scaled,nonzero_angles

new_units=[];new_recipes=[];scopes={};powers={};supports={};bb_hits={}
with zipfile.ZipFile(io.BytesIO(pack)) as z:
    for key,info in MAN['records'].items():
        uid=int(key)
        source=source_units[uid];from_id=info['fromId'];base=info['ownedBaseId']
        assert uid==from_id+1 and uid in EXPECTED
        assert source['name']==info['name'] and source['nameSource']=='2022_Global_English'
        assert source['element']==info['element'] and source['rarity']==info['rarity']==4
        assert {k:source['unitBase'+k.title()] for k in ('hp','atk','def','rec')}==info['stats']
        assert {k:source['unitLord'+k.title()] for k in ('hp','atk','def','rec')}==info['lordStats']
        assert (source['unitMaxLevel'],source['unitCost'])==(info['originalMaxLevel'],info['originalUnitCost'])
        prev=source_lore[from_id]['recipes']
        assert len(prev)==1 and prev[0]['target']==uid
        assert (prev[0]['zel'],prev[0]['karma'])==(info['sourceRecipe']['zel'],info['sourceRecipe']['karma'])
        materials={}
        for mat in prev[0]['materials']:
            assert mat['type']==1
            material=str(mat['id']);materials[material]=materials.get(material,0)+1
        assert materials==info['sourceRecipe']['materials']
        assert source_lore[uid]['bb']['name']==info['bb']['name'] and source_lore[uid]['bb']['description']==info['bb']['description']
        for name,digest in info['sourceFilesSha256'].items():
            assert sha(z.read(name))==digest,(uid,name)
        img,anims,frames,scaled,angles=bake(z,uid)
        assert frames==info['frameCount']
        assert sum(x['scalePct']!=100 for x in info['spriteTransformNotes']['nonDefaultLayers'])==scaled,(uid,scaled)
        assert sum(x['angleCode']!=0 for x in info['spriteTransformNotes']['nonDefaultLayers'])==angles,(uid,angles)
        paths=[(f'unit_anime_atlas_{uid}.png',img),
               (f'unit_ills_thum_{uid}.png',z.read(f'content/unit/img/unit_ills_thum_{uid}.png'))]
        for name,data in paths:
            target=ASSETS/'content/more_second_evolution'/name
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.is_file():assert target.read_bytes()==data,(uid,'unexpected changed sprite',name)
            else:target.write_bytes(data)
        elt=['','Fire','Water','Earth','Thunder','Light','Dark'][info['element']]
        new_units.append({'id':uid,'name':info['name'],'element':elt,'rarity':4,
            'stats':info['stats'],'animation':anims,
            'atlas':f'content/more_second_evolution/unit_anime_atlas_{uid}.png',
            'portrait':f'content/more_second_evolution/unit_ills_thum_{uid}.png',
            'frameWidth':480,'frameHeight':400,'columns':5,'frameCount':frames,'scale':0.5,
            'anchorX':220,'anchorY':190,
            'originalMaxLevel':info['originalMaxLevel'],'originalUnitCost':info['originalUnitCost'],
            'originalLordStats':info['lordStats']})
        new_recipes.append({'baseId':base,'fromId':from_id,'evolvedId':uid,
            'sourceRarity':3,'targetRarity':4,'archivedZel':info['sourceRecipe']['zel'],
            'demoZel':5000,'materials':materials,'targetStats':info['stats'],'frameCount':frames,
            'animationNote':'Original 2022 CGG/CGS layer sequence; scale approximated with nearest pixel rendering, orientation code not yet decoded'})
        skill=info['bb']
        target=skill['target']
        assert target in ('all_enemies','single_enemy','support')
        scopes[key]={'name':skill['name'],'target':target,'skillId':uid}
        lv=skill['levelPower'];assert len(lv)==10
        if target=='support':
            assert key=='40023' and lv[0]==50
            supports[key]={'name':skill['name'],'kind':'atk_buff_all','pct':50,'rounds':3}
        else:
            powers[key]={'name':skill['name'],'target':target,'base':lv[0],
                         'levels':lv,'secondaryUnmodeled':skill['secondaryUnmodeled']}
        groups=[]
        for group in skill['damageFramesRaw'].split('@'):
            frameset=[list(map(int,x.split(':'))) for x in group.split(',') if x]
            assert frameset and all(len(r)==4 for r in frameset)
            groups.append(frameset)
        bb_hits[key]={'unitId':uid,'bbId':uid,'skillNameSource':f'MST_SKILLS_{uid}_NAME',
            'skillTypeRaw':skill['sourceType'],'targetTypeRaw':skill['sourceTargetType'],
            'targetAreaRaw':skill['sourceTargetArea'],'effectFramesRaw':skill['effectFramesRaw'],
            'skillStartFrameRaw':'0','damageFramesRaw':skill['damageFramesRaw'],
            'groups':groups,'groupWeights':[100 for _ in groups],
            'offensiveCandidate':target!='support','firstGroupHitCount':len(groups[0])}
assert len(new_units)==len(new_recipes)==len(scopes)==len(bb_hits)==6
assert len(powers)==5 and len(supports)==1
mark='/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */'
if mark in html:
    assert html.count(mark)==1
    assert all(f'unit_anime_atlas_{id}.png' in html for id in EXPECTED)
    print('PASS v0.34 already staged (idempotent)')
else:
    dec=json.JSONDecoder()
    def extend(text,anchor,items,expect):
        assert text.count(anchor)==1,(anchor,text.count(anchor))
        pos=text.index(anchor)+len(anchor)
        current,width=dec.raw_decode(text[pos:])
        assert len(current)==expect,(anchor,len(current),expect)
        if isinstance(current,list):
            unique='id' if anchor=='window.BF_EVOLVED_UNITS=' else 'evolvedId'
            assert {r[unique] for r in current}.isdisjoint({r[unique] for r in items})
            current.extend(items)
        else:
            assert set(current).isdisjoint(set(items))
            current.update(items)
        return text[:pos]+json.dumps(current,ensure_ascii=True,separators=(',',':'))+text[pos+width:]
    html=extend(html,'window.BF_EVOLVED_UNITS=',new_units,24)
    html=extend(html,'const EVO_RECIPES=',new_recipes,24)
    html=extend(html,'window.BF_ARCHIVE_BB_HITS=',bb_hits,42)
    safe=lambda d:json.dumps(d,ensure_ascii=True,separators=(',',':')).replace('</','<\\/')
    substitutions=[
      ('const bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||null;',
       'const BF_VERIFIED_BB_V034=Object.freeze('+safe(scopes)+');\nconst bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||BF_VERIFIED_BB_V034[String(id)]||null;'),
      ('function originalSupport(id){return BF_VERIFIED_BB_SUPPORT[String(id)]||BF_VERIFIED_SUPPORT_V032[String(id)]||null;}',
       'const BF_VERIFIED_SUPPORT_V034=Object.freeze('+safe(supports)+');\nfunction originalSupport(id){return BF_VERIFIED_BB_SUPPORT[String(id)]||BF_VERIFIED_SUPPORT_V032[String(id)]||BF_VERIFIED_SUPPORT_V034[String(id)]||null;}'),
      ('const bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||BF_VERIFIED_POWER_V032[String(id)]||BF_VERIFIED_POWER_V033[String(id)]||null;',
       'const BF_VERIFIED_POWER_V034=Object.freeze('+safe(powers)+');\nconst bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||BF_VERIFIED_POWER_V032[String(id)]||BF_VERIFIED_POWER_V033[String(id)]||BF_VERIFIED_POWER_V034[String(id)]||null;')]
    for a,b in substitutions:
        assert html.count(a)==1,(a[:80],html.count(a))
        html=html.replace(a,b,1)
    assert html.count('const EVO_RECIPES=')==1
    html=html.replace('const EVO_RECIPES=[',mark+'\nconst EVO_RECIPES=[',1)
    assert html.count(mark)==1
    (ASSETS/'index.html').write_text(html,'utf8')
    print('PASS v0.34 six original second-stage forms; source animations, BB types, and chained save-v7 evolutions')
