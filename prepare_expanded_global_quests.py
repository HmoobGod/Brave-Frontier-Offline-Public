"""Safely add three verified Global Cave of Flames quests before game bootstrap.

The 4.5 MB archived index.html remains unchanged in Git. The CI/Gradle
asset-staging step injects only the validated quest records *before* the
original engine creates its QUEST_BY_ID map or loads saved lastMission.
This is vital for existing saves selecting Mission 21/22/23 on relaunch.
No battle formulas, enemy assignments or save schema are patched.
"""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parent
HTML=ROOT/"app/src/main/assets/index.html"
DATA=ROOT/"source_data/bf_global_missions_21_23.json"
config=json.loads(DATA.read_text(encoding="utf-8"))
assert config["schema"]=="bf-global-mission-expansion-v1"
missions=config["missions"]
assert [q["missionId"] for q in missions]==[21,22,23]
assert [q["requires"] for q in missions]==[20,21,22]
assert [(q["battles"],q["exp"],q["zel"],q["karma"],q["energy"]) for q in missions]==[
    (5,35,450,0,3),(5,50,500,0,4),(6,80,600,0,5)]
assert all(q["dungeonId"]==20 and q["background"]=="dungeon_battle_10200.jpg"
           for q in missions)
for quest in missions:
    n=quest["missionId"]
    assert quest["missionNameKey"]==f"MST_DUNGEONS_MISSION_{n}_NAME"
    assert quest["dungeonNameKey"]=="MST_DUNGEONS_DUNGEON_20_NAME"
source=HTML.read_text(encoding="utf-8")
marker="/* BF_GLOBAL_CAVE_QUESTS_21_23_V1 */"
if source.count(marker)==1:
    # Verify that repeated local/CI builds are idempotent.
    for quest in missions:
        assert f'"missionId":{quest["missionId"]}' in source
    print("PASS Cave of Flames quest expansion already staged once")
else:
    assert marker not in source
    match=re.search(r'window\.BF_QUEST_CATALOG=(\[.*?\]);window\.BF_QUEST_BACKGROUNDS', source)
    if not match:
        raise ValueError("Core Global quest catalog anchor missing; refusing to modify HTML")
    baseline=json.loads(match.group(1))
    assert [q["missionId"] for q in baseline]==[1,2,10,11,12,20], "Unexpected baseline quest array"
    assert baseline[-1]["background"]=="dungeon_battle_10200.jpg"
    core_bootstrap="</script><script>'use strict';\n/* Stage 3: six-slot state machine."
    if source.count(core_bootstrap)!=1:
        raise ValueError("Core engine bootstrap changed; abort without modifying HTML")
    payload=json.dumps(missions,ensure_ascii=False,separators=(",",":"))
    code=(f"</script><script>{marker}"
          f"window.BF_QUEST_CATALOG.push(...{payload});"
          f"</script><script>'use strict';\n/* Stage 3: six-slot state machine.")
    modified=source.replace(core_bootstrap,code,1)
    assert modified.count(marker)==1
    assert modified.count("window.BF_QUEST_CATALOG.push(")==1
    HTML.write_text(modified,encoding="utf-8")
    print("PASS injected original Global missions 21–23 before save/quest bootstrap")
