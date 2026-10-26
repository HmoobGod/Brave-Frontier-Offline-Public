"""v0.33: six original 4-star second-stage evolutions, CGG/CGS battle art.

Playability requires no new save field: P.evolutions[owned base ID] retains the
latest original form ID. The existing original 30 + v0.32 six records stay
unchanged. Actual 2022 recipe costs and source level data remain reference;
quest catalyst awards, Lv2 requirement and evolution payment are DEMO.
"""
from __future__ import annotations
import base64,hashlib,io,json,math,csv,zipfile
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
DATA=ROOT/'source_data'
MAN=json.loads((DATA/'bf_global_second_stage_evolutions_v033.json').read_text('utf8'))
assert MAN['schema']=='bf-global-second-stage-evolutions-2022-v033'
assert MAN['provenance']['sourceMstSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
EXPECTED={10013,20013,30013,40013,50013,60023}
assert {int(i) for i in MAN['records']}==EXPECTED
sha=lambda b:hashlib.sha256(b).hexdigest()
pack=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Second_Stage_Evolutions.zip.b64').read_text('ascii'))
assert sha(pack)==MAN['sourcePackSha256']

def parse(data):return [[int(v) for v in r if v.strip()] for r in csv.reader(io.StringIO(data.decode('utf-8-sig')))]

def bake(z,uid):
    image=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
    assert image.size in ((512,512),(256,256))
    frames=parse(z.read(f'content/unit/cgg/unit_cgg_{uid}.csv'))
    assert len(frames)>8
    w,h,columns,x0,y0=480,400,5,220,190
    atlas=Image.new('RGBA',(w*columns,h*math.ceil(len(frames)/columns)),(0,0,0,0))
    for fi,row in enumerate(frames):
        assert row[0]==0 and len(row)==2+11*row[1]
        frame=Image.new('RGBA',(w,h),(0,0,0,0))
        for n in range(row[1]):
            dx,dy,orientation,reserved,scale,unused,sx,sy,bw,bh,mode=row[2+11*n:2+11*(n+1)]
            # Decline all unknown CGG transformations. The six selected 4-star
            # unit art files all use untransformed original layers.
            assert (orientation,reserved,scale,unused,mode)==(0,0,100,0,0),(uid,fi,n)
            assert 0<=sx and 0<=sy and 0<bw and 0<bh and sx+bw<=image.width and sy+bh<=image.height
            dest=(x0+dx,y0+dy)
            assert dest[0]>=0 and dest[1]>=0 and dest[0]+bw<=w and dest[1]+bh<=h
            frame.alpha_composite(image.crop((sx,sy,sx+bw,sy+bh)),dest)
        assert frame.getbbox(),(uid,fi,'empty source frame')
        atlas.alpha_composite(frame,((fi%columns)*w,(fi//columns)*h))
    buf=io.BytesIO();atlas.save(buf,format='PNG',optimize=True)
    names={f'content/unit/cgs/unit_{seq}_cgs_{uid}.csv' for seq in ('idle','atk','move')}
    assert names.issubset(z.namelist())
    animation={seq:parse(z.read(f'content/unit/cgs/unit_{seq}_cgs_{uid}.csv')) for seq in ('idle','atk','move')}
    assert all(seq and all(len(frame)==4 and 0<=frame[0]<len(frames) for frame in seq) for seq in animation.values())
    return buf.getvalue(),animation,len(frames)

# Crosscheck the existing original Global decoded catalogue against this small
# verified, immutable source-asset slice. Do not introduce fabricated stats.
import gzip
catalog=gzip.decompress(base64.b64decode((DATA/'bf_global_original_unit_catalog.json.gz.b64').read_text('ascii')))
meta=json.loads((DATA/'bf_global_original_unit_catalog_meta.json').read_text('utf8'))
assert sha(catalog)==meta['catalogJsonSha256']
source_units={u['id']:u for u in json.loads(catalog)['units']}
lore_bytes=gzip.decompress(base64.b64decode((DATA/'bf_global_original_lore_codex.json.gz.b64').read_text('ascii')))
lore_meta=json.loads((DATA/'bf_global_original_lore_meta.json').read_text('utf8'))
assert sha(lore_bytes)==lore_meta['payloadJsonSha256']
source_lore={u['id']:u for u in json.loads(lore_bytes)['units']}

units=[];recipes=[];scopes={};powers={};hit_profiles={}
with zipfile.ZipFile(io.BytesIO(pack)) as z:
    assert len(z.namelist())==6*6
    for key,item in MAN['records'].items():
        uid=int(key);existing=source_units[uid]
        assert existing['name']==item['name'] and existing['element']==item['element'] and existing['rarity']==item['rarity']==4
        assert {k:existing['unitBase'+k.title()] for k in ('hp','atk','def','rec')}==item['stats']
        assert {k:existing['unitLord'+k.title()] for k in ('hp','atk','def','rec')}==item['originalLordStats']
        assert existing['unitCost']==item['originalUnitCost'] and existing['unitMaxLevel']==item['originalMaxLevel']
        origin=source_lore[item['fromId']]['recipes']
        assert len(origin)==1 and origin[0]['target']==uid
        assert origin[0]['zel']==item['sourceRecipe']['zel'] and origin[0]['karma']==item['sourceRecipe']['karma']
        mats={}
        for m in origin[0]['materials']:
            assert m['type']==1
            mat=str(m['id']);mats[mat]=mats.get(mat,0)+1
        assert mats==item['sourceRecipe']['materials']
        assert source_lore[uid]['bb']['name']==item['bb']['name']
        assert source_lore[uid]['bb']['description']==item['bb']['description']
        for p,digest in item['sourceFilesSha256'].items():assert sha(z.read(p))==digest,(uid,p)
        atlas,anims,num=bake(z,uid)
        assert num==item['frameCount']
        for file,data in [(f'unit_anime_atlas_{uid}.png',atlas),(f'unit_ills_thum_{uid}.png',z.read(f'content/unit/img/unit_ills_thum_{uid}.png'))]:
            target=ASSETS/'content/second_evolution'/file
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():assert target.read_bytes()==data,'Source art conflict '+file
            else:target.write_bytes(data)
        units.append({'id':uid,'name':item['name'],'element':['','Fire','Water','Earth','Thunder','Light','Dark'][item['element']],
            'rarity':item['rarity'],'stats':item['stats'],'animation':anims,
            'atlas':f'content/second_evolution/unit_anime_atlas_{uid}.png',
            'portrait':f'content/second_evolution/unit_ills_thum_{uid}.png',
            'frameWidth':480,'frameHeight':400,'columns':5,'frameCount':num,'scale':0.5,'anchorX':220,'anchorY':190,
            'originalMaxLevel':item['originalMaxLevel'],'originalUnitCost':item['originalUnitCost'],'originalLordStats':item['originalLordStats']})
        recipes.append({'baseId':item['ownedBaseId'],'fromId':item['fromId'],'evolvedId':uid,
            'sourceRarity':3,'targetRarity':4,'archivedZel':item['sourceRecipe']['zel'],
            'demoZel':5000,'materials':mats,'targetStats':item['stats'],'frameCount':num,
            'animationNote':'Original 2022 CGG/CGS verified; second-stage demo payment distinct from archive'})
        bb=item['bb']
        scopes[key]={'name':bb['name'],'target':'all_enemies','skillId':uid}
        levels=bb['levelPower']
        assert len(levels)==10 and all(0<=v<=400 for v in levels)
        powers[key]={'name':bb['name'],'target':'all_enemies','base':levels[0], 'levels':levels,
            'secondaryUnmodeled':'@' in bb['levelInfo'] or bb['effectCode']!=1500}
        groups=[]
        for group in bb['damageFramesRaw'].split('@'):
            events=[list(map(int,part.split(':'))) for part in group.split(',') if part]
            assert all(len(e)==4 for e in events)
            groups.append(events)
        hit_profiles[key]={'unitId':uid,'bbId':uid,'skillNameSource':f'MST_SKILLS_{uid}_NAME',
            'skillTypeRaw':bb['sourceType'],'targetTypeRaw':bb['sourceTargetType'],
            'targetAreaRaw':bb['sourceTargetArea'],'effectFramesRaw':bb['effectFramesRaw'],
            'skillStartFrameRaw':'0','damageFramesRaw':bb['damageFramesRaw'],'groups':groups,
            'groupWeights':[100 for _ in groups],'offensiveCandidate':True,'firstGroupHitCount':len(groups[0])}
assert len(units)==len(recipes)==len(powers)==len(hit_profiles)==6

index=ASSETS/'index.html';s=index.read_text('utf8');mark='/* BF_GLOBAL_SECOND_EVOLUTIONS_V033 */'
assert s.count('/* BF_GLOBAL_SIX_EVOLUTIONS_V032 */')==1
assert s.count('/* BF_GLOBAL_BB_POWER_V030 */')==1
if mark in s:
    assert s.count(mark)==1 and all(f'unit_anime_atlas_{uid}.png' in s for uid in EXPECTED)
    print('PASS v0.33 existing second-stage evolution patch and original artwork verified')
else:
    dec=json.JSONDecoder()
    def grow(anchor,addition,count):
        global s
        assert s.count(anchor)==1,(anchor,s.count(anchor))
        ix=s.index(anchor)+len(anchor);obj,sz=dec.raw_decode(s[ix:]);assert len(obj)==count,(anchor,len(obj),count)
        if isinstance(obj,list):
            assert {d['id'] for d in obj}.isdisjoint({d['id'] for d in addition}) if anchor=='window.BF_EVOLVED_UNITS=' else not {d['evolvedId'] for d in obj}&{d['evolvedId'] for d in addition}
            obj.extend(addition)
        else:
            assert not set(obj)&set(addition)
            obj.update(addition)
        s=s[:ix]+json.dumps(obj,ensure_ascii=True,separators=(',',':'))+s[ix+sz:]
    grow('window.BF_EVOLVED_UNITS=',units,18)
    grow('const EVO_RECIPES=',recipes,18)
    grow('window.BF_ARCHIVE_BB_HITS=',hit_profiles,36)
    safe=lambda d:json.dumps(d,ensure_ascii=True,separators=(',',':'))
    replacements=[
      ('while payable Zel is capped at 2,500 in this demo.',
       'with first evolutions priced at 2,500 demo Zel and eligible second-stage evolutions at 5,000 demo Zel.'),
      ('const bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||null;',
        'const BF_VERIFIED_BB_V033=Object.freeze('+safe(scopes)+');\nconst bfOriginalBB=id=>BF_VERIFIED_BB_SCOPES[String(id)]||BF_VERIFIED_BB_V032[String(id)]||BF_VERIFIED_BB_V033[String(id)]||null;'),
      ('const bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||BF_VERIFIED_POWER_V032[String(id)]||null;',
        'const BF_VERIFIED_POWER_V033=Object.freeze('+safe(powers)+');\nconst bfOriginalBBPower=id=>BF_ORIGINAL_BB_POWER[String(id)]||BF_VERIFIED_POWER_V032[String(id)]||BF_VERIFIED_POWER_V033[String(id)]||null;'),
      ('const EVO_BY_BASE=new Map(EVO_RECIPES.map(r=>[r.baseId,r]));',
       'const EVO_BY_BASE=new Map(EVO_RECIPES.filter(r=>!r.fromId).map(r=>[r.baseId,r]));'),
      ("const recipe=EVO_BY_BASE.get(Number(bid));\n   if(!recipe || recipe.evolvedId!==value || !out.roster.includes(Number(bid)))throw new Error('Unknown evolution');",
       "const recipe=EVO_RECIPES.find(r=>r.baseId===Number(bid) && r.evolvedId===value);\n   if(!recipe || !out.roster.includes(Number(bid)))throw new Error('Unknown evolution');"),
      ("if(filter==='evolve'&&!!P.evolutions[base.id])return false;",
       "if(filter==='evolve'&&!EVO_RECIPES.some(r=>r.baseId===base.id&&(r.fromId||r.baseId)===effectiveUnit(base.id).id))return false;"),
      ("const needed=new Set(EVO_RECIPES.filter(r=>P.roster.includes(r.baseId)&&!P.evolutions[r.baseId]).flatMap(r=>Object.keys(r.materials)));",
       "const needed=new Set(EVO_RECIPES.filter(r=>P.roster.includes(r.baseId)&&(r.fromId||r.baseId)===effectiveUnit(r.baseId).id).flatMap(r=>Object.keys(r.materials)));"),
      ("const QUEST_DEMO_MATERIALS=[[10130,10131],[20130,20131],[30130,30131],[40130,40131],[50120,50121],[60120,60121]];",
       "const QUEST_DEMO_MATERIALS=[[10130,10131],[20130,20131],[30130,30131],[40130,40131],[50120,50121],[60120,60121]];\n// A source recipe is authentic; this guaranteed catalyst schedule is DEMO.\nconst QUEST_DEMO_TIER3_MATERIALS=[10132,20132,30132,40132,50122,60122];"),
      ("const mat=choices[P.questClears[QUEST.missionId]%3===0?1:0];",
       "const mat=P.questClears[QUEST.missionId]%6===0?QUEST_DEMO_TIER3_MATERIALS[Math.max(0,missionIdx)%6]:choices[P.questClears[QUEST.missionId]%3===0?1:0];")
    ]
    for before,after in replacements:
        assert s.count(before)==1,('Unsafe v0.33 patch anchor',before[:120],s.count(before))
        s=s.replace(before,after,1)
    start=s.index('function renderEvolutionPanel(){');end=s.index('function renderSummonPanel(){',start)
    old=s[start:end]
    assert old.count('P.evolutions[r.baseId]')==3
    # Preserve one card per owned base unit. Show its *current next step* in
    # an original chain, or completed status when the owned form has no next.
    new='''function renderEvolutionPanel(){
 if(!E?.evolist||!P)return;
 E.evolist.replaceChildren();
 const owned=STARTERS.filter(u=>P.roster.includes(u.id));
 const inv=ALL_MATERIAL_IDS.filter(id=>(P.materials[id]||0)>0).map(id=>`${id} ×${P.materials[id]}`).join(' · ');
 E.evoinventory.textContent='Demo catalysts: '+(inv||'none yet')+' · Archived material IDs shown';
 for(const ownedBase of owned){
  const baseId=ownedBase.id,current=effectiveUnit(baseId);
  const sequence=EVO_RECIPES.filter(r=>r.baseId===baseId);
  const r=sequence.find(r=>(r.fromId||r.baseId)===current.id)||sequence[sequence.length-1];
  if(!r)continue;
  const next=UNIT_BY_ID.get(r.evolvedId),finished=(r.fromId||r.baseId)!==current.id;
  const level=demoLevel(P.unitExp[baseId]);
  const matList=Object.entries(r.materials).map(([id,n])=>`Catalyst ${id}: ${P.materials[id]||0}/${n}`);
  const hasMats=Object.entries(r.materials).every(([id,n])=>(P.materials[id]||0)>=n);
  const ready=!finished && level>=2 && hasMats && P.zel>=r.demoZel;
  const card=document.createElement('div');card.className='evocard';
  const thumbnail=document.createElement('img');thumbnail.src=current.portrait;thumbnail.alt='';
  const info=document.createElement('div');info.className='evoinfo';
  const heading=document.createElement('strong');heading.textContent=`${current.name} · ★${current.rarity} · Lv.${level}`;
  const sub=document.createElement('small');sub.textContent=finished?`Evolved to Unit ${current.id} · archived form`:`→ Unit ${next.id} ★${next.rarity} · HP ${next.stats.hp} ATK ${next.stats.atk} DEF ${next.stats.def} REC ${next.stats.rec}`;
  const req=document.createElement('small');req.textContent=finished?'Completed':`Lv.2 demo minimum · ${r.demoZel.toLocaleString()} demo Zel (archive: ${r.archivedZel.toLocaleString()}) · ${matList.join(' · ')}`;
  info.append(heading,sub,req);
  const button=document.createElement('button');button.type='button';button.className='evoaction';button.disabled=finished||!!S?.busy||!ready;
  button.textContent=finished?'Evolved':ready?'Evolve':'Need materials / Zel / level';
  button.onclick=()=>{
   // Verify the actual current form, not merely the presence of an earlier
   // evolution; this allows a second tier without changing the v7 schema.
   if(S?.busy||effectiveUnit(baseId).id!==(r.fromId||r.baseId)||demoLevel(P.unitExp[baseId])<2||P.zel<r.demoZel||!Object.entries(r.materials).every(([id,n])=>(P.materials[id]||0)>=n))return;
   if(!confirm(`Evolve ${current.name} into Unit ${r.evolvedId}? Spend ${r.demoZel} demo Zel and catalysts (original recipe: ${r.archivedZel} Zel); unit returns to Lv.1. Your squad slot is preserved.`))return;
   P.zel-=r.demoZel;for(const [id,n] of Object.entries(r.materials))P.materials[id]-=n;
   P.evolutions[baseId]=r.evolvedId;P.unitExp[baseId]=0;
   saveProgress();reset();renderProgress();E.evoresult.textContent=`Evolution complete: ${current.name} → ${next.name}. Original artwork and archived base stats now active.`;
  };
  card.append(thumbnail,info,button);E.evolist.append(card);
 }
}
'''
    s=s[:start]+new+s[end:]
    assert s.count('function renderEvolutionPanel(){')==1 and s.count('const BF_VERIFIED_POWER_V033=')==1
    # Original-stage marker also checked when idempotently rebuilding.
    assert s.count('const EVO_RECIPES=')==1
    s=s.replace('const EVO_RECIPES=[',mark+'\nconst EVO_RECIPES=[',1)
    index.write_text(s,'utf8')
    print('PASS v0.33 six archived 4-star second-stage forms, original battle art and staged v7 evolution-chain support')
