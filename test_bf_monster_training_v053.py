"""v0.53: archived BF1 sprite frames 0009–0016 only in opt-in demo Training."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_monster_training_v053.json').read_text('utf-8'))
atlas=(R/source['derivedAtlas']['sourcePath']).read_bytes()
assert hashlib.sha256(atlas).hexdigest()==source['derivedAtlas']['sha256']
assert (A/source['derivedAtlas']['apkPath']).read_bytes()==atlas
assert [r['id'] for r in source['entries']]==[f'{i:04d}' for i in range(9,17)]
assert source['runtime']['optInDefault'] is False
htmlfile=A/'index.html'
html=htmlfile.read_text('utf-8')
assert html.count('/* BF_MONSTER_TRAINING_HOOK_V053 */')==1
assert html.count('/* BF_MONSTER_TRAINING_DRAW_V053 */')==1
assert html.count('/* BF_ORIGINAL_MONSTER_TRAINING_V053 */')==1
assert 'bf_global_offline_demo_v7' in html
prior=hashlib.sha256(html.encode()).hexdigest()
subprocess.run([sys.executable,str(R/'prepare_monster_training_v053.py')],check=True,cwd=R)
assert hashlib.sha256(htmlfile.read_bytes()).hexdigest()==prior

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,
       executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
       args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def local(route):
        rel=route.request.url.split('bf-assets.test/',1)[-1]
        path=A/rel
        if path.is_file() and path.resolve().is_relative_to(A.resolve()) and path.suffix in ('.png','.jpg'):
            route.fulfill(status=200,body=path.read_bytes(),content_type='image/jpeg' if path.suffix=='.jpg' else 'image/png')
        else:route.fulfill(status=404,body=b'')
    page.route('http://bf-assets.test/**',local)
    page.evaluate("""() => {
      const data={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>data[k]??null,setItem:(k,v)=>{data[k]=String(v)},
        removeItem:k=>{delete data[k]},key:i=>Object.keys(data)[i]??null,
        get length(){return Object.keys(data).length}}});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),
        wait_until='load',timeout=90000)
    page.wait_for_function('()=>BF053TrainingMonsters.imageLoaded',timeout=15000)
    assert page.evaluate('BF053TrainingMonsters.sourceIds')==[f'{i:04d}' for i in range(9,17)]
    assert page.evaluate('BF053TrainingMonsters.enabled') is False
    assert page.evaluate('P.version')==7
    assert page.evaluate('S.enemies.every(e=>!e.id.startsWith("bf053_"))') is True
    page.locator('#mode').select_option('training')
    snap=page.evaluate("""() => ({save:localStorage.getItem('bf_global_offline_demo_v7'),
        progress:JSON.stringify(P),version:P.version})""")
    assert page.evaluate('S.mode')=='training'
    assert page.evaluate('S.enemies.every(e=>!e.id.startsWith("bf053_"))') is True
    toggle=page.locator('#bf053-extra-monsters')
    assert not toggle.is_checked()
    toggle.check()
    assert page.evaluate('BF053TrainingMonsters.enabled') is True
    assert page.evaluate('S.enemies.every(e=>e.id.startsWith("bf053_"))') is True
    assert page.evaluate('S.enemies.every(e=>e.sourceArtOriginal===true)') is True
    assert page.evaluate('S.enemies.every(e=>e.name.includes("DEMO combat"))') is True
    check=page.evaluate("""() => {
       let canv=document.createElement('canvas');canv.width=480;canv.height=344;
       let ctx=canv.getContext('2d');
       let calls=0;
       const drawImage=ctx.drawImage.bind(ctx);
       ctx.drawImage=(...args)=>{calls++;return drawImage(...args)};
       let drawn=BF053TrainingMonsters.drawSprite(S.enemies[0],performance.now(),ctx,120,150);
       return {drawn,calls};
    }""")
    assert check['drawn'] and check['calls']==1,check
    for wave in [0,1,3,7,8]:
        out=page.evaluate("""w=>BF053TrainingMonsters.encounter('training',w,
            [{id:'gel',name:'base',maxHp:100,atk:20,def:10}])""",wave)
        assert len(out)==1 and out[0]['id'].startswith('bf053_') and out[0]['sourceArtOriginal'] is True
    assert page.evaluate("""() => BF053TrainingMonsters.encounter('archive',0,
        [{id:'gel',maxHp:100,atk:20,def:10}])""") is None
    assert page.evaluate('JSON.stringify(P)')==snap['progress']
    assert page.evaluate('P.version')==snap['version']==7
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==snap['save']
    toggle.uncheck()
    assert page.evaluate('S.enemies.every(e=>!e.id.startsWith("bf053_"))') is True
    assert page.evaluate('JSON.stringify(P)')==snap['progress']
    page.locator('#mode').select_option('archive')
    toggle.check()
    assert page.evaluate('S.enemies.every(e=>!e.id.startsWith("bf053_"))') is True
    assert not errors,errors
    browser.close()
print('PASS v0.53 8 original archived sprite sheets, animation frame crops, opt-in training only, demo stats, save v7')
