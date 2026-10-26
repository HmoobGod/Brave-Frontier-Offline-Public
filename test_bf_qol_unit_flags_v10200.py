"""v102: independent persistent favorite/lock markers for owned unit box IDs."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf10200_qol_unit_flags.js').read_text('utf8')
assert js.count('BF_GLOBAL_QOL_UNIT_FLAGS_V10200')==1
assert len(js.encode())<65536
assert 'saveProgress(' not in js and 'P.roster=' not in js and 'bf_global_offline_demo_v7' not in js
assert 'advisoryOnly:true' in js
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
   const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
    removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
    get length(){return Object.keys(db).length}}});
 }""")
 p.set_content("""<html><body><div id="bf-owned-box">
 <div id="bf-box-results">
   <button class="bf-box-card" data-bf-unit-id="10011" aria-pressed="true">Vargas</button>
   <button class="bf-box-card" data-bf-unit-id="20011" aria-pressed="false">Selena</button>
 </div><section id="bf-box-detail">Selected unit</section></div></body></html>""")
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011,20011],squad:[10011,20011],questClears:{}};
   localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
   document.querySelectorAll('.bf-box-card').forEach(card=>card.addEventListener('click',()=>{
     document.querySelectorAll('.bf-box-card').forEach(c=>c.setAttribute('aria-pressed',String(c===card)));
   }));
 }""")
 original=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.add_script_tag(path=str(A/'bf10200_qol_unit_flags.js'))
 api='BFGlobalQoLUnitFlagsV10200'
 assert p.locator('#bf10200-flags').count()==1
 assert p.evaluate(api+'.state().id')==10011
 assert p.evaluate(api+'.state().favorite') is False
 assert p.evaluate(api+'.change(10011,"favorites",true)') is True
 assert p.evaluate(api+'.change(10011,"locked",true)') is True
 assert p.evaluate(api+'.state().favorite') is True
 assert p.evaluate(api+'.state().locked') is True
 assert p.locator('[data-bf-unit-id="10011"]').get_attribute('data-bf-qol-favorite')=='true'
 p.locator('[data-bf-unit-id="20011"]').click()
 p.wait_for_function("BFGlobalQoLUnitFlagsV10200.state().id===20011")
 assert p.evaluate(api+'.change(20011,"favorites",true)') is True
 assert p.evaluate(api+'.favorites')==[10011,20011]
 assert p.evaluate(api+'.change(999,"locked",true)') is False
 p.evaluate("P.roster=[20011]")
 assert p.evaluate(api+'.state().locks')==0
 assert p.evaluate(api+'.state().favorites')==1
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==original
 assert p.evaluate(api+'.state().advisoryOnly') is True
 p.add_script_tag(path=str(A/'bf10200_qol_unit_flags.js'))
 assert p.locator('#bf10200-flags').count()==1
 assert not errors,errors
 b.close()
print('PASS v102 unit marker persistence, owned-only toggles, advisory scope and save isolation')
