"""v101 source-only viewed dialogue skip does not mutate v7 save."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf10100_qol_viewed_dialogue.js').read_text('utf8')
assert src.count('BF_GLOBAL_QOL_VIEWED_DIALOGUE_SKIP_V10100')==1
assert len(src.encode())<65536
assert 'timeline.jump(s.lines)' in src and 'playback.pause()' in src
assert 'sourceBound(s)' in src and 'row.name===s.source' in src
assert 'min-height:44px' in src
assert "saveProgress(" not in src and "bf_global_offline_demo_v7" not in src
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
 p.set_content("""<html><body><details id="bf2200-reader" open><summary>Story</summary>
 <select id="bf2200-scenes"><option>dungeon:20</option></select>
 <div id="bf2200-nav"><button id="bf2200-next">Next</button></div>
 <div id="bf2200-text">First line</div></details></body></html>""")
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011],squad:[10011],questClears:{}};
   localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
   window.__scene101={chosen:'dungeon:20',source:'map1-dungeon1.txt',lines:3,step:1};
   window.__paused101=0;
   const t=document.getElementById('bf2200-text');
   document.getElementById('bf2200-next').addEventListener('click',()=>{
     if(__scene101.step<__scene101.lines){__scene101.step++;t.textContent='Page '+__scene101.step;}
   });
   window.BFGlobalOriginalEventsV2200={
     snapshot:()=>({...__scene101}),
     lookup:(kind,id)=>kind==='dungeon'&&id===20?
       {kind,id,name:'map1-dungeon1.txt',lines:['A','B','C']}:null
   };
   window.BFGlobalStoryPlaybackV3300={pause:()=>{__paused101++}};
   window.BFGlobalDialogueTimelineV3500={jump:n=>{
     if(n<1||n>__scene101.lines||!document.getElementById('bf2200-reader').open)return false;
     __scene101.step=n;t.textContent='Page '+n;return true;
   }};
 }""")
 original=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.add_script_tag(path=str(A/'bf10100_qol_viewed_dialogue.js'))
 api='BFGlobalQoLViewedDialogueV10100'
 assert p.locator('#bf10100-viewed-dialogue').count()==1
 assert p.evaluate(api+'.state().viewed') is False
 assert p.evaluate(api+'.skip()') is False
 # A corrupted reader snapshot must never mark an incomplete script as
 # previously viewed. This includes forged page counts and scene identity.
 original_marker=p.evaluate("localStorage.getItem('bf_global_offline_qol_viewed_scenes_v101')")
 for change in (
    "__scene101.lines=1;__scene101.step=1",
    "__scene101.source='unexpected.txt';__scene101.step=3",
    "__scene101.step='3'",
    "__scene101.chosen='dungeon:30';__scene101.step=3",
    "__scene101.lines=3.5;__scene101.step=3.5",
 ):
  p.evaluate(change)
  assert p.evaluate(api+'.observed()') is False,change
  assert p.evaluate(api+'.state().sourceVerified') is False,change
  assert p.evaluate(api+'.state().storedCount')==0,change
  assert p.evaluate("localStorage.getItem('bf_global_offline_qol_viewed_scenes_v101')")==original_marker,change
  p.evaluate("(s)=>{Object.assign(__scene101,s)}",{"chosen":"dungeon:20","source":"map1-dungeon1.txt","lines":3,"step":1})
 assert p.evaluate(api+'.state().sourceVerified') is True
 p.locator('#bf2200-next').click()
 assert p.evaluate(api+'.state().step')==2
 assert p.evaluate(api+'.state().viewed') is False
 p.locator('#bf2200-next').click()
 p.wait_for_function("BFGlobalQoLViewedDialogueV10100.state().viewed")
 assert p.evaluate(api+'.state().storedCount')==1
 assert p.evaluate(api+'.viewed')==['dungeon:20']
 for width in (320,390,540):
  p.set_viewport_size({'width':width,'height':844})
  rect=p.locator('#bf10100-skip').bounding_box()
  assert rect and rect['height']>=44,(width,rect)
 p.set_viewport_size({'width':390,'height':844})
 p.evaluate("""()=>{
   __scene101.step=1;
   document.getElementById('bf2200-text').textContent='First line again';
 }""")
 # A previously viewed marker must not authorize jumping a mismatched
 # or corrupt current scene; the existing valid marker remains intact.
 stable=p.evaluate("localStorage.getItem('bf_global_offline_qol_viewed_scenes_v101')")
 start_pause=p.evaluate('window.__paused101')
 start_step=p.evaluate('__scene101.step')
 for change in ("__scene101.source='tampered.txt'",
                "__scene101.lines=2",
                "__scene101.step='1'",
                "__scene101.chosen='dungeon:30'"):
  p.evaluate(change)
  assert p.evaluate(api+'.state().sourceVerified') is False,change
  assert p.evaluate(api+'.skip()') is False,change
  assert p.evaluate('window.__paused101')==start_pause,change
  assert p.evaluate("localStorage.getItem('bf_global_offline_qol_viewed_scenes_v101')")==stable,change
  p.evaluate("()=>{__scene101.source='map1-dungeon1.txt';__scene101.lines=3;__scene101.step=1;__scene101.chosen='dungeon:20'}")
 assert p.evaluate(api+'.state().step')==start_step
 assert p.evaluate(api+'.skip()') is True
 assert p.evaluate(api+'.state().step')==3
 assert p.evaluate('window.__paused101')==1
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==original
 p.add_script_tag(path=str(A/'bf10100_qol_viewed_dialogue.js'))
 assert p.locator('#bf10100-viewed-dialogue').count()==1
 assert p.evaluate(api+'.remember("clear:999")') is False
 assert p.evaluate(api+'.remember("__proto__")') is False
 assert p.evaluate(api+'.state().storedCount')==1
 assert not errors,errors
 b.close()
print('PASS v101 viewed-only dialogue skip, replay and v7 save immutability')
