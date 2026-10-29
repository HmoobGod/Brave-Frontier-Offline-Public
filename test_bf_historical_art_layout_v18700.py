"""v187: exact sourced historical 2014 art geometry preflight.

No animation playback or Android art changes are permitted in this PR.
"""
from pathlib import Path
import json
import audit_bf_historical_art_layout_v18700 as audit
R=Path(__file__).resolve().parent
a=audit.scan()
assert a["schema"]=="bf-global-historical-2014-art-layout-audit-v187"
assert (a["historicalBF1UnitIds"],a["totalOriginalSourceVisualFiles"])==(67,374)
assert (a["unitAnimationAtlases"],a["unitBattleIllustrations"])==(67,67)
assert (a["sourceCGGFiles"],a["sourceCGSFiles"])==(67,173)
assert (a["sourceCGGRows"],a["sourceCGSRows"])==(1111,1371)
assert len(a["nonstandardAtlasDimensions"])==7
assert len(a["zeroDurationSequenceRows"])==1
assert a["zeroDurationSequenceRows"][0]=={
  "path":"content/unit/cgs/unit_atk_cgs_10103.csv",
  "line":11,"rawRow":[18,-10,0,0]}
assert a["allCGSFirstColumnReferencesWithinOwnCGGRowCount"] is True
for name in ("native2022EnemyWaveFormationsVerified","native2022SpritePlaybackVerified",
             "androidSpritesActivated","gameplayMutation","saveMutation"):
 assert a[name] is False
java=(R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert "v187" not in java and "historical_2014_v178" not in java
assert "bf_global_offline_demo_v7" in (R/"app/src/main/assets/index.html").read_text("utf8")
print("PASS v187 source CGG/CGS shape, original byte-preserving atlas refs and zero-duration guard, no Android activation")
