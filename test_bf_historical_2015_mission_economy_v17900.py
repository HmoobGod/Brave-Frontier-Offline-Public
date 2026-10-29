"""v179: six source-2015 mission metadata records against source-2022 v142.

Counts/economy/prerequisites only. Neither historical source identifies 2022
enemy formations, monster AI, drops, or the native damage formula.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
fixture=json.loads((ROOT/"source_data/bf_global_2015_six_mission_metadata_v179.json").read_text("utf8"))
orig=json.loads((ROOT/"source_data/bf_global_original_2022_live_quest_economy_v142.json").read_text("utf8"))
assert fixture["schema"]=="bf-global-2015-vs-2022-six-mission-metadata-v179"
assert fixture["sourceRepository"]=="https://github.com/BluuArc/bfmt-data"
assert fixture["sourceEra"]=="historical global 2015 metadata; not 2022 waves"
assert fixture["nativeEnemyFormationsVerified"] is False
assert fixture["nativeEnemyAIVerified"] is False
assert fixture["activatesGameplay"] is False and fixture["mutatesSaves"] is False
assert orig["readOnly"] is True and orig["year"]==2022 and orig["total"]==106
assert fixture["original2022ArchiveSha256"]==orig["sourceArchiveSha256"]=="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
assert fixture["original2022MissionMasterSha256"]==orig["missionMasterSha256"]=="d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
assert orig["columns"]==["missionId","missionDungeonId","requiredMissionId","missionBattleCount","missionEnergyUse","exp","zel","karma"]
by_id={row[0]:row for row in orig["records"]}
assert len(by_id)==106
expected={
 300:("Scorching Trails","391b384e4a3da66d43b18570ba748fa84c507777",265,8,8,800,500,0),
 330:("The Tarnished Peaks","6c31e05d62f3b5c9f2fe1046cb70456f3a030034",324,8,8,1080,500,0),
 332:("Float Like a Butterfly","46d593b85129d01e11e8d1beb73c7b8f3e44d86d",331,9,8,1780,700,0),
 333:("The Riotous Thunderbird","078632c408a33db810e3fa912c707467879ebf3c",332,9,8,2010,800,0),
 334:("The Raged Beast of Destruction","f56a6fd2685c00b781b96aeaa3561d8db054fdba",333,11,10,2350,900,0),
 364:("The Fourfold Pillar","040498a843abc52f7e366eb5175baade07f4b0a3",363,11,10,2600,1000,0),
}
assert [row["id"] for row in fixture["rows"]]==sorted(expected)
for d in fixture["rows"]:
 id=d["id"]
 name,sha,*values=expected[id]
 assert d["name"]==name and d["gitBlobSha"]==sha,(id,d)
 assert d["sourcePath"]==f"gl/mission/{id}.json"
 assert d["sourceMetadataCreated"]=="2015-08-13T15:42:33.000Z"
 assert d["sourceMetadataUpdated"]=="2015-08-13T15:42:33.000Z"
 assert [d[k] for k in ("requiredMissionId","waveCount","energy","exp","zel","karma")]==values
 original=by_id[id]
 assert original[0]==id
 assert [original[i] for i in (2,3,4,5,6,7)]==values,(id,original,values)
 assert 1<=d["waveCount"]<=32
 # v178 source only: same *wave count*, never assert identical opponents.
 capture=json.loads((ROOT/f"source_data/historical_2014_v178/mission_{id}.json").read_text("utf8"))
 assert len(capture["waves"])==d["waveCount"]
 assert capture["sourceEra"]=="historical-2014-not-2022"
 assert capture["native2022FormationVerified"] is False
assert len(fixture["rows"])==6
java=(ROOT/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert "bf_global_2015_six_mission_metadata_v179" not in java
assert "historical_2014_v178" not in java
assert (ROOT/"app/src/main/assets/index.html").is_file()
print("PASS v179: 6 mission identities and six 2015-to-2022 mission counters/rewards/prerequisites parity, with no native formation or game activation")
