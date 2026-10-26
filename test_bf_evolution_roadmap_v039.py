"""v0.39 source-verified Evolution Roadmap, save-isolation and UI smoke test."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent; A=ROOT/'app/src/main/assets'
html=(A/'index.html').read_text('utf-8')
assert html.count('/* BF_EVOLUTION_ROADMAP_V039 */')==1
assert html.count('id="bf039-evo-roadmap-style"')==1
assert 'bf_global_offline_demo_v7' in html
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  from urllib.parse import urlsplit
  p=(A/urlsplit(route.request.url).path.lstrip('/')).resolve()
  if not p.is_relative_to(A.resolve()) or not p.is_file():route.fulfill(status=404,body=b'');return
  route.fulfill(status=200,content_type='image/png' if p.suffix=='.png' else 'text/plain',body=p.read_bytes())
 page.route('http://bf-assets.test/**',serve)
 page.evaluate("""()=>{const d={};window.__v39store=d;
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem(k){return d[k]??null},setItem(k,v){d[k]=String(v)},removeItem(k){delete d[k]},
    key(i){return Object.keys(d)[i]??null},get length(){return Object.keys(d).length}
   }});window.confirm=()=>true;window.alert=()=>{}}""")
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 page.evaluate("""()=>{BF_debug.reset();P.roster=[10021];P.squad=[10021];
   P.evolutions={'10021':10024};P.unitExp[10021]=100;P.zel=15000;
   P.materials={'10132':1,'10133':0,'50354':0,'60144':0,'60224':0};
   saveProgress();renderEvolutionPanel()}""")
 page.wait_for_function("""()=>!!document.getElementById('bf-evolution-roadmap-v039')""")
 page.evaluate("""()=>{document.getElementById('bf-evolution-roadmap-v039').open=true}""")
 page.wait_for_function("""()=>document.querySelector('#bf-evolution-roadmap-v039 select')?.value==='10021'""")
 info=page.evaluate("""()=>({
   p:BF_EvolutionRoadmapV039.plan(10021),
   text:document.querySelector('#bf-evolution-roadmap-v039').textContent,
   save:window.__v39store['bf_global_offline_demo_v7'],
   version:P.version, forms:window.BF_EVOLVED_UNITS.length
 })""")
 assert info['version']==7 and info['forms']==54,info
 assert info['p']['target']['id']==10025 and info['p']['demoZel']==10000,info
 assert info['p']['archivedZel']==500000 and len(info['p']['materials'])==5,info
 assert sorted(m['itemId'] for m in info['p']['materials'] if m['missing'])==['10133','50354','60144','60224'],info
 assert 'Inferno Beast Zegar' in info['text'] and 'Material #50354' in info['text'] and '500,000' in info['text'],info
 assert (window_save := info['save'])
 page.evaluate("""()=>{P.roster=[10021,10011];P.evolutions[10021]=10025;renderEvolutionPanel()}""")
 # Reopen guide when the Evolution Lab recreates its cards.
 page.wait_for_function("""()=>!!document.getElementById('bf-evolution-roadmap-v039')""")
 page.evaluate("""()=>{document.getElementById('bf-evolution-roadmap-v039').open=true}""")
 page.wait_for_function("""()=>document.getElementById('bf-evolution-roadmap-v039').textContent.includes('no further evolution')""")
 after=page.evaluate("""()=>({save:window.__v39store['bf_global_offline_demo_v7'],
   text:document.getElementById('bf-evolution-roadmap-v039').textContent})""")
 assert window_save==after['save'],"Guide must never modify persisted v7 save"
 assert not errors,errors
 browser.close()
print('PASS v0.39 Roadmap: next 6-star target, exact material deficits, archived/demo costs, max stage and unchanged v7')
