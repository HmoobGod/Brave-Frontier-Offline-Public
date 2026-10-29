"""v189 Chromium regression: independent opt-in 67 archived BF1 battle PNGs.

No archived image becomes a 2022 combat sprite, enemy assignment or game save.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
JS=(A/"bf_global_unit_archive.js").read_text("utf8")
CSS=(A/"bf_global_unit_archive.css").read_text("utf8")
EARLY13={10022,10030,10031,10040,10041,10050,10051,10061,10071,
         10081,10082,10102,10103}
assert JS.count("bf-v189-historical-battle-art")==2
assert "historicalBattleArtIds=new Set([...historicalArtIds," in JS
assert "content/unit_historical_battle_archive/unit_ills_battle_" in JS
assert "exact 2022 Global battlefield assignment unverified" in JS
assert "localStorage.setItem(" not in JS and "saveProgress(" not in JS
assert "bf-v189-battle-preview" in CSS
files=list((A/"content/unit_historical_battle_archive").glob("unit_ills_battle_*.png"))
assert len(files)==67 and len({p.name for p in files})==67
assert all((A/f"content/unit_historical_battle_archive/unit_ills_battle_{uid}.png").is_file()
           for uid in EARLY13)
assert len(list((A/"content/unit_archive").glob("unit_ills_thum_*.png")))==127
assert len(list((A/"content/unit_historical_archive").glob("unit_ills_thum_*.png")))==54

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":390,"height":844})
    failures=[]
    page.on("pageerror",lambda e: failures.append(str(e)))
    def serve(route):
        name=route.request.url.split("bf-assets.test/",1)[-1].split("?",1)[0]
        p=(A/name).resolve()
        if p.is_file() and p.is_relative_to(A.resolve()) and p.suffix==".png":
            route.fulfill(status=200,body=p.read_bytes(),content_type="image/png")
        else:
            route.fulfill(status=404,body=b"")
    page.route("http://bf-assets.test/**",serve)
    page.evaluate("""() => {
      const db={};window.__v189Writes=[];
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v);__v189Writes.push(k)},
        removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
        get length(){return Object.keys(db).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    html=(A/"index.html").read_text("utf8").replace(
        "<head>","<head><base href='http://bf-assets.test/'>",1)
    page.set_content(html,wait_until="load",timeout=90000)
    page.add_style_tag(path=str(A/"bf_home_nav.css"))
    page.add_script_tag(path=str(A/"bf_home_nav.js"))
    page.add_style_tag(path=str(A/"bf_global_unit_archive.css"))
    page.add_script_tag(path=str(A/"bf_global_unit_archive.js"))
    page.locator('.bf-navbar [data-bf-goto="units"]').click()
    page.locator('[data-bf-unit-tab="box"]').click()
    page.locator("#bf-unit-encyclopedia summary").click()
    assert page.evaluate("BFGlobalUnitArchive.count")==2291
    assert page.evaluate("BFGlobalUnitArchive.thumbnailCount")==127
    assert page.evaluate("BFGlobalUnitArchive.historicalThumbnailCount")==54
    assert page.evaluate("BFGlobalUnitArchive.historicalBattleIllustrationCount")==67
    toggle=page.locator("#bf-v189-historical-battle-art")
    assert not toggle.is_checked()
    assert not page.locator("#bf-v188-historical-art").is_checked()
    before=page.evaluate("""()=>({P:JSON.stringify(P),S:JSON.stringify(S),
        save:localStorage.getItem('bf_global_offline_demo_v7'),writes:[...__v189Writes]})""")
    page.evaluate("BFGlobalUnitArchive.showDetail(10022)")
    assert page.locator("#bf-v189-battle-preview").count()==0
    toggle.check()
    assert page.evaluate("BFGlobalUnitArchive.historicalBattleArtOptedIn") is True
    page.evaluate("BFGlobalUnitArchive.showDetail(10022)")
    assert page.locator("#bf-v189-battle-preview img").count()==1
    page.wait_for_function("document.querySelector('#bf-v189-battle-preview img')?.naturalWidth===108")
    assert "unit_ills_battle_10022.png" in page.locator("#bf-v189-battle-preview img").get_attribute("src")
    assert "unverified" in page.locator("#bf-v189-battle-preview figcaption").inner_text()
    page.evaluate("BFGlobalUnitArchive.showDetail(10130)")
    page.wait_for_function("document.querySelector('#bf-v189-battle-preview img')?.naturalWidth===108")
    assert "unit_ills_battle_10130.png" in page.locator("#bf-v189-battle-preview img").get_attribute("src")
    page.locator("#bf-v189-battle-preview img").evaluate(
        "(img)=>{img.src='content/unit_historical_battle_archive/unit_ills_battle_0.png'}")
    page.wait_for_function(
        "document.querySelector('#bf-v189-battle-preview .bf-archive-noart')?.textContent === 'ART PENDING'")
    assert page.locator("#bf-v189-battle-preview img").count()==0
    toggle.uncheck()
    assert page.evaluate("BFGlobalUnitArchive.historicalBattleArtOptedIn") is False
    page.evaluate("BFGlobalUnitArchive.showDetail(10022)")
    assert page.locator("#bf-v189-battle-preview").count()==0
    page.add_script_tag(path=str(A/"bf_global_unit_archive.js"))
    assert page.locator("#bf-unit-encyclopedia").count()==1
    assert not toggle.is_checked()
    after=page.evaluate("""()=>({P:JSON.stringify(P),S:JSON.stringify(S),
        save:localStorage.getItem('bf_global_offline_demo_v7'),writes:[...__v189Writes]})""")
    assert before==after,(before,after)
    assert not failures,failures
    browser.close()
print("PASS v189 desktop Chromium: 67 archived images, two independent opt-ins, 108px art, missing-image fallback, v7 save isolation")
