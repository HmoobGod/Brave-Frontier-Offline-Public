# Mission #10 — historical practice source audit (v410)

## Scope
This branch is intentionally **research/practice only**. It never changes the
standard APK, manifests, signing, gameplay JS, player battle AI, enemy/NPC AI,
campaign rewards, canonical `bf_global_offline_demo_v7`, or original saves.

A pre-existing experimental practice arena is defined by
`app/src/main/assets/bf200_historical_wave_lab.js`; this patch adds a pure,
in-memory adapter and strict provenance regression, **not a second battle engine**.
The adapter is not automatically loaded into the APK or main campaign.

## Grounded Mission #10 observations
- Our 2014 `Start of Adventure` capture:
  `missions_parsed/Start of Adventure_2014-14-10-08-07.json`
  (source Git blob `556829bc0639e417ecd4dbc99ef28c44da25c621`).
  It has five ordered historical wave groups and eleven enemy slots.
- Our verified 2022 Global mission master has the same **wave count** of five,
  and source metadata `[10,10,2,5,3,20,300,0]` in mission/dungeon/
  prerequisite/battles/energy/EXP/Zel/Karma order.
- Our 2022 English source identifies Mission #10 as `Start of Adventure`.
- External donor `joppe2001/bf-private-server-data` commit
  `480a8e4f78e13b1501ca77adc5b50090a8405983`,
  `archive/mission_sources.json` Git blob
  `bb217fa9dd6bc10b709b33b3c076eba5904286e8`, marks #10
  `captured` from `Start of Adventure_2014-14-10-08-34.json`.
  **This is a DIFFERENT 2014 capture**; matching names/battle counts do not
  establish same wave enemies, locations, stats, or native 2022 authenticity.

## Explicit non-evidence
The donor `archive/mission.json` (56 MB) could not be read as a
bounded complete record in this audit; no donor wave data was compared. The
external generator adds inferred positions and may substitute basic enemy AI,
so a `captured` provenance label does not certify every output field.
No authenticated ordered 2022 MissionStart waves, enemy AI or item drops were
recovered. **2022 authentic formation count remains 0/106**.

## Run tests
```sh
python3 -m unittest -v test_bf_mission10_provenance_v410
python3 audit_bf_mission10_provenance_v410.py
```

The workflow `mission10-provenance-source-preflight.yml` runs the tests on
pull requests. Its success is **source research evidence only**; signed Android
CI, independent exact-head Claude review, integration gates, and owner device
approval remain separate and mandatory if a future PR wires the adapter into
gameplay.

## Next decisive blocker
Obtain a verifiably original **2022** MissionStart response for Mission #10, or
independently prove the 2022 server-side encounter group mapping. Use the
existing privacy-preserving capture inspection tools. Do not upload sensitive
account-bearing raw captures or assume a 2014 donor mission is identical.
