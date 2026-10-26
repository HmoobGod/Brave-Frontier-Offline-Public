"""Build #27: archive-verified battle artwork with functional existing commands.
Test uses disposable browser localStorage and a mocked automatic timer.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib, shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
PACKS=[
 ("battle","3ebd25476004d55bde589ab79c8a3ec5dfbae0132caa1e1f7c3217adf2ee88d8",
   ["battle_header_ip5.png","battle_footer_frame_ip5.png",
    "battle_target_mark.png","battle_dungeon_name_deco.png",
    "battle_crystal_icon.png","battle_heart_icon.png",
    "battle_auto_btn1.png","battle_auto_btn2.png","battle_meter_base.png"]),
 ("_dlcbundle","cfbf33c08af11258d61156fb47f4a48c0c4b263657f6e52b31ad83d274167c26",
   ["action_attack1.png","action_attack2.png","action_guard1.png",
    "action_guard2.png","action_bb1.png","action_bb2.png",
    "action_auto1.png","action_auto2.png"])
]
for pack,archive_hash,images in PACKS:
    zip_path=ROOT/"source_assets/bf1"/f"BF1_{pack}_part001.zip"
    assert hashlib.sha256(zip_path.read_bytes()).hexdigest()==archive_hash
    with ZipFile(zip_path) as z:
        for name in images:
            original=z.read("content/"+pack+"/"+name)
            output_group="battle_actions" if pack=="_dlcbundle" else pack
            staged=(ASSETS/"content"/output_group/name).read_bytes()
            assert original==staged,name
print("PASS exactly 17 archive-matched Global battle/header/action sprite files")

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium"),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":390,"height":844})
    errors=[]
    page.on("pageerror",lambda error:errors.append(str(error)))
    def route_assets(route):
        relative=route.request.url.split("bf-assets.test/",1)[-1]
        path=ASSETS/relative
        if path.is_file() and path.resolve().is_relative_to(ASSETS.resolve()) and path.suffix in (".png",".jpg",".jpeg"):
            route.fulfill(status=200,body=path.read_bytes(),
                content_type="image/jpeg" if path.suffix in (".jpg",".jpeg") else "image/png")
        else:route.fulfill(status=404,body=b"")
    page.route("http://bf-assets.test/**",route_assets)
    page.evaluate("""() => {
      const cache={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return cache[k]??null},setItem(k,v){cache[k]=String(v)},
        removeItem(k){delete cache[k]},key(i){return Object.keys(cache)[i]??null},
        get length(){return Object.keys(cache).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    source=(ASSETS/"index.html").read_text(encoding="utf-8").replace(
        "<head>",'<head><base href="http://bf-assets.test/">',1)
    page.set_content(source,wait_until="load",timeout=60000)
    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS/"bf_home_nav.js"))
    page.locator('.bf-navbar [data-bf-goto="quest"]').click()
    assert page.evaluate("BF_homeNav.current")=="quest"
    assert page.locator("#attack").is_visible()
    assert page.locator("#burst").is_visible()
    assert page.locator("#guard").is_visible()
    assert page.locator("#execute").is_visible()
    assert page.locator("#bf-original-auto-action").is_visible()
    assert page.locator("#auto").count()==1
    assert page.evaluate("BFOriginalBattleUI.autoEnabled") is False
    assert page.evaluate("BFOriginalBattleUI.autoPressed") is False

    for sel,stem in [("#attack","attack"),("#guard","guard"),("#burst","bb")]:
        result=page.locator(sel).evaluate("""(e) => ({
          url:getComputedStyle(e).backgroundImage,disabled:e.disabled
        })""")
        expected="action_"+stem+("2.png" if result["disabled"] else "1.png")
        assert expected in result["url"],(sel,result,expected)
    for sel in ("#attack","#guard","#burst","#execute"):
        assert page.locator(sel).evaluate("(e)=>typeof e.onclick")=="function",sel

    # Toggle through original checkbox, preserving original core native handler.
    # Test on/off as adjacent synchronous browser operations to avoid demo AI.
    states=page.evaluate("""() => {
      const trigger=document.querySelector('#bf-original-auto-action');
      trigger.click();
      const enabled=[document.querySelector('#auto').checked,S.auto,
        BFOriginalBattleUI.autoPressed,trigger.getAttribute('aria-pressed')];
      trigger.click();
      const disabled=[document.querySelector('#auto').checked,S.auto,
        BFOriginalBattleUI.autoPressed,trigger.getAttribute('aria-pressed')];
      return {enabled,disabled};
    }""")
    assert states["enabled"]==[True,True,True,"true"],states
    assert states["disabled"]==[False,False,False,"false"],states
    page.evaluate("""() => {document.querySelector('#auto').click();}""")
    assert page.evaluate("BFOriginalBattleUI.autoPressed") is True
    page.evaluate("""() => {document.querySelector('#auto').click();}""")
    assert page.evaluate("BFOriginalBattleUI.autoPressed") is False
    page.locator("#reset").click()
    assert page.evaluate("BFOriginalBattleUI.autoPressed") is False
    assert page.evaluate("S.auto") is False
    print("PASS original Global Auto button, native checkbox synchronized both directions and reset")

    # The source-art overlay changes styling but MUST NOT replace original
    # game command event handlers or save keys.
    assert page.locator("#attack").evaluate("(e)=>e.textContent.includes('Attack')")
    assert page.locator("#guard").evaluate("(e)=>e.textContent.includes('Guard')")
    assert page.locator("#burst").get_attribute("aria-label")=="Brave Burst"
    assert page.locator("#execute").get_attribute("id")=="execute"
    page.wait_for_function("""() => [...document.querySelectorAll(
      '.bf-original-auto-action')].every(e=>getComputedStyle(e).backgroundImage.includes('action_auto'))""")
    assert not errors,errors
    print("PASS original command handlers retained and no page errors")
    browser.close()
