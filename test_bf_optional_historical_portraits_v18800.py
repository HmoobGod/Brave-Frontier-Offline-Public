"""v188 review-only Android candidate: 54 historical portraits opt-in, save-isolated.

Needs independent Claude approval before merge or owner-facing release.
"""
from pathlib import Path
import base64,hashlib,io,json,zipfile,shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
source=(R/"source_assets/bf1/BF1_Global_Archived_54_Enemy_Thumbnails_v183.zip.b64")
raw=base64.b64decode(source.read_text("ascii"),validate=True)
assert hashlib.sha256(raw).hexdigest()=="0030b4bac35055b4ca5c4791464f56e406a37e74d4c9539f46711da8289734fd"
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 assert z.testzip() is None
 record=json.loads(z.read("BF1_54_Archived_Portrait_Provenance_v183.json"))
 ids={entry["unitId"] for entry in record["records"]}
 assert len(ids)==54
 for row in record["records"]:
  uid=row["unitId"]
  path=A/f"content/unit_historical_archive/unit_ills_thum_{uid}.png"
  blob=path.read_bytes()
  assert blob==z.read(row["originalArchivePath"])
  assert len(blob)==row["bytes"] and hashlib.sha256(blob).hexdigest()==row["sha256"]
assert len(list((A/"content/unit_archive").glob("unit_ills_thum_*.png")))==127
assert len(list((A/"content/unit_historical_archive").glob("unit_ills_thum_*.png")))==54
js=(A/"bf_global_unit_archive.js").read_text("utf8")
css=(A/"bf_global_unit_archive.css").read_text("utf8")
assert "historicalArtOptedIn" in js and "historicalArtIds=new Set([" in js
assert "id=\\"bf-v188-historical-art\\"" in js
assert "bf-v188-art-optin" in css
assert js.count("content/unit_historical_archive/unit_ills_thum_")==1
assert "localStorage.setItem(" not in js and "saveProgress(" not in js

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
    executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
    args=["--no-sandbox","--disable-dev-shm-usage"])
 page=browser.new_page(viewport={"width":390,"height":844})
 errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
 def serve(route):
  path=(A/route.request.url.split("bf-assets.test/",1)[-1].split("?",1)[0]).resolve()
  if path.is_file() and path.is_relative_to(A.resolve()) and path.suffix==".png":
   route.fulfill(status=200,body=path.read_bytes(),content_type="image/png")
  else:route.fulfill(status=404,body=b"")
 page.route("http://bf-assets.test/**",serve)
 page.evaluate("""() => {
   const store={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>store[k]??null,setItem:(k,v)=>store[k]=String(v),removeItem:k=>delete store[k],
     key:i=>Object.keys(store)[i]??null,get length(){return Object.keys(store).length}}});
   window.alert=()=>{};window.confirm=()=>true;
 }""")
 html=(A/"index.html").read_text("utf8").replace("<head>","<head><base href='http://bf-assets.test/'>",1)
 page.set_content(html,wait_until="load",timeout=90000)
 page.add_style_tag(path=str(A/"bf_home_nav.css"))
 page.add_script_tag(path=str(A/"bf_home_nav.js"))
 page.add_style_tag(path=str(A/"bf_global_unit_archive.css"))
 page.add_script_tag(path=str(A/"bf_global_unit_archive.js"))
 assert page.evaluate("BFGlobalUnitArchive.count")==2291
 assert page.evaluate("BFGlobalUnitArchive.thumbnailCount")==127
 assert page.evaluate("BFGlobalUnitArchive.historicalThumbnailCount")==54
 assert page.evaluate("BFGlobalUnitArchive.find(10130).thumbnail") is False
 before=page.evaluate("""() => ({player:JSON.stringify(P),game:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator("#bf-unit-encyclopedia summary").click()
 page.locator("#bf-archive-search").fill("10130")
 assert page.locator(".bf-archive-unit").count()==1
 assert page.locator(".bf-archive-unit img").count()==0
 toggle=page.locator("#bf-v188-historical-art")
 assert toggle.is_checked() is False
 toggle.check()
 assert page.evaluate("BFGlobalUnitArchive.historicalArtOptedIn") is True
 assert page.locator(".bf-archive-unit img").count()==1
 assert "unit_historical_archive" in page.locator(".bf-archive-unit img").get_attribute("src")
 page.wait_for_function("document.querySelector('.bf-archive-unit img')?.naturalWidth>0")
 assert "exact 2022 Global client revision unverified" in page.locator(".bf-v188-art-provenance").inner_text()
 toggle.uncheck()
 assert page.locator(".bf-archive-unit img").count()==0
 assert page.evaluate("BFGlobalUnitArchive.historicalArtOptedIn") is False
 after=page.evaluate("""() => ({player:JSON.stringify(P),game:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,(before,after)
 assert not errors,errors
 browser.close()
print("PASS v188 opt-in archival encyclopedia: 54 recovered PNG images; default OFF, 127 curated unchanged, 2291 records, game/save isolation")
