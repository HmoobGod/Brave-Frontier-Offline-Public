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
# The standard Android workflow explicitly runs THIS Chromium script.
# Execute the standalone three source-guard cases here as well, so
# they cannot silently remain outside CI's collected test commands.
import unittest
from test_bf_unit_box_filter_v10201 import UnitBoxFilterSourceTests
source_suite=unittest.defaultTestLoader.loadTestsFromTestCase(UnitBoxFilterSourceTests)
assert source_suite.countTestCases()==3
assert unittest.TextTestRunner(verbosity=1).run(source_suite).wasSuccessful()
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
 # v399: advisory locks must persist in the separate local marker key.
 # The prior implementation passed next.lock (undefined) and omitted the
 # locked property from JSON, so locks disappeared after a restart.
 marker='bf_global_offline_qol_unit_flags_v102'
 persisted=p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_qol_unit_flags_v102'))")
 assert persisted=={'version':1,'favorites':[10011],'locked':[10011]},persisted
 assert p.locator('[data-bf-unit-id="10011"]').get_attribute('data-bf-qol-favorite')=='true'
 p.locator('[data-bf-unit-id="20011"]').click()
 p.wait_for_function("BFGlobalQoLUnitFlagsV10200.state().id===20011")
 assert p.evaluate(api+'.change(20011,"favorites",true)') is True
 assert p.evaluate(api+'.favorites')==[10011,20011]
 persisted=p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_qol_unit_flags_v102'))")
 assert persisted['locked']==[10011] and persisted['favorites']==[10011,20011],persisted
 # Lock a second owned form and then update favorites; both advisory lock
 # records must survive another write, with no v7 game save mutation.
 assert p.evaluate(api+'.change(20011,"locked",true)') is True
 assert p.evaluate(api+'.change(10011,"favorites",false)') is True
 persisted=p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_qol_unit_flags_v102'))")
 assert persisted=={'version':1,'favorites':[20011],'locked':[10011,20011]},persisted
 assert p.evaluate(api+'.change(10011,"favorites",true)') is True
 # Open another isolated page with the persisted marker JSON to exercise
 # cold-start loading (not merely the in-memory flags array).
 q=b.new_page(viewport={'width':390,'height':844})
 q.set_content("""<html><body><div id="bf-owned-box"><div id="bf-box-results">
   <button class="bf-box-card" data-bf-unit-id="10011" aria-pressed="true">Vargas</button>
   <button class="bf-box-card" data-bf-unit-id="20011" aria-pressed="false">Selena</button>
   </div><section id="bf-box-detail"></section></div></body></html>""")
 q.evaluate("""saved=>{const db={'bf_global_offline_qol_unit_flags_v102':saved};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
   removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}}});
   window.P={version:7,roster:[10011,20011],squad:[10011,20011],questClears:{}};
 }""",p.evaluate("localStorage.getItem('bf_global_offline_qol_unit_flags_v102')"))
 q.add_script_tag(path=str(A/'bf10200_qol_unit_flags.js'))
 assert q.evaluate(api+'.locked')==[10011,20011]
 assert q.evaluate(api+'.favorites')==[10011,20011]
 assert q.evaluate(api+'.state().locked') is True
 q.close()
 # Restore the original single-lock fixture for existing owned-only gates.
 assert p.evaluate(api+'.change(20011,"locked",false)') is True
 assert p.evaluate(api+'.locked')==[10011]
 # Browser-backed filter checks exercise real owned cards and clicks,
 # not only source strings. They must be reversible and must not mutate v7.
 assert p.evaluate(api+'.change(20011,"favorites",false)') is True
 p.locator('#bf10200-show-favorites').click()
 assert p.evaluate(api+'.filter')=='favorites'
 assert p.locator('[data-bf-unit-id="10011"]').is_visible()
 assert p.locator('[data-bf-unit-id="20011"]').is_hidden()
 assert p.locator('#bf10200-show-favorites').get_attribute('aria-pressed')=='true'
 assert p.locator('#bf10200-filter-info').inner_text().startswith('1 of 2')
 assert p.evaluate(api+'.setFilter("not-a-filter")') is False
 assert p.evaluate(api+'.filter')=='favorites'
 p.locator('#bf10200-show-locks').click()
 assert p.evaluate(api+'.filter')=='locked'
 assert p.locator('[data-bf-unit-id="10011"]').is_visible()
 assert p.locator('[data-bf-unit-id="20011"]').is_hidden()
 assert p.locator('#bf10200-show-favorites').get_attribute('aria-pressed')=='false'
 assert p.locator('#bf10200-show-locks').get_attribute('aria-pressed')=='true'
 p.locator('#bf10200-show-locks').click()
 assert p.evaluate(api+'.filter')=='all'
 assert p.locator('[data-bf-unit-id="10011"]').is_visible()
 assert p.locator('[data-bf-unit-id="20011"]').is_visible()
 assert p.locator('#bf10200-filter-info').inner_text().startswith('2 of 2')
 assert p.evaluate(api+'.change(20011,"favorites",true)') is True
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==original
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
