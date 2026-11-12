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
 p.set_content('<html><body><section id="bf-home"><section class="bf-scene-tools"></section></section><section id="bf101-story-continue"></section></body></html>')
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011],squad:[10011],questClears:{1:1}};
   window.__routes404=[];
   window.BF_homeNav={go:r=>{window.__routes404.push(r);return r==='quest'}};
   localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
   window.BFAndroid={exportSaveFile:(raw,name)=>{window.__export97={raw,name}}};
 }""")
 initial=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.add_script_tag(path=str(asset))
 api='BFGlobalQoLBackupsV9700'
 assert p.evaluate(api+'.enabled') is True
 assert p.evaluate(api+'.listing().length')==1
 assert p.locator('#bf9700-backups').count()==1
 assert p.locator('#bf9700-home-status').count()==1
 assert '1/3 verified snapshots' in p.locator('#bf9700-home-count').inner_text()
 assert 'Auto ON' in p.locator('#bf9700-home-count').inner_text()
 assert p.locator('#bf9700-auto').is_checked()
 # Home only navigates to the EXISTING backup manager on user click;
 # it must never export or capture the live save as a shortcut side effect.
 home_snapshot=p.evaluate("""() => ({
   live:localStorage.getItem('bf_global_offline_demo_v7'),
   backups:localStorage.getItem(BFGlobalQoLBackupsV9700.key)})""")
 p.locator('#bf9700-home-manage').click()
 assert p.evaluate('window.__routes404')==['quest']
 assert p.locator('#bf9700-backups').get_attribute('open') is not None
 assert p.evaluate('window.__export97') is None
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==home_snapshot['live']
 assert p.evaluate("localStorage.getItem(BFGlobalQoLBackupsV9700.key)")==home_snapshot['backups']
 p.set_viewport_size({'width':320,'height':844})
 box=p.locator('#bf9700-home-manage').evaluate("""el => {
   const r=el.getBoundingClientRect(),host=el.parentElement.getBoundingClientRect();
   return {inside:r.left>=host.left-.5&&r.right<=host.right+.5&&
     r.left>=0&&r.right<=innerWidth,large:r.height>=44,
     page:document.documentElement.scrollWidth<=innerWidth};
 }""")
 assert box=={'inside':True,'large':True,'page':True},box
 p.set_viewport_size({'width':390,'height':844})
 p.evaluate("document.getElementById('bf9700-backups').open=false")
 assert p.evaluate(api+'.capture()') is False
 for n in [2,3,4]:
  p.evaluate("""n=>{
    P.questClears[1]=n;
    localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
  }""",n)
  assert p.evaluate(api+'.capture()') is True
 assert p.evaluate(api+'.listing().length')==3
 assert '3/3 verified snapshots' in p.locator('#bf9700-home-count').inner_text()
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
 p.locator('#bf9700-backups > summary').click()
 assert p.locator('#bf9700-backups').get_attribute('open') is not None
 p.locator('#bf9700-export').click()
 exported=p.evaluate('window.__export97')
 assert exported['name'].startswith('BraveFrontier-v7-backup-')
 assert exported['name'].endswith('.json')
 assert __import__('json').loads(exported['raw'])['questClears']['1']==4
 # v164: the one-tap CURRENT export must read the exact canonical save, not
 # the last rotating snapshot (which can lag behind real gameplay).
 assert p.locator('#bf9700-export-current').count()==1
 # The preceding corruption test deliberately left an invalid live save.
 # Restore the in-memory valid player state before exercising live export.
 p.evaluate("localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P))")
 previous_raw=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 previous_backups=p.evaluate("localStorage.getItem(BFGlobalQoLBackupsV9700.key)")
 p.evaluate("""()=>{
   const v=JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'));
   v.questClears['12']=1;
   v._bfGemV160={schema:1,balance:0,paidFinales:[],legacyFinales:[12]};
   v._bfGemV161Pending=[12];
   localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(v));
 }""")
 exact_current=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.locator('#bf9700-export-current').click()
 current_export=p.evaluate('window.__export97')
 assert current_export['raw']==exact_current
 assert current_export['name'].startswith('BraveFrontier-v7-current-')
 assert current_export['name'].endswith('.json')
 assert __import__('json').loads(current_export['raw'])['_bfGemV161Pending']==[12]
 assert __import__('json').loads(current_export['raw'])['_bfGemV160']['balance']==0
 assert p.evaluate("localStorage.getItem(BFGlobalQoLBackupsV9700.key)")==previous_backups
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==exact_current
 p.evaluate("""()=>localStorage.setItem('bf_global_offline_demo_v7','{"version":7,"roster":null}')""")
 assert p.evaluate('BFGlobalQoLBackupsV9700.exportCurrent()') is False
 assert p.evaluate('window.__export97')==current_export
 p.evaluate("raw=>localStorage.setItem('bf_global_offline_demo_v7',raw)",previous_raw)
 p.locator('#bf9700-auto').uncheck()
 assert p.evaluate(api+'.enabled') is False
 assert 'Auto OFF' in p.locator('#bf9700-home-count').inner_text()
 assert p.evaluate("localStorage.getItem('bf_global_offline_qol_backups_enabled_v97')")=='off'
 p.evaluate("localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P))")
 assert p.evaluate(api+'.capture()') is False
 # Manual snapshot remains usable with background collection paused.
 p.evaluate("""()=>{P.questClears[1]=5;localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));}""")
 p.locator('#bf9700-capture').click()
 assert p.evaluate("JSON.parse(JSON.parse(localStorage.getItem(BFGlobalQoLBackupsV9700.key)).slots[0].raw).questClears[1]")==5
 # Re-enable catches up without wiping stored snapshots.
 p.locator('#bf9700-auto').check()
 assert p.evaluate(api+'.enabled') is True
 assert 'Auto ON' in p.locator('#bf9700-home-count').inner_text()
 assert p.evaluate(api+'.listing().length')==3
 assert p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_demo_v7')).version")==7
 # A previously saved state can become current again after an export/import
 # or a user restoring an older snapshot. Its bytes must not waste a slot.
 p.evaluate("""() => {
   const a=BFGlobalQoLBackupsV9700;
   P.questClears[1]=10;
   const raw=JSON.stringify(P);
   localStorage.setItem(a.liveKey,raw);
   localStorage.setItem(a.key,JSON.stringify({version:1,
      slots:[{time:1001,raw}]}));
 }""")
 for n in [11,10]:
  p.evaluate("""n=>{
    const a=BFGlobalQoLBackupsV9700;
    P.questClears[1]=n;
    localStorage.setItem(a.liveKey,JSON.stringify(P));
  }""",n)
  before_live=p.evaluate("localStorage.getItem(BFGlobalQoLBackupsV9700.liveKey)")
  assert p.evaluate(api+'.capture()') is True
  assert p.evaluate("localStorage.getItem(BFGlobalQoLBackupsV9700.liveKey)")==before_live
 assert p.evaluate("""()=>{
   const a=BFGlobalQoLBackupsV9700;
   const slots=JSON.parse(localStorage.getItem(a.key)).slots;
   return slots.map(x=>JSON.parse(x.raw).questClears[1]);
 }""")==[10,11]
 assert p.evaluate(api+'.listing().length')==2
 assert '2/3 distinct saved snapshots' in p.locator('#bf9700-status').text_content()
 # Older valid backup histories may already contain duplicate raw values.
 # Reading/refreshing deduplicates presentation without rewriting them.
 p.evaluate("""()=>{
   const a=BFGlobalQoLBackupsV9700,raw=localStorage.getItem(a.liveKey);
   const other=JSON.stringify({...P,questClears:{1:11}});
   localStorage.setItem(a.key,JSON.stringify({version:1,slots:[
     {time:1003,raw},{time:1002,raw},{time:1001,raw:other}]}));
 }""")
 original_duplicate=p.evaluate("localStorage.getItem(BFGlobalQoLBackupsV9700.key)")
 assert p.evaluate(api+'.refresh().length')==2
 assert p.evaluate("localStorage.getItem(BFGlobalQoLBackupsV9700.key)")==original_duplicate
 p.evaluate("""()=>{
   const a=BFGlobalQoLBackupsV9700;
   P.questClears[1]=12;localStorage.setItem(a.liveKey,JSON.stringify(P));
 }""")
 assert p.evaluate(api+'.capture()') is True
 assert p.evaluate("""()=>{
   const a=BFGlobalQoLBackupsV9700;
   return JSON.parse(localStorage.getItem(a.key)).slots
      .map(x=>JSON.parse(x.raw).questClears[1]);
 }""")==[12,10,11]
 p.add_script_tag(path=str(asset))
 assert p.locator('#bf9700-backups').count()==1
 assert not errors,errors
 b.close()
print('PASS v97 rotating backups: dedupe/3 slots/corrupt rejection/opt-out/export/v7 isolation')
