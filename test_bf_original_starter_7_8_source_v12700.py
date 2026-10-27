"""v127: fail-closed preflight for original 2022 Global 7★/8★ starter assets.

Original source (unit stats, typed recipes and sprite file SHA) is reference-only:
no forms become playable, no rendering transforms guessed, no save migration.
"""
from pathlib import Path
from collections import Counter
import base64, gzip, hashlib, json, shutil
from playwright.sync_api import sync_playwright

R = Path(__file__).resolve().parent
A = R / 'app/src/main/assets'
M = json.loads((R/'source_data/bf_global_2022_starter_7_8_source_readiness_v127.json').read_text('utf8'))
assert M['schema'] == 'bf-global-2022-7-8-starter-source-readiness-v127'
assert M['sourceZipSha256'] == '69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert [x['path'].rsplit('/',1)[-1] for x in M['sourceFiles']] == [
    'F_UNIT_MST_1_Ver1084.json', 'F_UNIT_MST_2_Ver1084.json','F_UNIT_EVO_MST_Ver597.json']
assert M['ownerAssetPacks'] == [
    {'name':'BF1_unit_part001.zip','sha256':'c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846','sizeBytes':136466482},
    {'name':'BF1_unit_part007.zip','sha256':'ad937083a4d023228f8796d45e5edd6adaf575872270476be994121941db3556','sizeBytes':40405512}
]
rows=M['rows']
assert len(rows)==12 and len({r['unitId'] for r in rows})==12
assert {r['unitId'] for r in rows}=={x*10000+y for x in range(1,7) for y in (16,17)}
assert Counter(r['rarity'] for r in rows)=={7:6,8:6}
assert all(r['previousFormId']==r['unitId']-1 for r in rows)
assert all(r['unitMaxLevel']==(120 if r['rarity']==7 else 150) for r in rows)
assert all(r['unitCost']==(38 if r['rarity']==7 else 45) for r in rows)
assert all(r['animation']['unverifiedTransformLayers']>0 and
           r['animation']['unknownFlagsPresent'] and
           r['animation']['nativeRendererProven'] is False for r in rows)
assert all(len(r['assets'])==6 for r in rows)
paths=[a['path'] for r in rows for a in r['assets']]
assert len(paths)==len(set(paths))==72
assert all(len(a['sha256'])==64 and a['bytes']>0 and
           a['pack'] in ('BF1_unit_part001.zip','BF1_unit_part007.zip')
           for r in rows for a in r['assets'])
assert all(x['originalEvo']['materialSlots'] and all(m['type'] in (1,2) for m in x['originalEvo']['materialSlots']) for x in rows)
assert all(any(m['type']==2 for m in x['originalEvo']['materialSlots']) for x in rows)
canonical=json.dumps([[r['unitId'],r['previousFormId'],r['rarity'],r['unitCost'],
                       r['unitMaxLevel'],r['expPatternId'],r['base'],r['lordAtMax'],
                       r['originalEvo']] for r in rows],separators=(',',':'),sort_keys=True)
assert hashlib.sha256(canonical.encode()).hexdigest()==M['canonical12SourceSha256']=='dcd3fb0f3d57b44880088f42c87409e3588a24a183ec866095ea0dbeae57bcbd'

# Independently rejoin exact 2022 decoded archive packaged in the repo.
archive=json.loads(gzip.decompress(base64.b64decode((R/'source_data/bf_global_original_unit_catalog.json.gz.b64').read_text('ascii'))))
lookup={u['id']:u for u in archive['units']}
assert len(lookup)==2291
for row in rows:
    src=lookup[row['unitId']]
    assert src['rarity']==row['rarity'] and src['unitMaxLevel']==row['unitMaxLevel'] and src['unitCost']==row['unitCost'], row['unitId']
    for k in ('hp','atk','def','rec'):
        assert src['unitBase'+k.title()]==row['base'][k],row['unitId']
        assert src['unitLord'+k.title()]==row['lordAtMax'][k],row['unitId']

# Owner saves and current gameplay must stay 72 playable source forms, NOT 84.
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.evaluate("""() => {
      const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
        removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
        get length(){return Object.keys(db).length}}});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
    result=page.evaluate("""() => ({
      version:P.version, saveKey:'bf_global_offline_demo_v7',
      stored:localStorage.getItem('bf_global_offline_demo_v7'),
      starters:BF_STARTER_UNITS.map(u=>u.id),
      evolved:BF_EVOLVED_UNITS.map(u=>u.id),
      saveSnapshot:JSON.stringify(P)
    })""")
    assert result['version']==7 and len(result['starters'])==18 and len(result['evolved'])==54
    assert not ({r['unitId'] for r in rows}&set(result['starters']+result['evolved']))
    assert page.evaluate('JSON.stringify(P)')==result['saveSnapshot']
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==result['stored']
    assert not errors,errors
    browser.close()
print('PASS v127: 12 original 7/8-star starter source + 72 exact art references, native animation unverified and 72 playable/v7 saves untouched')
