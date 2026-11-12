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
 p.set_content("""<html><body><section id="bf-home">
 <section class="bf-scene-squad"><div id="bf-scene-party">
   <div class="bf-scene-member"><strong>Vargas</strong></div>
   <div class="bf-scene-member"><strong>Selena</strong></div>
 </div></section></section><div id="bf-owned-box">
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
 assert p.locator('#bf-home .bf-home-unit-flags').count()==0
 assert p.evaluate(api+'.state().id')==10011
 assert p.evaluate(api+'.state().favorite') is False
 assert p.evaluate(api+'.change(10011,"favorites",true)') is True
 assert p.evaluate(api+'.change(10011,"locked",true)') is True
 assert p.evaluate(api+'.state().favorite') is True
 assert p.evaluate(api+'.state().locked') is True
 assert p.locator('[data-bf-unit-id="10011"]').get_attribute('data-bf-qol-favorite')=='true'
 first=p.locator('#bf-home .bf-scene-member').first
 assert first.locator('.bf-home-unit-flags').count()==1
 assert first.locator('.bf-home-unit-flags').get_attribute('aria-label')=='Favorite and Advisory lock'
 assert '★' in first.inner_text() and '🔒' in first.inner_text()
 assert p.locator('#bf-home .bf-scene-member').nth(1).locator('.bf-home-unit-flags').count()==0
 p.locator('[data-bf-unit-id="20011"]').click()
 p.wait_for_function("BFGlobalQoLUnitFlagsV10200.state().id===20011")
 assert p.evaluate(api+'.change(20011,"favorites",true)') is True
 assert p.evaluate(api+'.favorites')==[10011,20011]
 assert p.locator('#bf-home .bf-scene-member').nth(1).locator('.bf-home-unit-flags').get_attribute('aria-label')=='Favorite'
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
 p.evaluate(api+'.refresh()')
 assert p.locator('#bf-home .bf-scene-member').first.locator('.bf-home-unit-flags').count()==0
 p.evaluate('P.roster=[10011,20011]')
 p.evaluate(api+'.refresh()')
 assert p.locator('#bf-home .bf-scene-member').first.locator('.bf-home-unit-flags').count()==1
 # Home squad cards are reconstructed after real squad changes. Observe
 # direct child replacement and restore the same existing advisory badges.
 p.evaluate("""() => {
   const party=document.getElementById('bf-scene-party');
   party.replaceChildren(...[10011,20011].map(id=>{
     const node=document.createElement('div');
     node.className='bf-scene-member';
     node.textContent='Unit '+id;
     return node;
   }));
 }""")
 p.wait_for_function("document.querySelectorAll('#bf-home .bf-home-unit-flags').length===2")
 assert p.locator('#bf-home .bf-scene-member').first.locator('.bf-home-unit-flags').count()==1
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==original
 assert p.evaluate(api+'.state().advisoryOnly') is True
 p.add_script_tag(path=str(A/'bf10200_qol_unit_flags.js'))
 assert p.locator('#bf10200-flags').count()==1
 assert not errors,errors
 b.close()
print('PASS v102 unit marker persistence, owned-only toggles, advisory scope and save isolation')
