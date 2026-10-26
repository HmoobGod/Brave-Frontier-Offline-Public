"""Prepare selected original BF1 Global menu PNGs without changing source archives.
Run before browser tests, and automatically from Android Gradle preBuild.
Not related to save or combat logic.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import struct

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_assets" / "bf1"
DESTINATION = ROOT / "app" / "src" / "main" / "assets"
PACKS = {
    "home": (
        "2f23e6f57b03e359c53097fdd1ee7e8619bf978e5514dd91bb6c55d1f4a6ae69",
        (
            "home_win_quest.png",
            "home_win_gate.png",
            "home_win_arena.png",
            "home_win_raid_open.png",
            "home_new_btn_menu1.png",
            "home_new_btn_box1.png",
            "home_new_btn_exchange1.png",
            "home_new_btn_mission1.png",
            "home_new_btn_shortcut1.png",
            "home_character_frame_bg.png",
            "home_win_akras_smn_hall.png",
            "home_win_randall.png",
        ),
    ),
    "header": (
        "2165b5e24294b73e1f5dee282a6f190830caed0fc3d855daaffa6df572eb3a94",
        ("header_ui3.png",),
    ),
    "unit_top": (
        "b1252dfceb2f6270c4694a23b3a178fcfeaf76adf1905dfdc20122c3e40ea4e2",
        ("unit_top_edit_btn1.png", "unit_top_evo_btn1.png", "unit_top_box_btn1.png"),
    ),
    "party_edit": (
        "c176241b16d9679b0f5aa765407ebe7c14f21b6b10f30a6552f18a9d45613939",
        ("unit_table.png",),
    ),
    "mission_select": (
        "1b5654363f4b69047f3ce75ce2c2e074709ad47154457e5e13a0b3ecc3506f0a",
        ("area_name_frame.png", "party_frame_quest_btn1.png", "mission_frame_off.png",
         "mission_frame_light.png", "mission_check_unit_frame.png",
         "arrow_left.png", "arrow_right.png", "start_battle_btn1.png",
         "dungeon_name_frame_light.png", "clear.png"),
    ),
    "footer": (
        "2faada05f0f3047fbd04ea290d2a379c35f52c3c3017a5c009da1138e27fe3da",
        ("footer_btn2.png",),
    ),
}

def check_png(data: bytes, label: str) -> None:
    if len(data) < 24 or not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        raise ValueError(f"Invalid original PNG: {label}")
    width, height = struct.unpack(">II", data[16:24])
    if not 0 < width <= 4096 or not 0 < height <= 4096:
        raise ValueError(f"Invalid PNG dimensions: {label}")

def main():
    count = 0
    for group, (expected_hash, sprites) in PACKS.items():
        archive_file = SOURCE / f"BF1_{group}_part001.zip"
        if hashlib.sha256(archive_file.read_bytes()).hexdigest() != expected_hash:
            raise ValueError(f"BF1 {group} pack digest mismatch; refusing to extract")
        with ZipFile(archive_file) as archive:
            for name in sprites:
                source_name = f"content/{group}/{name}"
                data = archive.read(source_name)
                check_png(data, source_name)
                target = DESTINATION / source_name
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists() or target.read_bytes() != data:
                    target.write_bytes(data)
                count += 1
    print(f"PASS {count} verified, original Global home UI PNGs staged locally")

if __name__ == "__main__":
    main()
