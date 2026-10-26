"""Fail APK packaging if Android omits original Brave Frontier battle art.

The CI browser can see files that Android AAPT silently excludes. Validate the
actual built APK's compressed asset bytes BEFORE uploading it to the user.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib,sys
ROOT=Path(__file__).resolve().parent
APK=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/"app/build/outputs/apk/debug/app-debug.apk"
BATTLE=["battle_header_ip5.png","battle_footer_frame_ip5.png",
        "battle_target_mark.png","battle_dungeon_name_deco.png",
        "battle_crystal_icon.png","battle_heart_icon.png",
        "battle_auto_btn1.png","battle_auto_btn2.png","battle_meter_base.png"]
ACTIONS=["action_attack1.png","action_attack2.png","action_guard1.png",
         "action_guard2.png","action_bb1.png","action_bb2.png",
         "action_auto1.png","action_auto2.png"]
expected={"assets/content/battle/"+name for name in BATTLE}
expected.update("assets/content/battle_actions/"+name for name in ACTIONS)
with ZipFile(APK) as z, ZipFile(ROOT/"source_assets/bf1/BF1_battle_part001.zip") as battle, ZipFile(ROOT/"source_assets/bf1/BF1__dlcbundle_part001.zip") as dlc:
    actual=set(z.namelist())
    missing=sorted(expected-actual)
    assert not missing,("APK omitted original Global battle art",missing)
    for name in BATTLE:
        source=battle.read("content/battle/"+name)
        packaged=z.read("assets/content/battle/"+name)
        assert packaged==source,("Battle image altered",name)
    for name in ACTIONS:
        source=dlc.read("content/_dlcbundle/"+name)
        packaged=z.read("assets/content/battle_actions/"+name)
        assert packaged==source,("Action image altered",name)
    css=z.read("assets/bf_home_nav.css").decode("utf-8")
    for name in ACTIONS:
        assert "content/battle_actions/"+name in css,("APK CSS references wrong action art",name)
    assert "content/_dlcbundle/" not in css,("APK references unpackageable underscore directory")
    assert "assets/index.html" in actual and "assets/bf_home_nav.js" in actual
print(f"PASS {len(expected)} original BF Global sprites byte-identical in actual APK {APK.name}, all CSS references valid")
