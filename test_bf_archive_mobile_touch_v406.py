"""Standalone Chromium regression for Home -> Units original archive mobile styling.
Run: python test_bf_archive_mobile_touch_v406.py
Uses synthetic DOM only; does not claim game/device acceptance.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

CSS = Path(__file__).resolve().parent / "app/src/main/assets/bf_global_unit_archive.css"
assert CSS.is_file()
HTML = """<section class="bf-global-original-unit-archive">
<details open><summary>Original Unit Archive</summary>
<div class="bf-archive-filters">
<label>Search<input aria-label="Search" value="Vargas"></label>
<label>Element<select aria-label="Element"><option>All</option></select></label>
<label>Rarity<select aria-label="Rarity"><option>All</option></select></label>
<button id="bf-archive-reset" type="button">CLEAR FILTERS</button>
</div>
<div class="bf-archive-results"><button class="bf-archive-unit"><span class="bf-archive-noart">NO ART</span><span class="bf-archive-unit-text"><strong>Long original unit name</strong></span></button></div>
<div class="bf-archive-pagination"><button>Previous</button><span>1 / 2</span><button>Next</button></div>
<div class="bf-archive-detail"><button class="bf-archive-close">Close</button>
<table><tr><th>Original source</th><td>Long authenticated original source identifier 123456789012345678901234567890</td></tr></table>
<button class="bf-codex-evo-jump">Evolution</button></div>
</details></section>"""

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome')
                        or shutil.which('google-chrome-stable'),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    # Include the 370/371px breakpoint where archive filter columns switch.
    for width in (320, 370, 371, 390, 540):
        page = browser.new_page(viewport={"width": width, "height": 800})
        page.set_content(HTML)
        page.add_style_tag(path=str(CSS))
        result = page.evaluate("""() => {
          const root=document.querySelector('.bf-global-original-unit-archive');
          const rect=root.getBoundingClientRect();
          const controls=[...root.querySelectorAll('input,select,#bf-archive-reset,.bf-archive-pagination button,.bf-archive-close,.bf-codex-evo-jump')];
          const targets=controls.map(el=>({height:el.getBoundingClientRect().height,width:el.getBoundingClientRect().width}));
          const table=root.querySelector('table').getBoundingClientRect();
          const detail=root.querySelector('.bf-archive-detail').getBoundingClientRect();
          const reset=root.querySelector('#bf-archive-reset');
          const rr=reset.getBoundingClientRect();
          const fr=root.querySelector('.bf-archive-filters').getBoundingClientRect();
          return {left:rect.left,right:rect.right,viewport:innerWidth,
                  targets,reset:{height:rr.height,left:rr.left,right:rr.right,
                    hostLeft:fr.left,hostRight:fr.right},
                  pageWidth:document.documentElement.scrollWidth,
                  tableWidth:table.width,detailWidth:detail.width,
                  columns:getComputedStyle(root.querySelector('.bf-archive-filters')).gridTemplateColumns.split(' ').length};
        }""")
        assert result["left"] >= -0.5 and result["right"] <= width + 0.5, (width,result)
        assert all(t["height"] >= 44 for t in result["targets"]), (width,result)
        assert result["reset"]["height"] >= 44, (width,result)
        assert result["reset"]["left"] >= result["reset"]["hostLeft"]-0.5, (width,result)
        assert result["reset"]["right"] <= result["reset"]["hostRight"]+0.5, (width,result)
        assert result["pageWidth"] <= width, (width,result)
        assert result["tableWidth"] <= result["detailWidth"] + 1, (width,result)
        assert result["columns"] == (1 if width <= 370 else 2), (width,result)
        page.close()
    browser.close()
print("PASS synthetic 320/370/371/390/540 archive controls including CLEAR FILTERS, responsive filters and table bounds")
