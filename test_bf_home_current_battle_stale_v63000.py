"""Actual packaged Home guard: stale current-battle wave/turn refuses manual navigation.
Disposable browser-only canonical v7; no owner save, APK, capture or network."""
from pathlib import Path
import shutil, sys
R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
JS=(A/"bf_home_nav.js").read_text("utf8")
BUILD=(R/".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE=(R/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
NAME="test_bf_home_current_battle_stale_v63000.py"
assert JS.count("// v630: verify the displayed wave/turn") == 1
assert "state.wave!==shownWave" in JS and "state.round!==shownRound" in JS
assert "state.totalWaves!==shownTotalWaves" in JS
assert "Current battle wave or turn changed" in JS
assert BUILD.count("python3 "+NAME)==1 and PRE.count(NAME)==2
assert "android.permission.INTERNET" not in (A.parent/"AndroidManifest.xml").read_text()
assert len(JS.encode("utf8"))<128*1024
print("PASS v630 source/read-only guard/CI")
if "--source-only" in sys.argv:raise SystemExit(0)
from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome,"Real Chromium required"
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=chrome,args=["--no-sandbox","--disable-dev-shm-usage"])
 try:
  for width in (320,359,393,412,540):
   page=b.new_page(viewport={"width":width,"height":844})
   errors=[]
   page.on("pageerror",lambda e:errors.append(str(e)))
   try:
    page.evaluate("""() => {
      const db={};let writes=0;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{writes++;db[k]=String(v)},
        removeItem:k=>{writes++;delete db[k]},key:i=>Object.keys(db)[i]??null,
        get length(){return Object.keys(db).length}
      }});
      window.__v630writes=()=>writes;
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content((A/"index.html").read_text("utf8"),wait_until="load",timeout=90000)
    page.add_style_tag(path=str(A/"bf_home_nav.css"))
    page.add_script_tag(path=str(A/"bf_home_nav.js"))
    assert page.evaluate("P.version") == 7
    for mode in ("stale-turn","stale-wave","busy","baseline"):
     result=page.evaluate("""mode=>{
       const nav=BF_homeNav,api=BFHomeCurrentBattleB100;
       const row=QUESTS.find(q=>Number.isSafeInteger(q.missionId)&&q.battles>=2);
       if(!row)throw Error('No authentic source mission with multiple waves');
       if(nav.current!=='home')nav.go('home');
       S.mode='archive';S.over=false;S.auto=false;S.busy=false;
       S.wave=0;S.round=1;S.totalWaves=row.battles;
       QUEST.missionId=row.missionId;QUEST.dungeonId=row.dungeonId;QUEST.battles=row.battles;
       api.refresh();
       const button=document.getElementById('bf-home-current-battle');
       const msg=document.getElementById('bf-home-current-battle-status');
       if(!button||button.disabled||!msg)throw Error('Current battle preview unavailable');
       const old=button.textContent;
       if(mode==='stale-turn')S.round=2;
       if(mode==='stale-wave')S.wave=1;
       if(mode==='busy')S.busy=true;
       const snap=()=>JSON.stringify({p:P,s:S,q:QUEST,w:__v630writes(),
         storage:Array.from({length:localStorage.length},(_,i)=>{
            const k=localStorage.key(i);return [k,localStorage.getItem(k)]
         }).sort((a,b)=>a[0].localeCompare(b[0]))});
       const before=snap();
       button.focus();button.click();
       return {route:nav.current,unchanged:snap()===before,focused:document.activeElement===button,
         same:document.getElementById('bf-home-current-battle')===button,
         old,label:button.textContent,disabled:button.disabled,message:msg.textContent,
         aria:msg.getAttribute('aria-live'),role:msg.getAttribute('role'),
         overflow:document.documentElement.scrollWidth>innerWidth+1};
     }""",mode)
     assert result["same"] and not result["overflow"],(width,mode,result)
     if mode=="baseline":
      assert result["route"]=="quest",(width,result)
     else:
      assert result["route"]=="home" and result["unchanged"],(width,mode,result)
      assert (mode=="busy" or result["focused"]) and result["aria"]=="polite" and result["role"]=="status",result
      assert result["message"],(width,mode,result)
      if mode=="stale-turn":assert "TURN 2" in result["label"] and "tap again" in result["message"],result
      if mode=="stale-wave":assert "WAVE 2/" in result["label"] and "tap again" in result["message"],result
      if mode=="busy":assert result["disabled"],result
     assert not errors,(width,mode,errors[:3])
     print("PASS v630 real Home",width,mode)
   finally:page.close()
 finally:b.close()
print("PASS v630: 20 actual Home cases, no blocked-state or storage changes")
