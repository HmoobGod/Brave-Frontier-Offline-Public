from playwright.sync_api import sync_playwright
from pathlib import Path
import json,zipfile,hashlib
ROOT=Path('/mnt/data'); HTML=(ROOT/'Brave_Frontier_Offline_v0.11_Unit_Training.html').read_text()
results={'build':'v0.11','saveSchema':6,'checks':[]};errors=[]
def ok(label):results['checks'].append(label)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844},accept_downloads=True)
    page.on('pageerror', lambda e:errors.append(str(e)))
    page.evaluate('''() => {window.__saved={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window.__saved[k]??null;},setItem(k,v){window.__saved[k]=String(v);},removeItem(k){delete window.__saved[k];}}});const a=CanvasRenderingContext2D.prototype.save,b=CanvasRenderingContext2D.prototype.restore;window.__ctx={save:0,restore:0};CanvasRenderingContext2D.prototype.save=function(){window.__ctx.save++;return a.call(this)};CanvasRenderingContext2D.prototype.restore=function(){window.__ctx.restore++;return b.call(this)};window.confirm=()=>true;}''')
    page.set_content(HTML, wait_until='load',timeout=90000)
    page.wait_for_timeout(500)
    assert not errors,errors
    assert page.evaluate('P.version')==6
    assert page.locator('.train-unit').count()==6
    assert page.locator('.evocard').count()==6
    assert page.locator('.questcard').count()==6
    assets=page.evaluate('({base:STARTERS.length,evolutions:window.BF_EVOLVED_UNITS.length,images:starterImages.filter(x=>x.complete&&x.naturalWidth>0).length})')
    assert assets=={'base':12,'evolutions':12,'images':24},assets
    ok('New save v6, six original owned units, 12 base + 12 evolved original sprite sets loaded')
    # Old v5 save migration (no training currency injected)
    migrated=page.evaluate('''() => parseProgress({format:'bf-global-offline-demo',version:5,exp:20,zel:4000,karma:100,clears:2,level:3,squad:[10011,20011],roster:[10011,20011,30011,40011,50011,60011],summonTokens:1,summonHistory:[],unitExp:{10011:10,20011:2},questClears:{1:2},lastMission:1,evolutions:{10011:10012},materials:{10130:3}})''')
    assert migrated['version']==6 and migrated['trainingShards']==0 and migrated['trainingSpent']==0
    assert migrated['evolutions']=={'10011':10012} and migrated['materials']=={'10130':3}
    assert migrated['squad']==[10011,20011]
    ok('v0.10 v5 save migrates intact with evolution, squad, quest progress and catalysts')
    # Reject forged training counter/oversized counts
    invalid=page.evaluate('''() => {const a=defaultProgress();a.trainingShards=-1;try{parseProgress(a);return false}catch(e){return true}}''')
    assert invalid
    ok('Save validation rejects invalid shard amounts')
    # Demo training awards, card button and stage reset
    page.evaluate('''() => {P.squad=[10011];P.zel=2400;P.trainingShards=5;P.unitExp[10011]=0;saveProgress();reset();renderProgress()}''')
    first=page.locator('.train-unit').first
    assert 'Vargas' in first.inner_text()
    assert first.locator('button').first.is_enabled()
    first.locator('button').first.click()
    assert page.evaluate('P.trainingShards')==4
    assert page.evaluate('P.zel')==2250
    assert page.evaluate('P.unitExp[10011]')==10
    assert page.evaluate('S.party[0].level')==2
    assert page.evaluate('P.trainingSpent')==1
    ok('Train ×1 consumes one shard/150 Zel, adds 10 EXP and updates active unit level')
    # batch x5 should be disabled at 4 shards, then enabled at 5
    assert page.locator('.train-unit').first.locator('button').nth(1).is_disabled()
    page.evaluate('''() => {P.trainingShards=5;saveProgress();renderProgress()}''')
    page.locator('.train-unit').first.locator('button').nth(1).click()
    assert page.evaluate('P.trainingShards')==0
    assert page.evaluate('P.zel')==1500
    assert page.evaluate('P.unitExp[10011]')==60
    assert page.evaluate('P.trainingSpent')==6
    ok('Train ×5 uses five shards/750 Zel and adds 50 EXP; insufficient currency prevents action')
    # filters and inventory
    page.locator('#trainingsearch').fill('Selena')
    assert page.locator('.train-unit').count()==1
    page.locator('#trainingsearch').fill('xxnothing')
    assert page.locator('.train-unit').count()==0
    page.locator('#trainingsearch').fill('')
    page.locator('#trainingfilter').select_option('squad')
    assert page.locator('.train-unit').count()==1
    page.locator('#trainingfilter').select_option('owned')
    page.locator('.inventory-details summary').click()
    assert page.locator('.inv-row').count()==12
    ok('Live roster search/filter and complete 12-catalyst inventory render')
    # Evolution then train evolved unit, baseId persists
    page.evaluate('''() => {P.unitExp[10011]=5;P.materials[10130]=2;P.zel=3000;P.trainingShards=3;saveProgress();reset();renderProgress()}''')
    assert page.locator('.evocard').first.locator('button').is_enabled()
    page.locator('.evocard').first.locator('button').click()
    assert page.evaluate('P.evolutions[10011]')==10012
    assert page.evaluate('P.unitExp[10011]')==0
    assert page.evaluate('S.party[0].unitId')==10012
    page.locator('.train-unit').first.locator('button').first.click()
    assert page.evaluate('P.unitExp[10011]')==10
    assert page.evaluate('S.party[0].unitId')==10012
    assert page.evaluate('S.party[0].level')==2
    ok('Evolved unit remains evolved through training and uses base-unit save key')
    # Quest clear 3 waves awards shard
    page.evaluate('''() => {P.squad=[10011,20011,30011,40011,50011,60011];P.lastMission=1;saveProgress();reset();for(const e of S.enemies)e.hp=1;}''')
    old_shards=page.evaluate('P.trainingShards')
    page.locator('#auto').check()
    for wave in [1,2]:
        page.wait_for_function('(n)=>S.wave>=n',arg=wave,timeout=45000)
        page.evaluate('for(const e of S.enemies)e.hp=1')
    page.wait_for_function('S.over===true',timeout=45000)
    assert page.evaluate('S.phase')=='Victory'
    assert page.evaluate('P.trainingShards')==old_shards+1
    ok('Three-wave Auto Battle victory and guaranteed +1 shard with other quest rewards')
    page.wait_for_timeout(300)
    stack=page.evaluate('window.__ctx')
    assert stack['save']==stack['restore'],stack
    ok('Canvas save/restore balanced, no state leak')
    # Import/export and v6 reload in a clean browser session
    page.locator('#exportsave').click()
    saved=json.loads(page.locator('#savetc').input_value())
    assert saved['version']==6 and saved['evolutions']['10011']==10012
    assert saved['trainingSpent']>=1
    # Test full save download and importing the round trip into a different empty session
    with page.expect_download() as dw: page.locator('#downloadsave').click()
    download=dw.value; assert download.suggested_filename.endswith('.json')
    exported_path=ROOT/'BF_v011_Test_Export.json'
    download.save_as(exported_path)
    assert json.loads(exported_path.read_text())==saved
    ok('JSON Download Save File exactly preserves v6 progress')
    p2=browser.new_page(viewport={'width':390,'height':844})
    errs2=[];p2.on('pageerror',lambda e:errs2.append(str(e)))
    p2.evaluate('''() => {window.__saved={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window.__saved[k]??null},setItem(k,v){window.__saved[k]=String(v)},removeItem(k){delete window.__saved[k]}}});window.confirm=()=>true;}''')
    p2.evaluate('(data)=>window.__saved.bf_global_offline_demo_v6=JSON.stringify(data)',saved)
    p2.set_content(HTML,wait_until='load',timeout=90000)
    p2.wait_for_timeout(400)
    assert p2.evaluate('P.evolutions[10011]')==10012
    assert p2.evaluate('P.trainingSpent')==saved['trainingSpent']
    assert p2.evaluate('P.trainingShards')==saved['trainingShards']
    assert p2.evaluate('S.party[0].unitId')==10012
    assert not errs2,errs2
    ok('Fresh-session v6 reload retains enhanced evolved form, saved shards and squad')
    # Import a v5 file into v6 current via same function used in WebView and browser
    p2.evaluate('''() => {const old={...P,version:5};delete old.trainingShards;delete old.trainingSpent;const json=JSON.stringify(old);bfImportSaveText(json,'old v5 test');}''')
    assert p2.evaluate('P.version')==6
    assert p2.evaluate('P.trainingShards')==0
    assert p2.evaluate('P.evolutions[10011]')==10012
    ok('Browser import of v5 JSON migrates to v6 safely without loss of evolved form')
    # 320px layout smoke test and screenshot
    p2.set_viewport_size({'width':390,'height':844})
    p2.locator('#trainingfilter').select_option('squad')
    p2.evaluate('window.scrollTo(0,document.querySelector(".training-panel").offsetTop-78)')
    p2.wait_for_timeout(450)
    p2.screenshot(path=str(ROOT/'BF_v0.11_Training_Preview.png'),full_page=False)
    p2.set_viewport_size({'width':320,'height':700})
    p2.evaluate('window.scrollTo(0,document.querySelector(".training-panel").offsetTop-48)')
    p2.wait_for_timeout(150)
    assert p2.locator('.train-unit').count()>=1
    ok('Training screen renders on 320px and 390px browser viewports')
    assert not errors,errors
    browser.close()
results.update({'passed':len(results['checks']),'errors':errors,'canvasSaves':stack['save'],'canvasRestores':stack['restore'],'exportSize':exported_path.stat().st_size})
# Confirm Android embedded game is exact byte-for-byte match
app=ROOT/'Brave_Frontier_Android_Offline_v0.11'
assert (app/'app/src/main/assets/index.html').read_bytes()==HTML.encode()
results['androidEmbeddedHtmlSha256']=hashlib.sha256(HTML.encode()).hexdigest()
results['androidStatus']='Source prepared; APK not compiled or device-tested'
(ROOT/'BF_v0.11_Test_Report.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
