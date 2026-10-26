"""v0.32 source-backed 6 playable Global first evolutions; browser regressions."""
from pathlib import Path
import base64,gzip,hashlib,json,shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
MAN=json.loads((ROOT/'source_data/bf_global_six_evolutions_v032.json').read_text('utf-8'))
IDS={int(k) for k in MAN['records']}
assert IDS=={10042,20042,30042,40042,50042,60042}
html=(A/'index.html').read_text('utf-8')
assert html.count('/* BF_GLOBAL_SIX_EVOLUTIONS_V032 */')==1
for uid in IDS:
    for suffix in (f'unit_anime_atlas_{uid}.png',f'unit_ills_thum_{uid}.png'):
        assert (A/'content/extra_evolution'/suffix).is_file()

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=shutil.which('google-chrome') or shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    def serve(route):
        from urllib.parse import urlsplit
        path=urlsplit(route.request.url).path.lstrip('/') or 'index.html'
        file=(A/path).resolve()
        if not file.is_file() or not file.is_relative_to(A.resolve()):
            route.fulfill(status=404,body=b'not found');return
        mime=('text/html' if path.endswith('.html') else 'image/png' if path.endswith('.png') else 'text/plain')
        route.fulfill(status=200,content_type=mime,body=file.read_bytes())
    page.route('http://bf-assets.test/**',serve)
    page.evaluate('''() => {
        const store={}; window.__store=store;
        Object.defineProperty(window,'localStorage',{configurable:true,value:{
          getItem(k){return store[k]??null},setItem(k,v){store[k]=String(v)},
          removeItem(k){delete store[k]},key(n){return Object.keys(store)[n]??null},
          get length(){return Object.keys(store).length}
        }});
        window.confirm=()=>true;window.alert=()=>{};
    }''')
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
    print('initial errors',errors, flush=True)
    result=page.evaluate('''() => ({len:window.BF_EVOLVED_UNITS.length,recipe:EVO_RECIPES.length,
       bases:STARTERS.length,roster:P.roster.slice(),schema:P.version,bb:Object.keys(window.BF_ARCHIVE_BB_HITS).length,
       added:[10042,20042,30042,40042,50042,60042].map(id=>({id,unit:UNIT_BY_ID.get(id)?.name,scope:bfOriginalBB(id)?.target,
       skill:bfOriginalBB(id)?.name,power:bfOriginalBBPower(id)?.base||null,support:originalSupport(id)?.low||null,
       image:imagesById.get(id)?.src,frames:UNIT_BY_ID.get(id)?.frameCount}))})''')
    assert (result['len'],result['recipe'],result['bases'],result['schema'],result['bb'])==(54,54,18,7,72),result
    assert len(result['roster'])==6
    assert not errors,errors
    print('PASS 6 new source-verified evolved forms registered; existing v7 starters/saves and 36 archived BB records')
    page.wait_for_function('''() => [10042,20042,30042,40042,50042,60042].every(id => imagesById.get(id).naturalWidth>0)''',timeout=45000)
    assert all(r['frames']>10 and r['image'].endswith('.png') for r in result['added'])
    print('PASS original 6 CGG/CGS battle atlases loaded from offline Android content paths')
    # All six new evolution buttons must update the v7 mapping by original base ID.
    for new_id in sorted(IDS):
        base=new_id-1
        data=page.evaluate('''(base) => {
           BF_debug.reset();
           P.roster=[...new Set([...P.roster,base])];
           P.squad=[base];P.materials={};P.evolutions={};P.zel=90000;
           P.unitExp[base]=100;
           const rec=EVO_BY_BASE.get(base);
           for(const [id,n] of Object.entries(rec.materials))P.materials[id]=n;
           renderEvolutionPanel();
           const card=[...document.querySelectorAll('.evocard')].find(e=>e.innerText.includes(UNIT_BY_ID.get(base).name));
           const btn=card?.querySelector('.evoaction');
           return {base,materials:rec.materials,source:rec.archivedZel,buttonText:btn?.textContent,enabled:btn&&!btn.disabled,
                cardText:card?.innerText?.slice(0,400)};
        }''',base)
        assert data['source']==50000 and data['enabled'],data
        page.evaluate('''(base) => {
           const card=[...document.querySelectorAll('.evocard')].find(e=>e.innerText.includes(UNIT_BY_ID.get(base).name));
           card.querySelector('.evoaction').click();
        }''',base)
        after=page.evaluate('''({base,id}) => ({evolution:P.evolutions[base],chosen:effectiveUnit(base)?.name,
            played:S.party[0].unitId,level:demoLevel(P.unitExp[base]),saved:JSON.parse(localStorage.getItem('bf_global_offline_demo_v7')),
            image:imagesById.get(id).naturalWidth})''',{'base':base,'id':new_id})
        assert after['evolution']==new_id and after['played']==new_id and after['level']==1,after
        assert after['saved']['version']==7 and after['saved']['evolutions'][str(base)]==new_id,after
        assert after['image']>0 and not errors,errors
        print('PASS playable evolution',base,'→',new_id,after['chosen'])
    # Three original BB classes for new forms: AoE +60%, single +70%, and
    # party base recovery 1000..1200 (unverified REC terms still excluded).
    bb=page.evaluate('''async () => {
       P.squad=[60041,10011];BF_debug.reset();wait=()=>Promise.resolve();
       const p=S.party[0];p.active=true;p.hp=Math.max(1,p.hp);
       S.enemies=[0,1,2].map(slot=>({slot,id:1001+slot,name:'Demo foe',hp:50000,maxHp:50000,atk:50,def:20}));
       S.target=1;p.unitId=10042;p.bb=100;p.action={kind:'burst',target:1};
       await performUnit(p,epoch);
       const aoe=S.enemies.map(e=>50000-e.hp);
       for(const e of S.enemies)e.hp=50000;
       p.unitId=60042;p.bb=100;p.action={kind:'burst',target:1};
       await performUnit(p,epoch);
       const single=S.enemies.map(e=>50000-e.hp);
       for(const e of S.enemies)e.hp=50000;
       const ally=S.party[1];ally.active=true;ally.maxHp=6000;ally.hp=1000;
       p.unitId=20042;p.bb=100;p.action={kind:'burst',target:1};
       await performUnit(p,epoch);
       return {aoe,single,heal:ally.hp-1000,foes:S.enemies.map(e=>e.hp),bb:p.bb,
               skills:[bfOriginalBB(10042).name,bfOriginalBB(60042).name,bfOriginalBB(20042).name]};
    }''')
    assert len(bb['aoe'])==3 and all(v>0 for v in bb['aoe']),bb
    assert bb['single'][0]==0 and bb['single'][1]>0 and bb['single'][2]==0,bb
    assert 1000<=bb['heal']<=1200 and bb['foes']==[50000]*3 and bb['bb']==0,bb
    assert bb['skills']==['Meteor Storm','Grand Despair','Cure Storm'],bb
    print('PASS newly playable original BBs: all-enemy, single-target, and 1000–1200 base party recovery')
    # Reload from an existing v7 save with one newly evolved unit.
    saved_data=page.evaluate('window.__store')
    page.close()
    page=browser.new_page(viewport={'width':390,'height':844})
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.route('http://bf-assets.test/**',serve)
    page.evaluate('''(saved) => {
      window.__store=saved;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return saved[k]??null},setItem(k,v){saved[k]=String(v)},
        removeItem(k){delete saved[k]},key(n){return Object.keys(saved)[n]??null},
        get length(){return Object.keys(saved).length}
      }});
      window.confirm=()=>true;window.alert=()=>{};
    }''',saved_data)
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
    restored=page.evaluate('''() => ({version:P.version,form:P.evolutions[60041],party:S.party[0]?.unitId,
                              noError:!saveRecoveryPending})''')
    assert restored['version']==7 and restored['form']==60042 and restored['party']==60042 and restored['noError'],restored
    print('PASS v7 save reload recognizes new original evolution ID, original sprite and party slot')
    assert not errors,errors
    browser.close()
