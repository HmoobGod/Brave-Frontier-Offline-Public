"""v417 Morgan map mobile and read-only completion filter, actual Chromium."""
from pathlib import Path
import shutil
import unittest
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
A=ROOT/"app/src/main/assets"
SOURCE=A/"bf080_morgan_map.js"

class MorganMobileFilterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js=SOURCE.read_text(encoding="utf-8")

    def test_mobile_pin_touch_target(self):
        self.assertIn("min-width:44px;min-height:44px",self.js)
        self.assertIn("@media(max-width:360px)",self.js)

    def test_toggle_has_accessible_state(self):
        self.assertIn("filterButton.setAttribute('aria-pressed','false')",self.js)
        self.assertIn("filterButton.setAttribute('aria-pressed',String(unclearedOnly))",self.js)
        self.assertIn("filterCount.setAttribute('aria-live','polite')",self.js)

    def test_filter_uses_real_clears_and_retains_locked_unfinished(self):
        self.assertIn("(P.questClears?.[q.missionId]||0)>0",self.js)
        self.assertIn("const show=!unclearedOnly || cleared<total",self.js)
        self.assertIn("pin.hidden=!show",self.js)
        self.assertIn("button.hidden=!show",self.js)
        self.assertIn("filterCount.textContent=visible+",self.js)

    def test_original_selection_still_uses_existing_quest_router(self):
        self.assertIn("BFQuestAreas.choose(target)",self.js)
        self.assertIn("questUnlocked(q)",self.js)

    def test_filter_source_contains_no_direct_persistence(self):
        self.assertNotIn("localStorage.setItem(",self.js)
        self.assertNotIn("saveProgress(",self.js)
        self.assertNotIn("saveGame(",self.js)

    def test_real_chromium_mobile_filter_and_zero_save_writes(self):
        # Do not mistake source-string assertions for a browser interaction test.
        with sync_playwright() as pw:
            browser=pw.chromium.launch(
                headless=True,
                executable_path=shutil.which("chromium") or
                    shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
                args=["--no-sandbox","--disable-dev-shm-usage"])
            try:
                page=browser.new_page(viewport={"width":390,"height":844})
                errors=[]
                page.on("pageerror",lambda e:errors.append(str(e)))
                page.evaluate("""() => {
                  const db={};
                  Object.defineProperty(window,'localStorage',{configurable:true,value:{
                    getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
                    removeItem:k=>{delete db[k]},
                    key:i=>Object.keys(db)[i]??null,
                    get length(){return Object.keys(db).length}
                  }});
                  window.alert=()=>{};window.confirm=()=>true;
                  HTMLMediaElement.prototype.load=()=>{};
                  HTMLMediaElement.prototype.pause=()=>{};
                  HTMLMediaElement.prototype.play=()=>Promise.resolve();
                }""")
                page.set_content((A/"index.html").read_text("utf-8"),wait_until="load",timeout=90000)
                page.add_style_tag(path=str(A/"bf_home_nav.css"))
                page.add_script_tag(path=str(A/"bf_home_nav.js"))
                page.add_script_tag(path=str(SOURCE))
                self.assertEqual(page.evaluate("P.version"),7)
                self.assertEqual(page.evaluate("QUESTS.length"),106)
                self.assertEqual(page.evaluate("BFMorganMapV080.entries.length"),7)
                page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
                self.assertIs(page.evaluate("BFMorganMapV080.chooseRegion('morgan')"),True)
                toggle=page.locator("#bf080-morgan-map .bf080-filter button")
                count=page.locator("#bf080-morgan-map .bf080-filter [role=status]")
                self.assertEqual(toggle.count(),1)
                self.assertEqual(toggle.get_attribute("aria-pressed"),"false")
                self.assertEqual(page.locator("[data-bf-morgan-pin]").count(),7)
                self.assertEqual(page.locator("[data-bf-morgan-list]").count(),7)
                self.assertIn("7 of 7",count.inner_text())
                before=page.evaluate("""() => ({
                  player:JSON.stringify(P),auto:S.auto,
                  save:localStorage.getItem('bf_global_offline_demo_v7')
                })""")
                for width in (320,370,371,390,540):
                    page.set_viewport_size({"width":width,"height":844})
                    sizes=page.evaluate("""() => {
                      const root=document.querySelector('#bf080-morgan-map');
                      const btn=root.querySelector('.bf080-filter button').getBoundingClientRect();
                      const list=root.querySelector('.bf080-map-list');
                      const pins=[...root.querySelectorAll('.bf080-pin')].map(p=>p.getBoundingClientRect());
                      return {height:btn.height,left:btn.left,right:btn.right,
                        columns:getComputedStyle(list).gridTemplateColumns.split(' ').length,
                        pins:pins.map(r=>({width:r.width,height:r.height,left:r.left,right:r.right})),
                        scroll:document.documentElement.scrollWidth,viewport:innerWidth};
                    }""")
                    self.assertGreaterEqual(sizes["height"],44,(width,sizes))
                    self.assertGreaterEqual(sizes["left"],0,(width,sizes))
                    self.assertLessEqual(sizes["right"],width+1,(width,sizes))
                    self.assertEqual(sizes["columns"],1 if width<=360 else 2,(width,sizes))
                    self.assertLessEqual(sizes["scroll"],width,(width,sizes))
                    for pin in sizes["pins"]:
                        self.assertGreaterEqual(pin["height"],44,(width,pin))
                        self.assertGreaterEqual(pin["width"],44,(width,pin))
                        self.assertGreaterEqual(pin["left"],-1,(width,pin))
                        self.assertLessEqual(pin["right"],width+1,(width,pin))
                page.set_viewport_size({"width":390,"height":844})
                toggle.click()
                self.assertIs(page.evaluate("BFMorganMapV080.unclearedOnly"),True)
                self.assertEqual(toggle.get_attribute("aria-pressed"),"true")
                self.assertIn("7 of 7",count.inner_text())
                self.assertEqual(page.evaluate("""() => ({
                  player:JSON.stringify(P),auto:S.auto,
                  save:localStorage.getItem('bf_global_offline_demo_v7')
                })"""),before)
                # Explicit test-only simulated quest clears, not owner save writes.
                page.evaluate("""() => {
                  for(const q of QUESTS.filter(q=>q.dungeonId===200))
                    P.questClears[q.missionId]=1;
                  renderQuestList();
                  BFMorganMapV080.refresh();
                }""")
                self.assertIn("6 of 7",count.inner_text())
                self.assertTrue(page.locator('[data-bf-morgan-pin="200"]').is_hidden())
                self.assertTrue(page.locator('[data-bf-morgan-list="200"]').is_hidden())
                self.assertTrue(page.locator('[data-bf-morgan-list="210"]').is_visible())
                self.assertEqual(page.evaluate("S.auto"),before["auto"])
                self.assertEqual(page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')"),before["save"])
                toggle.click()
                self.assertIs(page.evaluate("BFMorganMapV080.unclearedOnly"),False)
                self.assertIn("7 of 7",count.inner_text())
                self.assertTrue(page.locator('[data-bf-morgan-pin="200"]').is_visible())
                self.assertTrue(page.locator('[data-bf-morgan-list="200"]').is_visible())
                self.assertFalse(errors,errors)
            finally:
                browser.close()

if __name__=="__main__":
    unittest.main()
