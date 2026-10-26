"""v0.40 original Global BB source guide — read-only Chromium regression."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
html=(ROOT/'app/src/main/assets/index.html').read_text('utf-8')
assert html.count('/* BF_BATTLE_BB_GUIDE_V040 */')==1
assert html.count('id="bf040-bb-guide-style"')==1
assert html.count('/* BF_EVOLUTION_ROADMAP_V039 */')==1
assert 'bf_global_offline_demo_v7' in html
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
      args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('http://bf-assets.test/**',lambda r:r.fulfill(status=404,body=b''))
    page.evaluate("""() => {
      const store={};window.__bb040storage=store;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return store[k]??null},setItem(k,v){store[k]=String(v)},
        removeItem(k){delete store[k]},key(i){return Object.keys(store)[i]??null},
        get length(){return Object.keys(store).length}}});
      window.confirm=()=>true;window.alert=()=>{};
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
    assert page.locator('#bf040-bb-guide').count()==1
    assert page.locator('#burst').count()==1
    assert page.evaluate("document.getElementById('bf040-bb-guide').previousElementSibling.id")=='burst'
    before=page.evaluate("""()=>({p:JSON.stringify(P),s:localStorage.getItem('bf_global_offline_demo_v7')})""")
    result=page.evaluate("""()=>({
      base:BFGlobalBBGuideV040.infoFor(10011),
      single:BFGlobalBBGuideV040.infoFor(10021),
      heal:BFGlobalBBGuideV040.infoFor(20041),
      elite:BFGlobalBBGuideV040.infoFor(40025),
      six:BFGlobalBBGuideV040.infoFor(30025),
      unknown:BFGlobalBBGuideV040.infoFor(987654),
      invalid:BFGlobalBBGuideV040.infoFor('10011x')})""")
    assert result['base']['name']=='Flare Ride' and result['base']['target']=='all_enemies' and result['base']['lv1Power']==30,result
    assert result['single']['target']=='single_enemy' and result['single']['lv1Power']==150,result
    assert result['heal']['support']['kind']=='heal_all' and result['heal']['lv1Power'] is None,result
    assert result['elite']['name']=="Thunder General's Command" and result['elite']['support']['pct']==94,result
    assert result['six']['name']=='Meteoric Gust' and result['six']['lv1Power'] is None,result
    assert result['unknown'] is None and result['invalid'] is None,result
    page.evaluate("document.querySelector('#bf040-bb-guide summary').click()")
    page.evaluate("""()=>{BF_debug.reset();S.party[0].unitId=40025;S.selected=0;BFGlobalBBGuideV040.refresh()}""")
    assert 'Thunder General' in page.locator('#bf040-bb-guide .bf040-body').text_content()
    assert '+94%' in page.locator('#bf040-bb-guide .bf040-body').text_content()
    page.evaluate("""()=>{S.party[0].unitId=10021;BFGlobalBBGuideV040.refresh()}""")
    assert 'Single enemy' in page.locator('#bf040-bb-guide .bf040-body').text_content()
    assert 'DEMO' in page.locator('#bf040-bb-guide .bf040-body').text_content()
    page.evaluate("document.querySelector('#bf040-bb-guide summary').click()")
    assert page.evaluate("document.getElementById('bf040-bb-guide').open") is False
    assert page.locator('#attack').count()==page.locator('#execute').count()==1
    assert page.evaluate("P.version")==7
    assert page.evaluate("JSON.stringify(P)")==before['p']
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before['s']
    # Save parser still refuses forged evolution IDs; the guide cannot unlock them.
    refused=page.evaluate("""()=>{
      const sample=JSON.parse(JSON.stringify(P));
      sample.evolutions={'10021':987654};
      try{parseProgress(sample);return false}catch(e){return true}
    }""")
    assert refused
    assert not errors,errors
    print('PASS v0.40: authentic BB names/scope/Lv1 metadata; forged ID rejection, interactive optional guide, v7 and buttons unchanged')
    browser.close()
