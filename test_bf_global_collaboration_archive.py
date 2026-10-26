"""v0.25: source-backed Global collaboration archive is preview-only and save-safe."""
import json
import re
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
data=json.loads((ROOT/"source_data/bf_global_collaboration_archive.json").read_text("utf-8"))
assert data["schema"]=="bf-global-collaboration-archive-preview-v1"
assert data["provenance"]["archiveSha256"]=="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
rows=data["units"]
assert len(rows)==8
assert len({r["id"] for r in rows})==8
assert sum(r["animation"]=="SAM" for r in rows)==1
assert data["scope"].startswith("Eight vetted examples")
js=(ASSETS/"bf_home_nav.js").read_text("utf-8")
assert js.count("window.BFGlobalCollaborationArchive=Object.freeze")==1
# Ensure the checked-in archive view does not diverge from its audited data.
embedded=re.search(r"const units = Object\.freeze\((\[.*?\])\.map\(unit => Object\.freeze\(unit\)\)\)",js)
assert embedded, "Missing archival records in view"
assert json.loads(embedded.group(1))==rows
print("PASS 8 source-backed Global collaboration archive references")

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium"),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":390,"height":844})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.evaluate("""() => {
      const stored={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return stored[k]??null;},setItem(k,v){stored[k]=String(v);},
        removeItem(k){delete stored[k];},key(n){return Object.keys(stored)[n]??null;},
        get length(){return Object.keys(stored).length;}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    html=(ASSETS/"index.html").read_text("utf-8").replace(
        "<head>",'<head><base href="http://bf-assets.test/">',1)
    page.route("http://bf-assets.test/**",lambda route: route.fulfill(status=404,body=b""))
    page.set_content(html,wait_until="load",timeout=60000)
    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS/"bf_home_nav.js"))
    assert page.evaluate("BFGlobalCollaborationArchive.count")==8
    before=page.evaluate("""() => ({
        p:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7'),
        quest:QUEST.missionId,auto:S.auto
    })""")
    page.locator('.bf-navbar [data-bf-goto="units"]').click()
    page.locator('[data-bf-unit-tab="box"]').click()
    page.locator("#bf-collab-browser summary").click()
    assert page.locator(".bf-collab-card").count()==8
    assert page.locator("#bf-collab-browser").is_visible()
    assert "not yet recruitable" in page.locator("#bf-collab-browser").inner_text().lower()
    assert "not the complete" in page.locator("#bf-collab-browser").inner_text().lower()
    page.locator("#bf-collab-search").fill("810588")
    assert page.locator(".bf-collab-card").count()==1
    assert "Katsuki Bakugo" in page.locator(".bf-collab-card").inner_text()
    page.locator("#bf-collab-search").fill("")
    page.locator("#bf-collab-series").select_option("Fairy Tail")
    assert page.locator(".bf-collab-card").count()==3
    page.locator("#bf-collab-series").select_option("Hatsune Miku")
    assert page.locator(".bf-collab-card").count()==1
    assert "SAM" in page.locator(".bf-collab-card").inner_text()
    page.locator("#bf-collab-search").fill("not a real character")
    assert page.locator(".bf-collab-card").count()==0
    assert "No matching" in page.locator("#bf-collab-results").inner_text()
    after=page.evaluate("""() => ({
        p:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7'),
        quest:QUEST.missionId,auto:S.auto
    })""")
    assert before==after,(before,after)
    assert not errors,errors
    print("PASS Android portrait preview, search/filter/empty state, unchanged save v7/roster/quest/Auto Battle")
    browser.close()
