"""v178: six original 2014 capture references, strictly NOT 2022 formations."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
D=ROOT/"source_data/historical_2014_v178"
ECONOMY=ROOT/"source_data/bf_global_original_2022_live_quest_economy_v142.json"
historical={
 300:("Scorching Trails_2014-18-10-14-41.json","8fb863b458b52614648a41c18e9ea1682c3050cd",8,25),
 330:("The Tarnished Peaks_2014-24-9-17-41.json","0980dfc03d8f02c62640be978074a59a1e158292",8,23),
 332:("Float Like a Butterfly_2014-16-9-23-49.json","6f6036273974ce618b428038afaa80c13d610e28",9,29),
 333:("The Riotous Thunderbird_2014-19-10-11-28.json","ff96f69d7e0bc010c080aabaf7fc28bdd5ecea04",9,32),
 334:("The Raged Beast of Destruction_2014-08-10-21-19.json","1b81543c5c547522e2c2acadb86d592f2c66668d",11,42),
 364:("The Fourfold Pillar_2014-22-9-16-44.json","3d6009699602a184a2bda67f014be5a989ebce85",11,41),
}
existing={int(x.stem.split("_")[1]) for x in (ROOT/"source_data/historical_2014_v200").glob("mission_*.json")}
assert len(existing)==17 and not set(historical).intersection(existing)
assert sorted(p.name for p in D.glob("*.json"))==[f"mission_{x}.json" for x in sorted(historical)]
e=json.loads(ECONOMY.read_text("utf8"))
assert e["sourceArchiveSha256"]=="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
verified={row[0]:row[3] for row in e["records"]}
assert len(verified)==106
total_waves=total_entries=0
for id,(source,blob,waves,entries) in historical.items():
 d=json.loads((D/f"mission_{id}.json").read_text("utf8"))
 assert d["id"]==id and d["name"]==source.split("_2014")[0]
 assert d["sourcePath"]=="missions_parsed/"+source
 assert d["gitBlobSha"]==blob and len(blob)==40
 assert d["sourceEra"]=="historical-2014-not-2022"
 assert d["native2022FormationVerified"] is False
 assert d["native2022EnemyAIVerified"] is False
 assert d["native2022DropRatesVerified"] is False
 assert d["mimicChestsIncluded"] is False
 assert len(d["waves"])==waves==verified[id],(id,len(d["waves"]),verified[id])
 assert [wave["wave"] for wave in d["waves"]]==list(range(1,waves+1))
 assert sum(len(w["enemies"]) for w in d["waves"])==entries
 for w in d["waves"]:
  assert w["enemies"]
  for monster in w["enemies"]:
   assert isinstance(monster["name"],str) and monster["name"]
   assert set(monster)=={"name","unitId","hp","atk","def","aiId"}
   for key in ("unitId","hp","atk","def","aiId"):
    assert type(monster[key]) is int and monster[key]>=0,(id,key,monster)
 total_waves+=waves
 total_entries+=entries
assert (total_waves,total_entries)==(56,192)
# Source-only new folder: existing prepared Android historical lab still explicitly
# reads the old 17 files and does not glob the newly researched six.
builder=(ROOT/"prepare_historical_wave_lab_v200.py").read_text("utf8")
assert "(D/'historical_2014_v200').glob('mission_*.json')" in builder
assert "historical_2014_v178" not in builder
java=(ROOT/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert "historical_2014_v178" not in java
print("PASS v178: six authentic 2014 capture sources, 56 historical waves, 192 enemy slots, exact 2022 wave-count parity ONLY; no activation")
