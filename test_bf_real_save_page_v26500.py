"""v265: verify read-only save/back-up layout with the actual index.html styles.

N1 follow-up: previous v256/v264 tests used hand-written markup; here the DOM,
inline styles, labels and original handlers come from the repository index.html.
No click is sent to a destructive/backup/import control, no owner profile loads.
An isolated in-memory localStorage shim is installed before loading the real
page, matching the repository's existing navigation browser test. This checks
route-induced state/storage changes without touching real browser/user saves.
It does not claim real-device persistence coverage.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
A = ROOT / "app/src/main/assets"
HTML = (A / "index.html").read_text("utf8")
CSS = (A / "bf_home_nav.css").read_text("utf8")
NAV = (A / "bf_home_nav.js").read_text("utf8")
WORKFLOW = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")

assert "<style>" in HTML and ".transferactions button{flex:1 1 140px" in HTML
for name in ("downloadsave", "quarantineexport", "recoverycontinue",
             "wipesave", "undosave", "uploadsave"):
    assert 'id="' + name + '"' in HTML, name
assert "/* v256 UI safeguard:" in CSS
assert "/* v264 safe-save visual hierarchy:" in CSS
assert "test_bf_real_save_page_v26500.py --source-only" in PREFLIGHT
assert WORKFLOW.count("python3 test_bf_real_save_page_v26500.py") == 1
assert "android.permission.INTERNET" not in MANIFEST
assert len(CSS.encode("utf8")) < 128*1024
assert len(NAV.encode("utf8")) < 128*1024
print("PASS v265 source: real save controls, embedded flex CSS, read-only regression registered")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright

chrome = (shutil.which("chromium") or shutil.which("google-chrome") or
          shutil.which("google-chrome-stable"))
assert chrome, "Chromium is required for full v265 real-page test"
with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True, executable_path=chrome,
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    for width in (320, 359, 360, 393, 412, 540):
        # Isolated context and fresh about:blank page, never an owner account.
        context = browser.new_context(
            viewport={"width": width, "height": 790},
            reduced_motion="reduce", service_workers="block")
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("dialog", lambda dlg: dlg.dismiss())
        page.route("http://**/*", lambda route: route.abort())
        page.route("https://**/*", lambda route: route.abort())
        # Match the established test_bf_home_nav.py isolation method.
        # All reads/writes are confined to this disposable page's memory.
        page.evaluate("""() => {
          const saved = Object.create(null);
          window.__bf265Storage = saved;
          Object.defineProperty(window, 'localStorage', {
            configurable:true, value:{
              getItem(k){return Object.prototype.hasOwnProperty.call(saved,k) ? saved[k] : null;},
              setItem(k,v){saved[String(k)] = String(v);},
              removeItem(k){delete saved[String(k)];},
              clear(){for (const k of Object.keys(saved)) delete saved[k];},
              key(n){return Object.keys(saved)[n] ?? null;},
              get length(){return Object.keys(saved).length;}
            }
          });
        }""")
        page.set_content(HTML, wait_until="load", timeout=90000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=NAV)
        nav = page.locator('.bf-navbar button[data-bf-goto="menu"]')
        assert nav.count() == 1, width
        before = page.evaluate("""() => ({
           squad: JSON.stringify(P.squad),
           gems: P.gems, zel: P.zel,
           save: localStorage.getItem('bf_global_offline_demo_v7'),
           storage: JSON.stringify(window.__bf265Storage)
        })""")
        nav.click()
        assert page.evaluate("BF_homeNav.current") == "menu", width
        assert page.locator("#downloadsave").is_visible()
        assert page.locator("#wipesave").is_visible()
        assert page.locator("#quarantineexport").is_hidden()
        assert page.locator("#recoverycontinue").is_hidden()
        # Only expose the real recovery panel for visual measurement.
        # Do NOT dispatch any click or modify any save-state handler.
        page.evaluate("""() => {
          document.getElementById('savewarning').hidden = false;
          document.getElementById('recoverycontinue').hidden = false;
        }""")
        buttons = ("downloadsave", "quarantineexport", "recoverycontinue",
                   "wipesave", "undosave")
        dims = page.evaluate("""ids => Object.fromEntries(ids.map(id => {
          const e = document.getElementById(id), r = e.getBoundingClientRect();
          const s = getComputedStyle(e);
          return [id, {x:r.x,y:r.y,w:r.width,h:r.height,
            bg:s.backgroundImage,border:s.borderTopColor,
            focus:s.outlineStyle, flex:s.flexBasis, min:parseFloat(s.minHeight)}];
        }))""", list(buttons))
        for id in ("downloadsave", "quarantineexport",
                   "recoverycontinue", "wipesave"):
            d = dims[id]
            assert d["h"] >= 48, (width, id, d)
            assert d["x"] >= -1 and d["x"] + d["w"] <= width + 1, (width,id,d)
        assert dims["downloadsave"]["bg"] == dims["quarantineexport"]["bg"], width
        assert dims["downloadsave"]["bg"] != dims["wipesave"]["bg"], width
        if width <= 359:
            assert dims["quarantineexport"]["h"] >= 50, width
            cols = page.locator(".transferactions").evaluate(
                "e => getComputedStyle(e).gridTemplateColumns")
            assert len(cols.strip().split()) == 1, (width,cols)
        else:
            assert dims["wipesave"]["y"] >= (
                dims["undosave"]["y"] + dims["undosave"]["h"] + 8
            ), (width,dims["wipesave"],dims["undosave"])
            assert dims["wipesave"]["flex"] == "100%", width
        page.keyboard.press("Tab")
        page.locator("#quarantineexport").focus()
        assert page.locator("#quarantineexport").evaluate(
            "e => e.matches(':focus-visible')"),width
        assert page.locator("#quarantineexport").evaluate(
            "e => getComputedStyle(e).outlineStyle !== 'none'"),width
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth + 1"
        ),width
        # Return to the real default hidden state, preserve existing handler behavior.
        page.evaluate("""() => {
          document.getElementById('savewarning').hidden = true;
          document.getElementById('recoverycontinue').hidden = true;
        }""")
        assert page.locator("#quarantineexport").is_hidden()
        assert page.locator("#recoverycontinue").is_hidden()
        after = page.evaluate("""() => ({
           squad: JSON.stringify(P.squad),
           gems: P.gems, zel: P.zel,
           save: localStorage.getItem('bf_global_offline_demo_v7'),
           storage: JSON.stringify(window.__bf265Storage)
        })""")
        assert before == after, (width, "route/visual inspection changed demo save")
        assert not errors, (width,errors[:5])
        page.close()
        context.close()
    browser.close()
print("PASS v265 real HTML + full inline styles: six-width recovery/export/reset layout, no save writes")
