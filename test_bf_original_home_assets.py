"""Validate whitelisted original Global home art and the offline hub's references."""
from pathlib import Path
import struct
import subprocess
import sys
from prepare_original_home_assets import PACKS, ROOT, DESTINATION

subprocess.check_call([sys.executable, str(ROOT / "prepare_original_home_assets.py")])
expected = {
    "header_ui3.png": (644, 206),
    "footer_btn2.png": (512, 1024),
    "home_character_frame_bg.png": (128, 350),
    "unit_top_edit_btn1.png": (260, 156),
    "unit_top_evo_btn1.png": (260, 156),
    "unit_top_box_btn1.png": (260, 156),
    "mission_frame_light.png": (622, 176),
    "mission_check_unit_frame.png": (644, 293),
    "arrow_left.png": (42, 44),
    "arrow_right.png": (25, 26),
    "start_battle_btn1.png": (258, 108),
    "dungeon_name_frame_light.png": (265, 53),
    "clear.png": (150, 32),
    "unit_table.png": (194, 104),
    "area_name_frame.png": (286, 58),
    "party_frame_quest_btn1.png": (210, 55),
    "mission_frame_off.png": (622, 176),
}
expected.update({name: (100, 80) for name in (
    "home_new_btn_menu1.png", "home_new_btn_box1.png",
    "home_new_btn_exchange1.png", "home_new_btn_mission1.png",
    "home_new_btn_shortcut1.png")})
for group, (_, sprites) in PACKS.items():
    for name in sprites:
        asset = DESTINATION / "content" / group / name
        data = asset.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", data[16:24])
        assert (width, height) == expected.get(name, (450, 316)), (asset, width, height)

js = (DESTINATION / "bf_home_nav.js").read_text(encoding="utf-8")
css = (DESTINATION / "bf_home_nav.css").read_text(encoding="utf-8")
for selector in ("home", "units", "quest", "summon", "menu"):
    assert f"['{selector}'" in js, selector
for group, (_, sprites) in PACKS.items():
    for name in sprites:
        ref = f"content/{group}/{name}"
        assert ref in js or ref in css, ref
for label in ("NOT YET AVAILABLE", "DEMO SUMMON", "CURRENT SQUAD"):
    assert label in js
assert 'MutationObserver(refreshParty)' in js
assert 'bf-scene-locked' in js and "bf-global-level" in js
print("PASS original PNG checks, original-art hub, locked locations, dynamic squad references")
