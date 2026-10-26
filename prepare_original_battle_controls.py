"""Extract only selected SHA256-verified original BF1 Global battle graphics.
Keep source ZIP bytes immutable. Idempotent and standard-library only.
"""
from pathlib import Path
from zipfile import ZipFile
from struct import unpack
import hashlib

ROOT=Path(__file__).resolve().parent
packs={
 "battle":("3ebd25476004d55bde589ab79c8a3ec5dfbae0132caa1e1f7c3217adf2ee88d8",{
  "battle_header_ip5.png":(640,95),
  "battle_footer_frame_ip5.png":(640,227),
  "battle_target_mark.png":(66,66),
  "battle_dungeon_name_deco.png":(640,154),
  "battle_crystal_icon.png":(32,32),
  "battle_heart_icon.png":(32,32),
  "battle_auto_btn1.png":(77,42),
  "battle_auto_btn2.png":(77,42),
  "battle_meter_base.png":(475,37)}),
 "_dlcbundle":("cfbf33c08af11258d61156fb47f4a48c0c4b263657f6e52b31ad83d274167c26",{
  "action_attack1.png":(140,62),
  "action_attack2.png":(140,62),
  "action_guard1.png":(140,62),
  "action_guard2.png":(140,62),
  "action_bb1.png":(140,62),
  "action_bb2.png":(140,62),
  "action_auto1.png":(140,62),
  "action_auto2.png":(140,62)})
}
for pack,(sha,images) in packs.items():
    original=ROOT/"source_assets/bf1"/f"BF1_{pack}_part001.zip"
    assert hashlib.sha256(original.read_bytes()).hexdigest()==sha,(pack,"archive changed")
    with ZipFile(original) as z:
        for filename,(width,height) in images.items():
            source_path=f"content/{pack}/{filename}"
            blob=z.read(source_path)
            assert blob[:8]==bytes([137,80,78,71,13,10,26,10]),source_path
            assert unpack(">II",blob[16:24])==(width,height),source_path
            # AAPT excludes directories starting with underscore. Preserve
            # original ZIP names but stage action sprites into APK-safe path.
            output_path=(f"content/battle_actions/{filename}"
                         if pack=="_dlcbundle" else source_path)
            destination=ROOT/"app/src/main/assets"/output_path
            destination.parent.mkdir(exist_ok=True,parents=True)
            if destination.is_file():
                assert destination.read_bytes()==blob,(source_path,"output mismatches archive")
            else:
                destination.write_bytes(blob)
            print("Original Global UI:",source_path,width,height)
print("PASS: 17 original battle/action UI images staged without touching game engine or save.")
