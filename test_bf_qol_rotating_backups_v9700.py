"""v97 QoL: rotating valid offline v7 snapshots, opt-out, manual export."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
asset=ROOT/'app/src/main/assets/bf9700_qol_rotating_backups.js'
src=asset.read_text('utf8')
java=(ROOT/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('BF_GLOBAL_QOL_ROTATING_BACKUPS_V9700')==1
assert len(src.encode())<65536
assert 'bf_global_offline_demo_v7' in src
assert "localStorage.setItem(liveKey" not in src
assert "localStorage.removeItem(liveKey" not in src
assert 'BFAndroid?.exportSaveFile' in src
assert 'readPackagedText("bf9700_qol_rotating_backups.js")' in java

with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
   const db={};window.__storage97=db;
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
    removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
    get length(){return Object.keys(db).length}}});
 }""")
 p.set_content('<html><body><section id="bf101-story-continue"></section></body></html>')
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011],squad:[10011],questClears:{1:1}};
   localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
   window.BFAndroid={exportSaveFile:(raw,name)=>{window.__export97={raw,name}}};
 }""")
 initial=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.add_script_tag(path=str(asset))
 api='BFGlobalQoLBackupsV9700'
 assert p.evaluate(api+'.enabled') is True
 assert p.evaluate(api+'.listing().length')==1
 assert p.locator('#bf9700-backups').count()==1
 assert p.locator('#bf9700-auto').is_checked()
 assert p.evaluate(api+'.capture()') is False
 for n in [2,3,4]:
  p.evaluate("""n=>{
    P.questClears[1]=n;
    localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
  }""",n)
  assert p.evaluate(api+'.capture()') is True
 assert p.evaluate(api+'.listing().length')==3
 assert p.evaluate("""()=>{
   const data=JSON.parse(localStorage.getItem(BFGlobalQoLBackupsV9700.key));
   return data.slots.map(x=>JSON.parse(x.raw).questClears[1]);
 }""")==[4,3,2]
 # Malformed/corrupted save is never backed up over valid snapshots.
 before=p.evaluate("localStorage.getItem(BFGlobalQoLBackupsV9700.key)")
 p.evaluate("localStorage.setItem('bf_global_offline_demo_v7','{\"version\":7,\"roster\":null}')")
 assert p.evaluate(api+'.capture()') is False
 assert p.evaluate("localStorage.getItem(BFGlobalQoLBackupsV9700.key)")==before
 # A backup is exported only on an explicit tap.
 assert p.evaluate("window.__export97") is None
 p.locator('#bf9700-export').click()
 exported=p.evaluate('window.__export97')
 assert exported['name'].startswith('BraveFrontier-v7-backup-')
 assert exported['name'].endswith('.json')
 assert __import__('json').loads(exported['raw'])['questClears']['1']==4
 p.locator('#bf9700-auto').uncheck()
 assert p.evaluate(api+'.enabled') is False
 assert p.evaluate("localStorage.getItem('bf_global_offline_qol_backups_enabled_v97')")=='off'
 p.evaluate("localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P))")
 assert p.evaluate(api+'.capture()') is False
 # Manual snapshot remains usable with background collection paused.
 p.evaluate("P.questClears[1]=5;localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P))")
 p.locator('#bf9700-capture').click()
 assert p.evaluate("JSON.parse(JSON.parse(localStorage.getItem(BFGlobalQoLBackupsV9700.key)).slots[0].raw).questClears[1]")==5
 # Re-enable catches up without wiping stored snapshots.
 p.locator('#bf9700-auto').check()
 assert p.evaluate(api+'.enabled') is True
 assert p.evaluate(api+'.listing().length')==3
 assert p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_demo_v7')).version")==7
 p.add_script_tag(path=str(asset))
 assert p.locator('#bf9700-backups').count()==1
 assert not errors,errors
 b.close()
print('PASS v97 rotating backups: dedupe/3 slots/corrupt rejection/opt-out/export/v7 isolation')
