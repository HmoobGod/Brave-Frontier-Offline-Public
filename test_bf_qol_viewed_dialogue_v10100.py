"""v101 source-only viewed dialogue skip does not mutate v7 save."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf10100_qol_viewed_dialogue.js').read_text('utf8')
assert src.count('BF_GLOBAL_QOL_VIEWED_DIALOGUE_SKIP_V10100')==1
assert len(src.encode())<65536
assert 'timeline.jump(s.lines)' in src and 'playback.pause()' in src
assert 'sourceBound(s)' in src and "row.source==='content/event/'+s.source" in src
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
       {kind,id,source:'content/event/map1-dungeon1.txt',lines:['A','B','C']}:null
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
 # Real public API contract, not only a hand-authored lookup stub:
 # the v2200 reader's lookup returns source='content/event/'+filename,
 # while snapshot().source carries only the bare filename.
 real=b.new_page(viewport={'width':390,'height':844})
 real_errors=[];real.on('pageerror',lambda e:real_errors.append(str(e)))
 real.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{
   configurable:true,value:{getItem:k=>db[k]??null,
   setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
   key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 real.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 real.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js',
              'bf090_st_lamia_map.js','bf100_grand_gaia_campaign.js',
              'bf101_story_continue.js','bf110_quest_journal.js',
              'bf2000_story_battle_hud.js','bf2100_battle_command_tray.js',
              'bf2200_original_event_reader.js'):
  real.add_script_tag(path=str(A/name))
 real.evaluate("""()=>{window.__realPaused=0;
   window.BFGlobalStoryPlaybackV3300={pause:()=>{__realPaused++}};
   window.BFGlobalDialogueTimelineV3500={jump:n=>{
     const api=BFGlobalOriginalEventsV2200;
     const initial=api.snapshot();
     if(!document.getElementById('bf2200-reader').open||
        !Number.isInteger(n)||n<1||n>initial.lines)return false;
     const next=document.getElementById('bf2200-next');
     while(api.snapshot().step<n){
       if(next.disabled)return false;
       next.click();
     }
     return api.snapshot().step===n;
   }};
 }""")
 assert real.evaluate('P.version')==7
 real.evaluate('()=>{P.questClears[10]=1;P.questClears[12]=1;renderQuestList()}')
 assert real.evaluate('BFGlobalOriginalEventsV2200.read("clear",10)') is True
 contract=real.evaluate("""()=>({
   row:BFGlobalOriginalEventsV2200.lookup('clear',10),
   snapshot:BFGlobalOriginalEventsV2200.snapshot()
 })""")
 assert contract['row']['source']=='content/event/'+contract['snapshot']['source'],contract
 assert 'name' not in contract['row'],contract
 real_save=real.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 real.add_script_tag(path=str(A/'bf10100_qol_viewed_dialogue.js'))
 assert real.evaluate(api+'.state().sourceVerified') is True
 assert real.evaluate(api+'.observed()') is False or real.evaluate(api+'.state().storedCount')==1
 assert real.evaluate(api+'.state().storedCount')==1
 assert real.evaluate(api+'.viewed')==['clear:10']
 # Original multi-page dungeon reader must complete, remember and
 # subsequently skip using the real public row lookup contract.
 assert real.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 assert real.evaluate(api+'.state().sourceVerified') is True
 assert real.evaluate(api+'.state().viewed') is False
 real.evaluate("""()=>{const a=BFGlobalOriginalEventsV2200,
   next=document.getElementById('bf2200-next');
   while(!next.disabled)next.click();}""")
 real.wait_for_function("BFGlobalQoLViewedDialogueV10100.state().viewed")
 assert 'dungeon:20' in real.evaluate(api+'.viewed')
 assert real.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 assert real.evaluate(api+'.state().available') is True
 assert real.evaluate(api+'.skip()') is True
 assert real.evaluate(api+'.state().step')==real.evaluate(api+'.state().lines')
 assert real.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==real_save
 assert not real_errors,real_errors
 real.close()
 b.close()
print('PASS v101 viewed-only dialogue skip, replay and v7 save immutability')
