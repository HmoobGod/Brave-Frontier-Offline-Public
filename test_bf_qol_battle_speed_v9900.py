"""v99: fast speed options, optional animation wait cap and v7 save isolation."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf9900_qol_battle_speed.js').read_text('utf8')
assert js.count('BF_GLOBAL_QOL_BATTLE_SPEED_V9900')==1
assert len(js.encode())<65536
assert 'window.wait=function(ms)' in js
assert 'nativeWait.call(this,40)' in js
assert "S.mode!=='archive'" in js
assert 'saveProgress(' not in js and 'awardDemoRewards(' not in js
assert 'if(S.busy)return false;' in js
assert 'if(S.busy||!allowed.has(speed.value))' in js and 'speed.value=confirmedSpeed' in js
assert 'control.disabled=!!S.busy;' in js
assert js.count('min-height:44px')>=2
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
    const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
    removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
    get length(){return Object.keys(db).length}}});
 }""")
 p.set_content("""<html><body><div id="bf2000-run"></div>
   <select id="speed"><option value="1">1x</option>
   <option value="2" selected>2x</option><option value="3">3x</option>
   <option value="5">5x</option></select></body></html>""")
 p.evaluate("""()=>{
   window.P={version:7,roster:[],squad:[],questClears:{}};
   window.S={mode:'archive',busy:false};
   window.E={speed:document.getElementById('speed')};
   window.wait=ms=>new Promise(resolve=>setTimeout(resolve,Math.max(0,ms)));
   localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
 }""")
 saved=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.add_script_tag(path=str(A/'bf9900_qol_battle_speed.js'))
 api='BFGlobalQoLBattleSpeedV9900'
 assert p.evaluate(api+'.snapshot().originalOptions')==['1','2','3','5']
 assert p.evaluate(api+'.snapshot().extra')==[8,12]
 assert p.locator('#speed option').count()==6
 assert p.locator('#bf9900-speed-select option').count()==6
 assert p.evaluate(api+'.snapshot().speed')==2
 assert p.evaluate(api+'.snapshot().skip') is False
 # The optional controls must meet minimum touch sizes at narrow widths.
 p.locator('#bf9900-speed summary').click()
 for width in (320,390,540):
  p.set_viewport_size({'width':width,'height':844})
  for selector in ('#bf9900-speed summary','#bf9900-speed-select'):
   rect=p.locator(selector).bounding_box()
   assert rect and rect['height']>=44,(width,selector,rect)
 p.set_viewport_size({'width':390,'height':844})
 assert p.evaluate(api+'.setSpeed(9)') is False
 assert p.evaluate(api+'.setSpeed(12)') is True
 assert p.evaluate("document.getElementById('speed').value")=='12'
 assert p.evaluate("localStorage.getItem('bf_global_offline_qol_speed_v99')")=='12'
 assert p.evaluate(api+'.setSkip(true)') is True
 assert p.evaluate(api+'.snapshot().skip') is True
 assert p.evaluate("localStorage.getItem('bf_global_offline_qol_skip_animations_v99')")=='on'
 fast=p.evaluate("""async()=>{const t=performance.now();await window.wait(250);
    return performance.now()-t;}""")
 assert 25<=fast<170,fast
 # Skip presentation waits only in archive combat, not training.
 p.evaluate("S.mode='training'")
 normal=p.evaluate("""async()=>{const t=performance.now();await window.wait(125);
    return performance.now()-t;}""")
 assert normal>=95,normal
 p.evaluate("""()=>{S.mode='archive';S.busy=true;BFGlobalQoLBattleSpeedV9900.refresh()}""")
 assert p.locator('#bf9900-speed-select').is_disabled()
 assert p.locator('#bf9900-anim-skip').is_disabled()
 assert p.evaluate(api+'.setSpeed(5)') is False
 # A queued stale DOM event during a busy turn must restore the true speed.
 p.evaluate("""()=>{const c=document.getElementById('bf9900-speed-select');
   c.value='5';c.dispatchEvent(new Event('change',{bubbles:true}))}""")
 assert p.evaluate("document.getElementById('speed').value")=='12'
 assert p.evaluate("document.getElementById('bf9900-speed-select').value")=='12'
 assert p.evaluate("localStorage.getItem('bf_global_offline_qol_speed_v99')")=='12'
 assert p.evaluate(api+'.setSkip(false)') is False
 assert p.evaluate(api+'.snapshot().skip') is True
 # v453: a stale stock/native speed change event must not bypass the
 # same busy-turn lock that protects the optional QoL select.
 p.evaluate("""()=>{const native=document.getElementById('speed');
   native.value='5';native.dispatchEvent(new Event('change',{bubbles:true}));}""")
 assert p.evaluate("document.getElementById('speed').value")=='12'
 assert p.evaluate("document.getElementById('bf9900-speed-select').value")=='12'
 assert p.evaluate("localStorage.getItem('bf_global_offline_qol_speed_v99')")=='12'
 assert p.evaluate(api+'.snapshot().speed')==12
 p.evaluate("S.busy=false;BFGlobalQoLBattleSpeedV9900.refresh()")
 assert p.locator('#bf9900-speed-select').is_enabled()
 # Normal stock speed changes between turns remain functional and persistent.
 p.evaluate("""()=>{const native=document.getElementById('speed');
   native.value='5';native.dispatchEvent(new Event('change',{bubbles:true}));}""")
 assert p.evaluate("document.getElementById('bf9900-speed-select').value")=='5'
 assert p.evaluate("localStorage.getItem('bf_global_offline_qol_speed_v99')")=='5'
 assert p.evaluate(api+'.snapshot().speed')==5
 # Tampered/unknown native values cannot be persisted or shown as valid.
 p.evaluate("""()=>{const native=document.getElementById('speed');
   const extra=document.createElement('option');extra.value='99';native.append(extra);
   native.value='99';native.dispatchEvent(new Event('change',{bubbles:true}));
   extra.remove();}""")
 assert p.evaluate("document.getElementById('speed').value")=='5'
 assert p.evaluate("document.getElementById('bf9900-speed-select').value")=='5'
 assert p.evaluate("localStorage.getItem('bf_global_offline_qol_speed_v99')")=='5'
 assert p.evaluate(api+'.setSkip(false)') is True
 normal2=p.evaluate("""async()=>{const t=performance.now();await window.wait(125);
    return performance.now()-t;}""")
 assert normal2>=95,normal2
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==saved
 assert p.evaluate("P.version")==7
 p.add_script_tag(path=str(A/'bf9900_qol_battle_speed.js'))
 assert p.locator('#bf9900-speed').count()==1
 assert p.locator('#speed option').count()==6
 assert not errors,errors
 b.close()
print('PASS v99 extended round speed and animation skip are optional, save-safe, archive-only and idempotent')

if __name__ == '__main__':
 import subprocess,sys
 subprocess.run([sys.executable,str(R/'test_bf_hidden_battle_render.py')],check=True)
