"""Source-backed 2022 Brave Frontier Global unit lore/skills/evolutions normalization.
This must run against the user's archived MST/sgtext zip, never invent names/effects.
Output contains *descriptive strings*, not executable effect rules or gameplay recipes.
"""
from zipfile import ZipFile
from pathlib import Path
import json,io,base64,re,hashlib,collections,html,gzip
# Supply the downloaded archives in the same working directory when regenerating.
ROOT=Path(__file__).resolve().parent
MST=ROOT/'mst-decoded.zip'; SGT=ROOT/'BF1_sgtext_part001.zip'
archive=json.loads((ROOT/'BF_Global_2022_Original_Unit_Catalog.json').read_text())
ids={int(x['id']) for x in archive['units']}
assert len(ids)==2291
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(MST)=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert sha(SGT)=='4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
print('MST SHA',sha(MST),'SGTEXT SHA',sha(SGT))

def parse_en_zip(name):
    with ZipFile(SGT) as z:
      fn=[n for n in z.namelist() if n.split('/')[-1].lower().startswith(name.lower()+'_')]
      assert len(fn)==1,(name,fn)
      with ZipFile(io.BytesIO(z.read(fn[0]))) as inner:
        b=base64.b64decode(inner.read(inner.namelist()[0]))
        out={}
        for row in b.decode('utf-8-sig').splitlines()[1:]:
          parts=row.rstrip('\r').split('^')
          if len(parts)>=2 and parts[0].strip() and parts[1].strip():
            out[parts[0].strip()]=parts[1].strip()
        return out
names={}
for key in ['sgtext_skillName','sgtext_SkillDescription','sgtext_leaderSkillName','sgtext_leaderSkillDescription','sgtext_extraPassiveSkill_Name','sgtext_extraPassiveSkill_DESC','sgtext_unitComments_D','sgtext_itemMaterialName','sgtext_itemConsumableName']:
 names[key]=parse_en_zip(key)
 print(key,len(names[key]),'example',next(iter(names[key].items())))

def tbl(family):
  with ZipFile(MST) as z:
    paths=[n for n in z.namelist() if n.startswith('3-mst-translated/'+family+'_') and n.endswith('.json')]
    assert paths,family
    rows=[]
    for p in paths:rows+=json.loads(z.read(p))
    print('table',family,len(rows));return rows
comments={int(r['unitId']):r for r in tbl('F_UNIT_COMMENT_MST')}
skills={int(r['bbId']):r for r in tbl('F_SKILL_MST')}
leaders={int(r['lsId']):r for r in tbl('F_LEADER_SKILL_MST')}
extras={int(r['esId']):r for r in tbl('F_EXTRA_PASSIVE_SKILL_MST')}
evolutions=collections.defaultdict(list)
for r in tbl('F_UNIT_EVO_MST'):
  base=int(r['unitId']); nxt=int(r['evoUnitId']);
  mats=[]
  for k in range(1,11):
    mid=int(r.get('evoMaterialId'+str(k),'0') or 0)
    if mid: mats.append({'type':int(r.get('evoMaterialType'+str(k),'0') or 0),'id':mid})
  if base in ids and nxt in ids:
    evolutions[base].append({'target':nxt,'zel':int(r['zel'] or 0),'karma':int(r['karma'] or 0),'materials':mats})
# English translation texts must match source keys. Master literal accepted only if is ASCII-ish latin.
western=re.compile(r'^[\x09\x0a\x0d\x20-\x7e\xa0-\xff]+$')
placeholder=re.compile(r'^(MST_|[A-Z0-9_]+_(NAME|DESCRIPTION)$)')
markup=re.compile(r'<br\s*/?>',re.I)
otherTags=re.compile(r'<[^>]*>')
def clean(v):
  return html.unescape(otherTags.sub('',markup.sub(' \n ',v or ''))).strip()

def localized(raw,dictkey):
  if not raw:return None
  trans=names[dictkey].get(raw)
  if trans:return clean(trans)
  if placeholder.match(raw):return None
  if western.fullmatch(raw):return clean(raw)
  return None

itemRows=tbl('F_ITEM_MST')
itemDict={int(r['itemId']):r for r in itemRows}
item_names={}
for mid in {m['id'] for v in evolutions.values() for e in v for m in e['materials']}:
  r=itemDict.get(mid)
  if r:
    key=r.get('itemName','')
    item_names[mid]=localized(key,'sgtext_itemMaterialName') or localized(key,'sgtext_itemConsumableName')

catalog=[]
counts=collections.Counter()
for row in archive['units']:
  uid=int(row['id']);comm=comments.get(uid,{})
  story=localized(comm.get('description',''),'sgtext_unitComments_D')
  if story:counts['story']+=1
  code={'id':uid}
  if story:code['story']=story
  if evolutions[uid]:
    recipes=[]
    for e in evolutions[uid]:
      recipe=dict(e)
      recipe['materials']=[{'type':m['type'],'id':m['id'],**({'name':item_names[m['id']]} if item_names.get(m['id']) else {})} for m in e['materials']]
      recipes.append(recipe)
    code['recipes']=recipes
    counts['recipes']+=len(recipes)
  def ability(table,idField,nameField,nameKey,descKey):
    skId=int(row.get(idField,0) or 0)
    if not skId:return None
    source=table.get(skId)
    if not source:return None
    original_name=localized(source.get(nameField,''),nameKey)
    original_desc=localized(source.get('description',''),descKey)
    if not original_name and not original_desc:return None
    info={'id':skId}
    if original_name:info['name']=original_name
    if original_desc:info['description']=original_desc
    return info
  for typ,table,idfield,namefield,nkey,dkey in [
    ('leader',leaders,'lsId','lsName','sgtext_leaderSkillName','sgtext_leaderSkillDescription'),
    ('bb',skills,'bbId','skillName','sgtext_skillName','sgtext_SkillDescription'),
    ('sbb',skills,'sbbId','skillName','sgtext_skillName','sgtext_SkillDescription'),
    ('ubb',skills,'ubbId','skillName','sgtext_skillName','sgtext_SkillDescription'),
    ('extra',extras,'esId','skillName','sgtext_extraPassiveSkill_Name','sgtext_extraPassiveSkill_DESC')]:
    info=ability(table,idfield,namefield,nkey,dkey)
    if info:
      code[typ]=info;counts[typ]+=1
  catalog.append(code)
payload={'schema':'bf-global-original-lore-codex-v1',
 'provenance':{'mstZipSha256':sha(MST),'englishTextZipSha256':sha(SGT),
 'normalization':'Original 2022 Global English strings + literal ASCII master descriptions; no combat-effect interpretation.'},
 'stats':{'rows':len(catalog),**dict(counts)},'units':catalog}
raw=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf8')
compressed=gzip.compress(raw,compresslevel=9,mtime=0)
(ROOT/'BF_Global_2022_Original_Lore_Codex.json').write_bytes(raw)
(ROOT/'BF_Global_2022_Original_Lore_Codex.json.gz.b64').write_text(base64.b64encode(compressed).decode('ascii')+'\n')
meta={'schema':'bf-global-original-lore-package-v1','payloadJsonSha256':hashlib.sha256(raw).hexdigest(),'payloadGzipSha256':hashlib.sha256(compressed).hexdigest(),'payloadRecordCount':2291,'jsonBytes':len(raw),'gzipBytes':len(compressed),'stats':dict(counts),'mstZipSha256':sha(MST),'englishTextZipSha256':sha(SGT)}
(ROOT/'bf_global_original_lore_meta.json').write_text(json.dumps(meta,indent=2)+'\n')
print('COUNTS',counts,'bytes',len(raw),'gzip',len(compressed))
for id in (10011,10012,20011,810547,850198):
  print('\nEXAMPLE',id,json.dumps(next(x for x in catalog if x['id']==id),ensure_ascii=False)[:2400])
