"""v0.44 Chrome regression: opt-in SBB prototype separate from original BB."""
from pathlib import Path
import shutil,json,base64,gzip,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
html=(R/'app/src/main/assets/index.html').read_text('utf8')
assert html.count('/* BF_EXPERIMENTAL_SBB_V044 */')==1
for marker in ('/* BF_GLOBAL_SBB_PREVIEW_V043 */','/* BF_COORDINATED_AUTO_V042 */','/* BF_SOURCE_AWARE_AUTO_V041 */','/* BF_EVOLUTION_ROADMAP_V039 */'):
    assert html.count(marker)==1,marker
assert html.count("if(action.kind==='sbb_demo' && window.BF044SBBDemo?.perform)")==1
meta=json.loads((R/'source_data/bf_global_original_lore_meta.json').read_text())
packed=base64.b64decode((R/'source_data/bf_global_original_lore_codex.json.gz.b64').read_text())
assert hashlib.sha256(packed).hexdigest()==meta['payloadGzipSha256']
src={u['id']:u for u in json.loads(gzip.decompress(packed))['units']}
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
    page=b.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.route('http://bf-assets.test/**',lambda route:route.fulfill(status=404,body=b''))
    page.evaluate("""()=>{const store={};window.__sbb044store=store;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>store[k]??null,setItem:(k,v)=>{store[k]=String(v)},
        removeItem:k=>{delete store[k]},key:i=>Object.keys(store)[i]??null,
        get length(){return Object.keys(store).length}}});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
    assert page.locator('#bf044-enable').count()==1
    assert page.evaluate('BF044SBBDemo.enabled()') is False
    assert page.evaluate('BF043SBBSource.count')==12
    assert page.locator('#burst').count()==1
    before=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
    result=page.evaluate("""async()=>{
      BF_debug.reset();
      S.selected=0;const p=S.party[0];
      p.unitId=10015;p.name='Test Vargas';p.bb=100;
      S.enemies=[0,1,2].map(slot=>({slot,name:'Dummy '+slot,
        hp:100000,maxHp:100000,def:40,atk:5}));S.target=1;
      const disabled=BF044SBBDemo.queue();
      document.getElementById('bf044-enable').checked=true;
      BF044SBBDemo.refresh();
      const allowed=BF044SBBDemo.canQueue();
      const queued=BF044SBBDemo.queue();
      const action=p.action?.kind;
      wait=()=>Promise.resolve();
      await performUnit(p,epoch);
      const damaged=S.enemies.map(e=>100000-e.hp);
      const spent=p.bb,log=E.log.textContent;
      const noEffect=p.atkBuff===undefined || p.atkBuff===null;
      S.selected=0;p.unitId=10011;p.bb=100;p.action=null;
      const noSource=BF044SBBDemo.queue();
      p.unitId=60025;p.bb=100;p.action=null;
      const mifune=BF044SBBDemo.sourceFor(60025);
      const canMifune=BF044SBBDemo.canQueue();
      document.getElementById('bf044-enable').checked=false;
      const disabledAgain=BF044SBBDemo.queue();
      return {disabled,allowed,queued,action,damaged,spent,log,noEffect,
        noSource,mifune,canMifune,disabledAgain,schema:P.version,
        legacyBBButton:!!document.getElementById('burst')};
    }""")
    assert not result['disabled'] and result['allowed'] and result['queued'],result
    assert result['action']=='sbb_demo',result
    assert all(n>0 for n in result['damaged']),result
    assert result['spent']==0 and result['noEffect'],result
    assert 'EXPERIMENTAL SBB DEMO' in result['log'] and 'SIMULATED' in result['log'],result
    assert not result['noSource'] and result['canMifune'] and not result['disabledAgain'],result
    assert result['mifune']['name']==src[60025]['sbb']['name']
    assert result['mifune']['combo'] is None,result
    assert result['schema']==7 and result['legacyBBButton']
    assert page.evaluate("JSON.stringify(P)")==before['p']
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before['save']
    assert not errors,errors
    print('PASS v0.44 opt-in 12 SBB IDs, all-enemy prototype, honest demo labeling, old BB and v7 untouched')
    b.close()
