"""v268: all four unit portrait surfaces in 4 widths x 3 modes; no owner data."""
from pathlib import Path
from urllib.parse import quote
import sys, shutil
R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
H=(A/"index.html").read_text()
C=(A/"bf_home_nav.css").read_text()
J=(A/"bf_home_nav.js").read_text()
PRE=(R/".github/workflows/android-back-ui-source-preflight.yml").read_text()
BUILD=(R/".github/workflows/build-debug-apk.yml").read_text()
assert "fallback.textContent = 'NO ART'" in J
assert "fallback.setAttribute('aria-label'" in J
assert "/* v267 narrow-screen fallback readability;" in C
assert "test_bf_portrait_readability_matrix_v26800.py --source-only" in PRE
assert BUILD.count("python3 test_bf_portrait_readability_matrix_v26800.py")==1
assert "android.permission.INTERNET" not in (R/"app/src/main/AndroidManifest.xml").read_text()
assert len(J.encode())<128*1024 and len(C.encode())<128*1024
print("PASS v268 source/read-only registration")
if "--source-only" in sys.argv[1:]:raise SystemExit(0)
from playwright.sync_api import sync_playwright
CHROME=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert CHROME, "Chromium required"
VALID="data:image/svg+xml,"+quote('<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4"><rect width="4" height="4"/></svg>',safe="")
SURFACES={
 "home":("#bf-scene-party .bf-portrait-fallback","#bf-scene-party img",6),
 "box":("#bf-box-results .bf-portrait-fallback","#bf-box-results .bf-box-card img",6),
 "detail":("#bf-box-detail>.bf-portrait-fallback","#bf-box-detail>img",1),
 "evolution":("#bf-box-detail .bf-evo-preview>.bf-portrait-fallback","#bf-box-detail .bf-evo-preview>img",1)}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=CHROME,headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
 for width in (320,359,393,540):
  for mode in ("valid","missing","corrupted"):
   ctx=browser.new_context(viewport={"width":width,"height":790},service_workers="block",reduced_motion="reduce")
   page=ctx.new_page()
   errs=[]
   page.on("pageerror",lambda e:errs.append(str(e)))
   page.on("dialog",lambda d:d.dismiss())
   page.route("http://**/*",lambda route:route.abort())
   page.route("https://**/*",lambda route:route.abort())
   page.evaluate("""() => {const d=Object.create(null);window.__v268=d;Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>Object.prototype.hasOwnProperty.call(d,k)?d[k]:null,
    setItem:(k,v)=>d[String(k)]=String(v),removeItem:k=>delete d[String(k)],
    clear:()=>Object.keys(d).forEach(k=>delete d[k]),key:n=>Object.keys(d)[n]??null,
    get length(){return Object.keys(d).length}
   }})}""")
   page.set_content(H,wait_until="load",timeout=90000)
   page.add_style_tag(content=C)
   src=VALID if mode=="valid" else ("" if mode=="missing" else "data:image/png;base64,corrupted")
   page.evaluate("""src=>{
    const old=window.effectiveUnit;window.effectiveUnit=id=>{const u=old(id);return u?{...u,portrait:src}:u};
    for(const recipe of EVO_RECIPES){const u=UNIT_BY_ID.get(recipe.evolvedId);if(u)UNIT_BY_ID.set(recipe.evolvedId,{...u,portrait:src})}
   }""",src)
   snapshot="""()=>JSON.stringify({s:P.squad,r:P.roster,e:P.evolutions,g:P.gems,z:P.zel,k:P.karma,save:localStorage.getItem('bf_global_offline_demo_v7'),storage:window.__v268})"""
   before=page.evaluate(snapshot)
   page.add_script_tag(content=J)
   def verify(surface):
    fallback,image,n=SURFACES[surface]
    if mode!="valid":
     page.wait_for_function("({q,n})=>document.querySelectorAll(q).length===n",arg={"q":fallback,"n":n})
     assert page.locator(image).count()==0,(width,mode,surface,"image present")
     for e in page.locator(fallback).all():
      assert e.is_visible() and e.inner_text()=="NO ART",(width,mode,surface)
      assert e.get_attribute("role")=="img"
      assert e.get_attribute("aria-label").startswith("Portrait unavailable for ")
      d=e.evaluate("""e=>{const t=e.firstChild,ys=[],r=e.getBoundingClientRect(),p=e.parentElement.getBoundingClientRect();for(let i=0;i<t.length;i++){const g=document.createRange();g.setStart(t,i);g.setEnd(t,i+1);ys.push(Math.round(g.getBoundingClientRect().y))}return {f:parseFloat(getComputedStyle(e).fontSize),ys,x:r.x,right:r.right,px:p.x,pr:p.right,sw:e.scrollWidth,cw:e.clientWidth,sh:e.scrollHeight,ch:e.clientHeight}}""")
      assert d["f"]>=11 and len(set(d["ys"]))==1,(width,mode,surface,d)
      assert d["sw"]<=d["cw"]+1 and d["sh"]<=d["ch"]+1,(width,mode,surface,d)
      assert d["x"]>=d["px"]-1 and d["right"]<=d["pr"]+1,(width,mode,surface,d)
    else:
     assert page.locator(fallback).count()==0,(width,mode,surface,"fallback in valid mode")
     images=page.locator(image)
     assert images.count()==n,(width,mode,surface,"images")
     for e in images.all():assert e.evaluate("e=>e.complete&&e.naturalWidth>0"),(width,mode,surface,"decode")
   verify("home")
   page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box');BFUnitBox.refresh()")
   for surface in ("box","detail","evolution"):verify(surface)
   assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,mode,"overflow")
   assert before==page.evaluate(snapshot),(width,mode,"player/save mutation")
   assert not errs,(width,mode,errs[:3])
   ctx.close();print("PASS v268",width,mode)
 browser.close()
print("PASS v268 all 12 viewport/portrait combinations across four UI surfaces")
