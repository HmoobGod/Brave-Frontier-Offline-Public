"""v221: browser proof for authentic original item thumbnail in v153 source UI.

Loads local fixture as a file:// page so a browser actually loads the 98x98
packaged original PNG. No real user save or Android device is touched.
"""
from pathlib import Path
import os
import shutil
import tempfile
from playwright.sync_api import sync_playwright

R = Path(__file__).resolve().parent
A = R / "app/src/main/assets"
script = A / "bf15300_legend_stone_merit_source.js"
fd, name = tempfile.mkstemp(prefix="bf22100-preview-", suffix=".html", dir=A)
os.close(fd)
fixture = Path(name)
try:
    fixture.write_text(
        '<!doctype html><html><head><meta charset="utf-8"></head>'
        '<body><details id="bf13000-source-evolutions"><summary>Evolution sources</summary></details></body></html>',
        encoding="utf8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
            args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page(viewport={"width":390, "height":844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(fixture.as_uri(), wait_until="load")
        page.evaluate("""() => {
          const saved = {'bf_global_offline_demo_v7':'preserve-owner-v7-test-fixture'};
          let writes=0;
          Object.defineProperty(window,'localStorage',{configurable:true,value:{
            getItem:k=>saved[k]??null,
            setItem:(k,v)=>{writes++;saved[k]=String(v)},
            removeItem:k=>{writes++;delete saved[k]}
          }});
          window.__writes=()=>writes;
          window.P={version:7,roster:[10011],squad:[10011],unitExp:{10011:200},materials:{}};
          window.S={mode:'idle',enemies:[],party:[]};
          window.BFGlobalOriginalStarterTypedEvolutionV13000={
            source:{sourceItemId:110100,playableExpansion:false,sourceItemAcquisitionKnown:false}
          };
        }""")
        before = page.evaluate("""() => ({
          p:JSON.stringify(P),s:JSON.stringify(S),
          save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()
        })""")
        page.add_script_tag(path=str(script))
        page.wait_for_function("""() => {
          const img=document.getElementById('bf22100-legend-stone-item-icon');
          return img && img.complete && img.naturalWidth===98 && img.naturalHeight===98;
        }""", timeout=10000)
        img = page.locator("#bf22100-legend-stone-item-icon")
        assert img.count() == 1
        assert img.get_attribute("src") == "content/item/item_thum_111000.png"
        assert "Original 2022 Legend Stone item icon" in img.get_attribute("alt")
        assert page.locator("#bf22100-legend-stone-original-icon").count() == 1
        assert page.locator("#bf15300-price").count() == 1
        assert page.evaluate("BFGlobalOriginalLegendStoneExchangeV15300.source.originalPrice") == 4000
        assert page.evaluate("BFGlobalOriginalLegendStoneExchangeV15300.source.liveAcquisition") is False
        assert page.evaluate("BFGlobalOriginalLegendStoneExchangeV15300.source.saveMutation") is False
        page.add_script_tag(path=str(script))
        assert page.locator("#bf22100-legend-stone-item-icon").count() == 1
        after = page.evaluate("""() => ({
          p:JSON.stringify(P),s:JSON.stringify(S),
          save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()
        })""")
        assert before == after, (before, after)
        assert not errors, errors
        browser.close()
finally:
    fixture.unlink(missing_ok=True)
print("PASS v221 browser: original 98x98 Legend Stone icon loads, v153 Merit source is read-only and v7 saves unchanged")
