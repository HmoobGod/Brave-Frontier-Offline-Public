"""Build 6 real BF Global evolution sprites and append original data to demo.

Source: immutable and hash-verified BF1 original unit PNG/CGG/CGS archive slice
plus original 2022 translated MST + English codex. Demo evolution economy stays
separate. Existing playable identities, v7 save fields and owned rosters untouched.
Idempotent; refuses mismatched source or unexpected gameplay anchors.
"""
from __future__ import annotations
import base64,csv,gzip,hashlib,io,json,math,zipfile
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
DATA=ROOT/'source_data'
manifest=json.loads((DATA/'bf_global_six_evolutions_v032.json').read_text('utf-8'))
assert manifest['schema']=='bf-global-six-first-evolutions-2022-v032'
assert manifest['provenance']['sourceMstSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
sha=lambda b:hashlib.sha256(b).hexdigest()
pack=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Extra_Evolutions.zip.b64').read_text('ascii'))
assert sha(pack)==manifest['sourcePackSha256']
with zipfile.ZipFile(io.BytesIO(pack)) as raw:
  for uid,row in manifest['records'].items():
    for path,digest in row['sourceFilesSha256'].items():assert sha(raw.read(path))==digest,(uid,path)

# Independently compare the original unit and lore records already committed in
# v0.26/0.27 (not user-editable runtime data).
base_catalog=gzip.decompress(base64.b64decode((DATA/'bf_global_original_unit_catalog.json.gz.b64').read_text('ascii')))
meta=json.loads((DATA/'bf_global_original_unit_catalog_meta.json').read_text('utf-8'))
assert sha(base_catalog)==meta['catalogJsonSha256']
units={u['id']:u for u in json.loads(base_catalog)['units']}
base_lore=gzip.decompress(base64.b64decode((DATA/'bf_global_original_lore_codex.json.gz.b64').read_text('ascii')))
loremeta=json.loads((DATA/'bf_global_original_lore_meta.json').read_text('utf-8'))
assert sha(base_lore)==loremeta['payloadJsonSha256']
lore={u['id']:u for u in json.loads(base_lore)['units']}
assert len(manifest['records'])==6
expected_ids={10042,20042,30042,40042,50042,60042}
assert set(map(int,manifest['records']))==expected_ids

# The existing Global source atlas for 10012 reproduces pixel-identically by
# layering the original CGG rects at (anchorX + dx, anchorY + dy). All new
# six original CGG rows have no unsupported rotation/flip/scale modes.
def parse_rows(raw):
    return [[int(v) for v in record if v.strip()] for record in csv.reader(io.StringIO(raw.decode('utf-8-sig')))]
def cgs(raw):
    rows=parse_rows(raw)
    assert rows and all(len(v)==4 and v[3]>0 for v in rows)
    return rows

def bake(raw,uid):
    src=Image.open(io.BytesIO(raw.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
    assert src.size==(512,512)
    lines=parse_rows(raw.read(f'content/unit/cgg/unit_cgg_{uid}.csv'))
    assert lines and len(lines)<=25
    framew,frameh,columns,anchorx,anchory=480,400,5,220,190
    rows=math.ceil(len(lines)/columns)
    atlas=Image.new('RGBA',(framew*columns,frameh*rows),(0,0,0,0))
    for fi,row in enumerate(lines):
        assert row[0]==0 and len(row)==2+11*row[1],(uid,fi)
        frame=Image.new('RGBA',(framew,frameh),(0,0,0,0))
        for layer in range(row[1]):
            dx,dy,orientation,unknown,scale,other,sx,sy,w,h,mode=row[2+11*layer:2+11*(layer+1)]
            # Existing atlas baker treats the reserved orientation field as
            # optional effect metadata (no geometric flip); all original
            # transforms here remain at 100%, 0 mode, and 0 offsets.
            assert orientation in (0,1) and unknown==0 and scale==100 and other==0 and mode==0,(uid,fi,layer)
            assert w>0 and h>0 and sx>=0 and sy>=0 and sx+w<=src.width and sy+h<=src.height
            piece=src.crop((sx,sy,sx+w,sy+h))
            assert 0<=anchorx+dx<framew and 0<=anchory+dy<frameh
            frame.alpha_composite(piece,(anchorx+dx,anchory+dy))
        assert frame.getbbox(),(uid,fi,'empty source frame')
        atlas.alpha_composite(frame,((fi%columns)*framew,(fi//columns)*frameh))
    output=io.BytesIO();atlas.save(output,format='PNG',optimize=True)
    idle=cgs(raw.read(f'content/unit/cgs/unit_idle_cgs_{uid}.csv'))
    attack=cgs(raw.read(f'content/unit/cgs/unit_atk_cgs_{uid}.csv'))
    path=f'content/unit/cgs/unit_move_cgs_{uid}.csv'
    move=cgs(raw.read(path)) if path in raw.namelist() else list(idle)
    assert all(0<=entry[0]<len(lines) for seq in (idle,attack,move) for entry in seq)
    return output.getvalue(),dict(idle=idle,atk=attack,move=move),len(lines)

# Build precise source-derived new unit configurations and six evolution links.
new_units=[];new_recipes=[];new_bb_meta={};new_scopes={};new_support={};new_power={}
with zipfile.ZipFile(io.BytesIO(pack)) as raw:
    for key,item in manifest['records'].items():
        uid=int(key);old=uid-1;origin=units[uid];before=units[old]
        assert origin['name']==item['name'] and origin['rarity']==item['rarity']
        assert origin['unitMaxLevel']==item['originalMaxLevel'] and origin['unitCost']==item['originalUnitCost']
        assert item['stats']=={k:origin['unitBase'+k.title()] for k in ('hp','atk','def','rec')}
        assert item['originalLordStats']=={k:origin['unitLord'+k.title()] for k in ('hp','atk','def','rec')}
        recipes=lore[old]['recipes'];assert len(recipes)==1 and recipes[0]['target']==uid
        assert recipes[0]['zel']==item['sourceRecipe']['zel'] and recipes[0]['karma']==item['sourceRecipe']['karma']
        mats={}
        for mat in recipes[0]['materials']:
            assert mat['type']==1
            mk=str(mat['id']);mats[mk]=mats.get(mk,0)+1
        assert mats==item['sourceRecipe']['materials']
        assert lore[uid]['bb']['name']==item['bb']['name'] and lore[uid]['bb']['description']==item['bb']['description']
        img,animation,count=bake(raw,uid)
        assert count==item['frameCount']
        portrait=raw.read(f'content/unit/img/unit_ills_thum_{uid}.png')
        assert portrait.startswith(b'\x89PNG\r\n\x1a\n')
        target=ASSETS/f'content/extra_evolution/unit_anime_atlas_{uid}.png'
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==img,(uid,'asset changed unexpectedly')
        else:target.write_bytes(img)
        target=ASSETS/f'content/extra_evolution/unit_ills_thum_{uid}.png'
        if target.exists():assert target.read_bytes()==portrait,(uid,'portrait changed unexpectedly')
        else:target.write_bytes(portrait)
        new_units.append({'id':uid,'name':item['name'],'element':item['element'],'rarity':item['rarity'],
           'stats':item['stats'],'animation':animation,'atlas':f'content/extra_evolution/unit_anime_atlas_{uid}.png',
           'portrait':f'content/extra_evolution/unit_ills_thum_{uid}.png',
           'frameWidth':480,'frameHeight':400,'columns':5,'frameCount':count,'scale':0.5,
           'anchorX':220,'anchorY':190,'originalMaxLevel':item['originalMaxLevel'],'originalUnitCost':item['originalUnitCost'],
           'originalLordStats':item['originalLordStats']})
        new_recipes.append({'baseId':old,'evolvedId':uid,'sourceRarity':before['rarity'],
           'targetRarity':origin['rarity'],'archivedZel':recipes[0]['zel'],'demoZel':2500,
           'materials':mats,'targetStats':item['stats'],'frameCount':count,
           'animationNote':'Original CGG/CGS and PNG verified; missing original move sequence uses idle frames when needed'})
        skill=item['bb'];scope=skill['target'];new_scopes[key]={'name':skill['name'],'target':scope,'skillId':uid}
        rawgroups=skill['damageFramesRaw'].split('@')
        groups=[]
        for group in rawgroups:
            vals=[list(map(int,x.split(':'))) for x in group.split(',') if x]
            assert vals and all(len(v)==4 for v in vals)
            groups.append(vals)
        new_bb_meta[key]={'unitId':uid,'bbId':uid,'skillNameSource':f'MST_SKILLS_{uid}_NAME',
            'skillTypeRaw':skill['sourceType'],'targetTypeRaw':skill['sourceTargetType'],
            'targetAreaRaw':skill['sourceTargetArea'],'effectFramesRaw':skill['effectFramesRaw'],
            'skillStartFrameRaw':'0','damageFramesRaw':skill['damageFramesRaw'],
            'groups':groups,'groupWeights':[100 for _ in groups],
            'offensiveCandidate':scope!='support','firstGroupHitCount':len(groups[0])}
        first=skill['levelInfo'].split('|')[0].split('@')[0]
        level,code,p=first.split(':');assert int(level)==1 and int(code)==1500
        values=list(map(int,p.split(',')))
        if scope=='support':
            assert values==[1000,1200,50,50]
            new_support[key]={'name':skill['name'],'kind':'heal_all','low':1000,'high':1200}
        else:
            assert values[0] in (60,70)
            levels=[]
            for seg in skill['levelInfo'].split('|'):
                level_info=seg.split('@')[0];lv,c,p=level_info.split(':');assert int(lv)==len(levels)+1 and int(c)==1500
                levels.append(int(p.split(',')[0]))
            assert len(levels)==10
            new_power[key]={'name':skill['name'],'target':scope,'base':values[0],
                            'levels':levels,'secondaryUnmodeled':'@' in skill['levelInfo']}
assert len(new_units)==len(new_recipes)==len(new_scopes)==len(new_bb_meta)==6
assert len(new_support)==4 and len(new_power)==2

# Patch the pre-existing bundled HTML in place only after the prior v0.31
# source validations have run. This is the same established architecture used
# by the legacy demo (data in an offline HTML file, not a server).
index=ASSETS/'index.html'
html=index.read_text('utf-8')
assert html.count('/* BF_GLOBAL_BB_POWER_V030 */')==1
assert html.count('const BF_ORIGINAL_PLAYABLE_IDENTITY=')==1
assert html.count('bf_global_offline_demo_v7')>=1
marker='/* BF_GLOBAL_SIX_EVOLUTIONS_V032 */'
if marker in html:
    assert html.count(marker)==1
    assert all(f'unit_anime_atlas_{uid}.png' in html for uid in expected_ids)
    print('PASS v0.32 original Global six evolutions already staged; no changes.')
else:
    dec=json.JSONDecoder()
    def grow_json(text,anchor,addition,expected):
        assert text.count(anchor)==1,(anchor,text.count(anchor))
        at=text.index(anchor)+len(anchor)
        existing,used=dec.raw_decode(text[at:])
        assert len(existing)==expected,(anchor,len(existing))
        if isinstance(existing,list):
            assert not {x['id'] for x in addition}&{x['id'] for x in existing} if anchor=='window.BF_EVOLVED_UNITS=' else not {x['baseId'] for x in addition}&{x['baseId'] for x in existing}
            updated=existing+addition
        else:
            assert set(existing).isdisjoint(addition)
            updated=dict(existing,**addition)
        return text[:at]+json.dumps(updated,ensure_ascii=True,separators=(',',':'))+text[at+used:]
    # Insert before mapping is built, so new forms work on load and on old v7 saves.
    html=grow_json(html,'window.BF_EVOLVED_UNITS=',new_units,12)
    html=grow_json(html,'const EVO_RECIPES=',new_recipes,12)
    html=grow_json(html,'window.BF_ARCHIVE_BB_HITS=',new_bb_meta,30)
    safe=lambda d:json.dumps(d,ensure_ascii=True,separators=(',',':')).replace('</','<\\/')
    before='const bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||null;'
    after='const BF_VERIFIED_BB_V032=Object.freeze('+safe(new_scopes)+');\nconst bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||null;'
    assert html.count(before)==1
    html=html.replace(before,after,1)
    before='function originalSupport(id){return BF_VERIFIED_BB_SUPPORT[String(id)]||null;}'
    after='const BF_VERIFIED_SUPPORT_V032=Object.freeze('+safe(new_support)+');\nfunction originalSupport(id){return BF_VERIFIED_BB_SUPPORT[String(id)]||BF_VERIFIED_SUPPORT_V032[String(id)]||null;}'
    assert html.count(before)==1
    html=html.replace(before,after,1)
    before='const bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||null;'
    after='const BF_VERIFIED_POWER_V032=Object.freeze('+safe(new_power)+');\nconst bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||BF_VERIFIED_POWER_V032[String(id)]||null;'
    assert html.count(before)==1
    html=html.replace(before,after,1)
    # The v0.31 identity baseline legitimately covers only 30 older forms.
    # New units carry hash-checked original identity fields in their configs.
    before="if(!identity)throw Error('Missing original unit identity: '+unit.id);"
    after="if(!identity){if(unit.originalMaxLevel&&unit.originalUnitCost&&unit.originalLordStats)continue;throw Error('Missing original unit identity: '+unit.id);}"
    assert html.count(before)==1
    html=html.replace(before,after,1)
    # Protect the existing original-effect visualizer against negative radii
    # when rapid BB event clocks briefly differ (no gameplay stat changes).
    before='ctx.arc(fx.x,fx.y,10+t*26,0,Math.PI*2)'
    after='ctx.arc(fx.x,fx.y,Math.max(0,10+t*26),0,Math.PI*2)'
    assert html.count(before)==1
    html=html.replace(before,after,1)
    before="const EVO_RECIPES=["
    assert html.count(before)==1
    html=html.replace(before,marker+'\n'+before,1)
    index.write_text(html,'utf-8')
    print('PASS v0.32: added 6 original Global playable evolved sprites, matching source BB effects and accurate source recipes. Demo economy / save v7 retained.')
