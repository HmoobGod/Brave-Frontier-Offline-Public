"""v259: fail-closed source audit for the offline UI acceptance inventory.

Read-only, intentionally independent of generated art and device screenshots.
No claim of original 2022 visual parity; no data or runtime modifications.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
JS = (ASSETS / "bf_home_nav.js").read_text("utf8")
CSS = (ASSETS / "bf_home_nav.css").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
DOC = (ROOT / "V259_UI_SCREEN_ACCEPTANCE_INVENTORY.md").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")

# Route names and owner-facing offline/demo content must stay present.
ROUTES = (("home", "Home"), ("units", "Units"), ("quest", "Quest"),
          ("summon", "Summon"), ("menu", "Menu"))
for route, label in ROUTES:
    assert "['" + route + "','" + label + "']" in JS, (route, label)
assert "bf-route-title" in JS and "bf-home" in JS
assert "ORIGINAL GLOBAL ART" in JS and "RECONSTRUCTION" in JS
assert "demo" in JS.lower() and "not playable" in JS.lower()

# Archived areas must not gain a clickable main-route ID by accident.
for locked in ("vortex", "arena", "raid", "randall", "exchange"):
    assert 'data-bf-goto="' + locked + '"' not in JS, locked
for disabled_label in ("Vortex Gate not implemented", "Arena not implemented",
                       "Raid Battle not implemented", "Capital Randall not implemented",
                       "Exchange Hall not implemented"):
    assert disabled_label in JS, disabled_label

# Nine surfaces each have a real cited automated guard, but the inventory
# explicitly refuses to equate CI evidence with physical-phone acceptance.
SURFACES = {
    "HOME": "test_bf_home_ui_release_readiness_v24900.py",
    "NAVIGATION": "test_bf_global_route_headers_v25200.py",
    "QUEST / BATTLE": "test_bf_quest_mission_cards_v25300.py",
    "UNITS / BOX": "test_bf_unit_box_mobile_v25400.py",
    "SQUAD EDITOR": "test_bf_squad_editor_mobile_v25700.py",
    "SUMMON HALL": "test_bf_summon_hall_mobile_v25500.py",
    "MENU / SAVES": "test_bf_save_controls_mobile_v25600.py",
    "UNAVAILABLE LOCATIONS": "test_bf_home_semantic_hierarchy_v24500.py",
    "STATIC UI ART": "test_bf_ui_asset_paths_v25800.py",
}
for surface, guard in SURFACES.items():
    assert "| " + surface + " |" in DOC, surface
    assert "`" + guard + "`" in DOC, guard
    assert (ROOT / guard).is_file(), guard
assert "PENDING for the full screen inventory" in DOC
assert "2022 archive screenshot comparison" in DOC
# Verify the ledger records the actual approved HEAD instead of requiring
# obsolete pre-merge wording. This is a documentation consistency guard,
# not an independent CI certification of Claude's review.
assert "v264 exact head" in DOC and "Claude APPROVED" in DOC

# Registered as both a short source check and an Android build source gate.
assert "test_bf_ui_screen_inventory_v25900.py --source-only" in PRE
assert WF.count("python3 test_bf_ui_screen_inventory_v25900.py") == 1
assert "android.permission.INTERNET" not in MAN
assert len(JS.encode("utf8")) < 128 * 1024
assert len(CSS.encode("utf8")) < 128 * 1024
print("PASS v259: 5 routes, 5 locked areas, 9 audited UI surfaces; "
      "owner visual acceptance remains pending")
