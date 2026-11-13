"""Read-only Mission #10 2014 practice provenance adapter; NEVER 2022 combat.

Inputs are existing pinned repository research and a tiny, source-attributed donor
metadata snapshot. The donor's 56MB mission.json WAS NOT inspected: neither
enemy identity parity nor 2022 authenticity is asserted. No downloads, writes,
APK changes, progress changes, or canonical save access.
"""
from __future__ import annotations
from pathlib import Path
from copy import deepcopy
import json

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "historical": "source_data/bf_global_historical_encounters_v120.json",
    "economy": "source_data/bf_global_original_2022_live_quest_economy_v142.json",
    "english": "source_data/bf_global_quest_en_2022.json",
    "manifest": "QUEST_SOURCE_MANIFEST.json",
    "donor": "source_data/bf_mission10_donor_provenance_v410.json",
}
PINNED_2014_BLOB = "556829bc0639e417ecd4dbc99ef28c44da25c621"
PINNED_2022_MASTER = "d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
COLUMNS = ["missionId", "missionDungeonId", "requiredMissionId",
           "missionBattleCount", "missionEnergyUse", "exp", "zel", "karma"]


class ProvenanceError(ValueError):
    """Source changed, malformed, or no longer meets strict isolation gate."""


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ProvenanceError(reason)


def build_snapshot(historical: dict, economy: dict, english: dict,
                   manifest: dict, donor: dict) -> dict:
    """Return a deep, disconnected historical-practice adapter and proof ledger.

    Data never enters the 2022 campaign or any save path. This function does
    not mutate inputs, files, browser state, enemy AI or gameplay.
    """
    require("2014" in historical.get("caution", "") and
            "NOT confirmed 2022" in historical["caution"],
            "2014 historical caution missing")
    rows = [m for m in historical.get("missions", []) if type(m) is dict and m.get("id") == 10]
    require(len(rows) == 1, "missing/duplicate historical mission 10")
    row = rows[0]
    require(row.get("name") == "Start of Adventure" and
            row.get("sourcePath") ==
            "missions_parsed/Start of Adventure_2014-14-10-08-07.json" and
            row.get("gitBlobSha") == PINNED_2014_BLOB,
            "historical capture identity changed")
    require(economy.get("year") == 2022 and economy.get("readOnly") is True and
            economy.get("total") == 106 and economy.get("columns") == COLUMNS and
            economy.get("missionMasterSha256") == PINNED_2022_MASTER,
            "2022 mission metadata provenance changed")
    values = [v for v in economy.get("records", []) if type(v) is list and v[0:1] == [10]]
    require(len(values) == 1 and values[0] == [10, 10, 2, 5, 3, 20, 300, 0],
            "2022 quest 10 metadata mismatch")
    names = [m for m in english.get("missions", []) if type(m) is dict and m.get("id") == 10]
    require(len(names) == 1 and names[0].get("name") == row["name"] and
            english.get("provenance", {}).get("archive") == "BF1_sgtext_part001.zip",
            "2022 English source name mismatch")
    quests = [q for q in manifest.get("quests", []) if type(q) is dict and q.get("missionId") == 10]
    require(len(quests) == 1, "quest 10 missing/duplicated")
    q = quests[0]
    require([q.get(k) for k in ("missionId", "dungeonId", "requires", "battles",
                               "energy", "exp", "zel", "karma")] == values[0],
            "manifest and 2022 quest metadata diverged")
    require(donor.get("donorRepository") == "joppe2001/bf-private-server-data" and
            donor.get("commit") == "480a8e4f78e13b1501ca77adc5b50090a8405983" and
            donor.get("missionSourcesGitBlob") == "bb217fa9dd6bc10b709b33b3c076eba5904286e8" and
            donor.get("mission10") == {
                "method": "captured",
                "source": "Start of Adventure_2014-14-10-08-34.json",
                "replaced": "regenerated record"},
            "donor provenance snapshot changed; revalidate independently")
    waves = row.get("waves")
    require(type(waves) is list and len(waves) == values[0][3],
            "2014 vs 2022 battle count mismatch")
    practice_waves = []
    for index, wave in enumerate(waves, start=1):
        require(type(wave) is dict and type(wave.get("wave")) is int and
                wave["wave"] == index and type(wave.get("enemies")) is list and
                1 <= len(wave["enemies"]) <= 6, "invalid historical wave")
        enemies = []
        for enemy in wave["enemies"]:
            require(type(enemy) is dict and
                    type(enemy.get("name")) is str and bool(enemy["name"]) and
                    all(type(enemy.get(key)) is int for key in
                        ("unitId", "hp", "atk", "def", "aiId")) and
                    enemy["unitId"] > 0 and enemy["hp"] > 0 and
                    enemy["atk"] >= 0 and enemy["def"] >= 0 and enemy["aiId"] >= 0,
                    "invalid historical enemy")
            enemies.append({key: enemy[key] for key in
                            ("name", "unitId", "hp", "atk", "def", "aiId")})
        practice_waves.append({"wave": index, "enemies": enemies})
    require(sum(len(w["enemies"]) for w in practice_waves) == 11,
            "unexpected historical roster change")
    return deepcopy({
        "audit": {
            "schema": "bf-m10-practice-provenance-v410",
            "missionId": 10,
            "historical": {
                "era": 2014, "name": row["name"],
                "capturePath": row["sourcePath"],
                "captureGitBlob": row["gitBlobSha"],
                "waves": len(practice_waves),
                "enemySlots": 11
            },
            "donor": {
                "repository": donor["donorRepository"],
                "commit": donor["commit"],
                "captureSource": donor["mission10"]["source"],
                "sourceMethod": "captured",
                "isSameCaptureAsOurs": False,
                "fullMissionRecordInspected": False,
                "waveEnemyStatParityEstablished": False
            },
            "original2022": {
                "missionNameVerified": True,
                "battleCountVerified": True,
                "missionMasterSha256": PINNED_2022_MASTER,
                "orderedFormationsVerified": False,
                "enemyAiVerified": False,
                "dropsVerified": False
            },
            "mutatesGameOrSave": False,
            "native2022CampaignUseAuthorized": False
        },
        "practiceAdapter": {
            "scope": "historical-2014-practice-only",
            "missionId": 10,
            "historicalSourceGitBlob": PINNED_2014_BLOB,
            "notOriginal2022": True,
            "runtimeConnected": False,
            "mayStartCanonicalQuest": False,
            "mayGrantRewards": False,
            "mayWriteV7Save": False,
            "mayModifyEnemyOrPartnerAI": False,
            "waves": practice_waves
        }
    })


def load_snapshot(root: Path = ROOT) -> dict:
    def read(key: str) -> dict:
        return json.loads((root / SOURCES[key]).read_text(encoding="utf-8"))
    return build_snapshot(*(read(k) for k in
                            ("historical", "economy", "english", "manifest", "donor")))


if __name__ == "__main__":
    print(json.dumps(load_snapshot(), sort_keys=True, indent=2))
