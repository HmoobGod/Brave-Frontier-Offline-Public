"""v266: read-only missing unit portrait UI regression on actual offline HTML.

All scenarios run in fresh, no-network Chromium contexts with synthetic unit
portrait sources and in-memory localStorage. Never touches device or owner save.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
A = ROOT / "app/src/main/assets"
HTML = (A / "index.html").read_text("utf8")
CSS = (A / "bf_home_nav.css").read_text("utf8")
NAV = (A / "bf_home_nav.js").read_text("utf8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
BUILD = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")

# Definition plus five audited views, including the read-only Equipment card.
assert NAV.count("bfOfflineUnitPortraitV266(") == 6
assert "bfOfflineUnitPortraitV266(row.unit.portrait,row.unit.name)" in NAV
assert "image.addEventListener('error'" in NAV
assert "image.replaceWith(fallback)" in NAV
assert "fallback.setAttribute('aria-label'" in NAV
assert "fallback.textContent = 'NO ART'" in NAV
assert "unit.portrait" in NAV and "evolved.portrait" in NAV
assert "/* v266:" in CSS and ".bf-portrait-fallback" in CSS
assert "bf_global_offline_demo_v7" in HTML
assert "test_bf_unit_portrait_fallback_v26600.py --source-only" in PREFLIGHT
assert BUILD.count("python3 test_bf_unit_portrait_fallback_v26600.py") == 1
assert "android.permission.INTERNET" not in MANIFEST
assert len(NAV.encode("utf8")) < 128 * 1024 and len(CSS.encode("utf8")) < 128 * 1024
print("PASS v266 source: four portrait views, accessibility, offline guards and CI")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright

CHROME = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert CHROME, "Chromium is required for v266 full UI test"
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=CHROME,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    for width in (320, 359, 393, 540):
        for mode in ("valid", "broken", "empty"):
            context = browser.new_context(viewport={"width": width, "height": 790},
                                          reduced_motion="reduce", service_workers="block")
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("dialog", lambda d: d.dismiss())
            page.route("http://**/*", lambda route: route.abort())
            page.route("https://**/*", lambda route: route.abort())
            page.evaluate("""() => {
              const store = Object.create(null);
              window.__bf266Storage = store;
              Object.defineProperty(window,'localStorage',{configurable:true,value:{
                getItem(k){return Object.prototype.hasOwnProperty.call(store,k) ? store[k] : null;},
                setItem(k,v){store[String(k)] = String(v);},
                removeItem(k){delete store[String(k)];},
                clear(){for(const k of Object.keys(store)) delete store[k];},
                key(n){return Object.keys(store)[n] ?? null;},
                get length(){return Object.keys(store).length;}
              }});
            }""")
            page.set_content(HTML, wait_until="load", timeout=90000)
            page.add_style_tag(content=CSS)
            if mode != "valid":
                page.evaluate("""mode => {
                  const original = window.effectiveUnit;
                  const portrait = mode === 'empty' ? '' : 'data:image/png;base64,corrupted';
                  window.effectiveUnit = id => {
                    const unit = original(id);
                    return unit ? {...unit, portrait} : unit;
                  };
                  // Modify only an ephemeral synthetic archive map, never a save.
                  for (const recipe of EVO_RECIPES) {
                    const unit = UNIT_BY_ID.get(recipe.evolvedId);
                    if (unit) UNIT_BY_ID.set(recipe.evolvedId, {...unit, portrait});
                  }
                }""", mode)
            state = """() => ({
              squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster),
              evo:JSON.stringify(P.evolutions),gems:P.gems,zel:P.zel,karma:P.karma,
              save:localStorage.getItem('bf_global_offline_demo_v7'),
              storage:JSON.stringify(window.__bf266Storage)
            })"""
            before = page.evaluate(state)
            page.add_script_tag(content=NAV)
            page.wait_for_timeout(150)
            party = page.locator("#bf-scene-party .bf-portrait-fallback")
            failing = mode != "valid"
            assert party.count() == (6 if failing else 0), (width,mode,"home")
            if not failing:
                assert page.locator("#bf-scene-party img").count() == 6
            page.evaluate("BF_homeNav.go('units'); BFInnerScreens.setTab('box'); BFUnitBox.refresh()")
            page.wait_for_timeout(200)
            cards = page.locator("#bf-box-results .bf-portrait-fallback")
            detail = page.locator("#bf-box-detail > .bf-portrait-fallback")
            evo = page.locator("#bf-box-detail .bf-evo-preview > .bf-portrait-fallback")
            if failing:
                assert cards.count() == 6 and detail.count() == 1 and evo.count() == 1,(width,mode,"unit previews")
                for locator in (cards.first,detail,evo):
                    assert locator.is_visible(), (width,mode,"fallback hidden")
                    assert locator.get_attribute("role") == "img"
                    assert locator.get_attribute("aria-label").startswith("Portrait unavailable for ")
                    assert locator.evaluate("e => getComputedStyle(e).display") == "flex"
            else:
                assert cards.count() == detail.count() == evo.count() == 0
                assert page.locator("#bf-box-results .bf-box-card img").count() == 6
                assert page.locator("#bf-box-detail > img").count() == 1
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"),(width,mode,"overflow")
            assert before == page.evaluate(state),(width,mode,"player data changed")
            assert not errors,(width,mode,errors[:4])
            context.close()
            print("PASS v266",width,mode)
    browser.close()
print("PASS v266: 12 actual-page responsive valid/broken/empty portrait scenarios")
