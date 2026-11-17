"""v632: real packaged Home button must honor the story action actually displayed.
Playwright Chromium; isolated in-memory canonical v7 only; no owner save or APK.
"""
from pathlib import Path
import shutil, sys
R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
JS=(A/"bf_home_nav.js").read_text("utf8")
BUILD=(R/".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE=(R/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
NAME="test_bf_home_story_action_identity_v63200.py"
assert JS.count("// v632: a rendered VIEW QUESTS button") == 1
assert "const selectShown=shown!==null&&desired===shown" in JS
assert "if(selectShown&&safeNextStoryMission()===shown)" in JS
assert "displayedNextStoryMission=safeNextStoryMission()" in JS
assert BUILD.count("python3 "+NAME)==1 and PRE.count(NAME)==2
assert "android.permission.INTERNET" not in (A.parent/"AndroidManifest.xml").read_text()
assert len(JS.encode("utf8"))<128*1024
print("PASS v632 source: visible manual story action identity and signed registration")
if "--source-only" in sys.argv:raise SystemExit(0)
from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome,"Real Chromium required"
MODULES=("bf_home_nav.js","bf080_morgan_map.js","bf090_st_lamia_map.js",
    "bf100_grand_gaia_campaign.js","bf101_story_continue.js",
    "bf14300_original_quest_energy.js")
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=chrome,
   args=["--no-sandbox","--disable-dev-shm-usage"])
 try:
  for width in (320,359,393,412,540):
   for mode in ("view-then-select","select-then-view","baseline"):
    page=browser.new_page(viewport={"width":width,"height":844})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    try:
     page.evaluate("""() => {
        const db={};let writes=0;
        Object.defineProperty(window,'localStorage',{configurable:true,value:{
         getItem:k=>db[k]??null,setItem:(k,v)=>{writes++;db[k]=String(v)},
         removeItem:k=>{writes++;delete db[k]},
         key:i=>Object.keys(db)[i]??null,
         get length(){return Object.keys(db).length}
        }});
        window.__v632writes=()=>writes;window.alert=()=>{};window.confirm=()=>true;
        HTMLMediaElement.prototype.load=()=>{};
        HTMLMediaElement.prototype.pause=()=>{};
        HTMLMediaElement.prototype.play=()=>Promise.resolve();
     }""")
     page.set_content((A/"index.html").read_text("utf8"),wait_until="load",timeout=90000)
     page.add_style_tag(path=str(A/"bf_home_nav.css"))
     for mod in MODULES:page.add_script_tag(path=str(A/mod))
     assert page.evaluate("P.version")==7
     result=page.evaluate("""mode=>{
       const nav=BF_homeNav,api=BFGrandGaiaContinueV101;
       if(nav.current!=='home')throw Error('Home route not available');
       S.mode='archive';S.busy=false;S.over=false;S.auto=false;
       if(Array.isArray(S.party))for(const p of S.party)if(p)p.action=null;
       api.refresh();BFGlobalHome.refreshStory();
       const button=document.getElementById('bf-home-story-open');
       if(button.textContent!=='SELECT NEXT STORY ›')throw Error('No initial select action');
       let original,mutated;
       if(mode==='view-then-select'){
         S.auto=true;api.refresh();BFGlobalHome.refreshStory();
         if(button.textContent!=='VIEW QUESTS ›')throw Error('View action not displayed');
         S.auto=false;api.refresh();
       }else if(mode==='select-then-view'){
         S.auto=true;api.refresh();
       }
       const displayed=button.textContent;
       const native=document.getElementById('bf101-continue');
       let calls=0;
       native.addEventListener('click',()=>calls++);
       const snapshot=()=>JSON.stringify({P,S,QUEST,
          writes:__v632writes(),keys:Array.from({length:localStorage.length},(_,i)=>{
            const k=localStorage.key(i);return [k,localStorage.getItem(k)]
          }).sort((a,b)=>a[0].localeCompare(b[0]))});
       const prior=snapshot(),player=JSON.stringify(P);
       button.click();
       return {route:nav.current,displayed,calls,unchanged:snapshot()===prior,
         playerSame:JSON.stringify(P)===player,auto:S.auto,
         stored:localStorage.getItem('bf_global_offline_demo_v7'),
         overflow:document.documentElement.scrollWidth>innerWidth+1};
     }""",mode)
     assert result["route"]=="quest" and not result["overflow"],(width,mode,result)
     if mode=="baseline":
      assert result["displayed"]=="SELECT NEXT STORY ›",result
      assert result["calls"]==1 and result["auto"] is False and result["playerSame"],result
     else:
      assert result["calls"]==0 and result["unchanged"],(width,mode,result)
      if mode=="view-then-select":assert result["displayed"]=="VIEW QUESTS ›",result
      else:assert result["displayed"]=="SELECT NEXT STORY ›",result
     assert not errors,(width,mode,errors[:3])
     print("PASS v632 actual Home",width,mode)
    finally:page.close()
 finally:browser.close()
print("PASS v632: 15 real manual Home action identity cases; blocked cases have no owner writes")
